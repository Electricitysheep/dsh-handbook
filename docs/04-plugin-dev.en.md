[English](./04-plugin-dev.en.md) | [中文](./04-plugin-dev.md) · [← Back](../README.md)

# Chapter 4: Plugin Development, Hands-On

> **Goal of this chapter:** Build a **real, working host plugin** from scratch, one that automatically adjusts reasoning effort via the `agent/request` extension point. This is a full breakdown of an example speed-up plugin. All code is runnable and testable.

## TL;DR (30-second version)

1. **Core problem**: dsh re-thinks before every tool call; in a 50-step task, 90%+ of wall-clock time is thinking. Lowering the reasoning effort is the fastest speedup.
2. **Three-layer verification**: pure-function tests (decision logic) → waterfall contract tests (correct wiring) → live verification (real agent loop).
3. **`agent/request` waterfall**: fires before every model request; listener return values flow to the next listener, enabling "keep original config + override one field."
4. **`next()` is a Promise; you must `await` it**: spreading without awaiting yields an empty object, dropping the provider/model and causing errors.
5. **Development discipline**: find the extension point first (90% of behaviors have official hooks), extract logic into pure functions, never skip live verification.

## 4.1 What We're Building

**Problem:** Before every tool call, the dsh model re-thinks from scratch (`reasoning_effort`). In a 50-step tool-chain task, "thinking" accounts for 90%+ of wall-clock time.

**Solution:** A host plugin that listens on the `agent/request` waterfall and downgrades `reasoning_effort` from `high` to `low` for simple turns, based on the most recent tool calls.

## 4.2 Project Skeleton

<!-- [style] 目录树代码块统一补 text 语言标签 -->
```text
dsh-speed-plugin/
├── package.json          # Host plugin declaration
├── tsconfig.json
├── src/
│   ├── effort-decision.ts  # Pure function: decision logic (zero deps, unit-testable)
│   └── index.ts            # apply(ctx): hooks into the extension point
└── tests/
    └── effort-decision.spec.ts
```

Key fields in `package.json`:

```json
{
  "name": "dsh-speed-plugin",
  "type": "module",
  "main": "src/index.ts",
  "exports": {
    ".": { "types": "./src/index.ts", "default": "./src/index.ts" }
  },
  "peerDependencies": {
    "@deepseek-ai/cordis": "^4.0.1",
    "@deepseek-ai/dsh-agent": "^0.1.0-rc.6"
  }
}
```

> ⚠️ Always use the `^0.1.0-rc.6` dependency line. The rc.1 npm dependency chain is broken (see Chapter 3 pitfalls).

## 4.3 Pure Function: Decision Logic (Zero Dependencies, Unit-Testable)

`src/effort-decision.ts`:

```ts
export type EffortId = 'low' | 'high' | 'max'

export interface ToolCallSample {
  name: string      // Tool name, e.g. 'write', 'read', 'bash'
  argsSize: number  // Argument size (character count)
}

export interface EffortDecisionInput {
  recentCalls: readonly ToolCallSample[]
  selected: EffortId      // User's baseline effort
  allowDowngrade: boolean
  allowUpgrade: boolean
}

const SIMPLE_TOOL_RE = /^(fs|bash|terminal|read|write|grep|glob|edit|ls|cat|rm|cp|touch|mkdir|pwd)/i
const HEAVY_ARGS = 800

export function decideEffort(input: EffortDecisionInput): EffortId {
  const { recentCalls, selected, allowDowngrade, allowUpgrade } = input
  if (recentCalls.length === 0) return selected   // Fresh prompt: keep baseline

  const ratio = recentCalls.filter(c =>
    SIMPLE_TOOL_RE.test(c.name) && c.argsSize < HEAVY_ARGS,
  ).length / recentCalls.length
  const heaviest = recentCalls.reduce((m, c) => Math.max(m, c.argsSize), 0)

  if (ratio >= 0.75 && allowDowngrade) return 'low'
  if (heaviest >= HEAVY_ARGS * 4 && allowUpgrade) return 'max'
  if (ratio < 0.75) return allowUpgrade ? 'high' : selected
  return selected
}
```

**Why extract a pure function:** The decision logic is decoupled from the dsh runtime. Unit tests have zero dependencies, run in milliseconds, and cover every branch. Live verification only needs to confirm "did the injection actually happen."

## 4.4 Plugin Body: Hooking into the `agent/request` Waterfall

`src/index.ts`:

```ts
import type { Context } from '@deepseek-ai/cordis'
import { decideEffort, type ToolCallSample } from './effort-decision.ts'

export interface SpeedPluginConfig {
  enabled: boolean
  allowDowngrade: boolean
  allowUpgrade: boolean
  baseline: 'low' | 'high' | 'max'
}

export const DEFAULT_CONFIG: SpeedPluginConfig = {
  enabled: true, allowDowngrade: true, allowUpgrade: false, baseline: 'high',
}

const WINDOW = 8

function recentToolCalls(agent: unknown): ToolCallSample[] {
  const events = (agent as { session?: { events?: readonly unknown[] } }).session?.events ?? []
  const out: ToolCallSample[] = []
  for (let i = events.length - 1; i >= 0 && out.length < WINDOW; i--) {
    const e = events[i] as { type?: string; data?: { name?: string; arguments?: unknown } } | undefined
    if (e?.type !== 'tool/call') continue
    out.push({
      name: e.data?.name ?? 'tool',
      argsSize: typeof e.data?.arguments === 'string' ? e.data.arguments.length : 0,
    })
  }
  return out.reverse()
}

export function apply(ctx: Context, config: SpeedPluginConfig = DEFAULT_CONFIG): void {
  if (!config.enabled) return

  // Boundary adaptation: npm package doesn't re-export official event type augmentations,
  // so we relax the signature here (see Chapter 3 pitfalls)
  const on = ctx.on as unknown as (
    event: string,
    handler: (payload: Record<string, unknown>, next: () => unknown) => unknown | Promise<unknown>,
  ) => void

  on('agent/request', async (payload, next) => {
    const seed = await next() as { reasoningEffort?: unknown }   // ⚠️ Must await!
    const calls = recentToolCalls(payload.agent)
    const effort = decideEffort({
      recentCalls: calls,
      selected: config.baseline,
      allowDowngrade: config.allowDowngrade,
      allowUpgrade: config.allowUpgrade,
    })
    console.log(`[speed-plugin] calls=${JSON.stringify(calls)} => reasoningEffort=${effort}`)
    return { ...seed, reasoningEffort: effort }
  })
}
```

**Three critical points** (all learned the hard way):

1. **`next()` is a Promise:** `await next()` retrieves the current config. Spreading without awaiting yields an empty object, which drops the provider/model and causes errors.
2. **Waterfall semantics:** The listener's **return value** is passed to the next listener and ultimately to the request. Returning `{...seed, reasoningEffort}` means "keep the original config, but override the reasoning effort."
3. **`agent/request` fires every step:** The `agent-loop`'s `buildRequest` runs through this waterfall at every step, so dynamic decisions naturally take effect per-step.

## 4.5 Testing

Stopping at “the module loads” is not enough. Test plugins in three layers: pure-function tests for business rules, waterfall contract tests for the runtime boundary, and live verification for the complete agent loop.

### Layer 1: Pure-function tests

Pure-function tests have no runtime dependency, run quickly, and cover every decision branch:

```ts
import { describe, expect, it } from 'vitest'
import { decideEffort } from '../src/effort-decision.ts'

it('downgrades to low for simple tool chains', () => {
  expect(decideEffort({
    recentCalls: [{ name: 'write', argsSize: 40 }],
    selected: 'high', allowDowngrade: true, allowUpgrade: true,
  })).toBe('low')
})
// ... more branches: fresh prompt keeps baseline / downgrade disabled /
//     oversized payload upgrades to max / mixed tools upgrade to high
```

### Layer 2: Waterfall contract tests

Passing pure-function tests does not prove that the plugin is wired correctly. A particularly dangerous mistake is omitting `await next()`, which silently drops upstream fields such as `provider`, `model`, and `tools`. A contract test captures the listener with a minimal `Context` substitute; it needs neither an API key nor a running dsh instance:

```ts
it('awaits next, preserves the seed, and only overrides reasoning effort', async () => {
  const next = async () => ({
    provider: 'deepseek-official',
    model: 'deepseek-reasoner',
    reasoningEffort: 'max',
    tools: ['read', 'write'],
  })

  const result = await runRegisteredHandler({ agent: { session: { events: [] } } }, next)

  expect(result).toEqual({
    provider: 'deepseek-official',
    model: 'deepseek-reasoner',
    reasoningEffort: 'high',
    tools: ['read', 'write'],
  })
})
```

The template's [`tests/plugin.spec.ts`](../examples/plugin-template/tests/plugin.spec.ts) also verifies that the plugin:

- registers exactly one `agent/request` listener;
- reads only the eight most recent `tool/call` events and ignores unrelated events;
- propagates downstream waterfall failures instead of swallowing them.

Run all automated checks:

```bash
cd examples/plugin-template
npm install
npm test
npm run typecheck
```

### Layer 3: Real agent-loop verification

Contract tests prove the plugin boundary, but they do not replace the real runtime. Mount the plugin (Chapter 3 method) → restart `dsh web` → send a file-creation task → watch the dsh process logs:

```text
[speed-plugin] agent/request: calls=[]                    => reasoningEffort=high
[speed-plugin] agent/request: calls=[{"name":"write",…}] => reasoningEffort=low
```

First turn has no tool calls → stays at baseline `high`. After detecting the `write` tool → next turn drops to `low`. **The injection pipeline works end to end.**

To run this layer in CI, see [Chapter 8, Section 8.7: testing plugin runtime behavior without an API key](./08-tools-context.en.md#87-testing-plugin-runtime-behavior-without-an-api-key). It distinguishes the built-in smoke/mock capabilities from the community waterfall audit plugin.

> Full runnable code: see [`examples/plugin-template/`](../examples/plugin-template/).

> **⚠️ Reasoning-effort support varies by adapter/model (real pitfall)**: if `decideEffort` returns `low` but the current provider adapter's capability table doesn't support it (e.g. the `deepseek-official` adapter only exposes `off`/`high`/`max`), the request fails with `does not support reasoning effort "low"` — **this is an adapter gap, not a plugin bug** (the official API does support `low`, see api-docs.deepseek.com/guides/thinking_mode/; FAQ Q4 covers effort tiers).
>
> **Adapter-aware mapping** — resolve the desired effort against the adapter's supported set:
> ```ts
> const SUPPORTED = ['off', 'high', 'max']  // current adapter capability table
> const effort = decideEffort({...})        // what the plugin wants
> const final = SUPPORTED.includes(effort) ? effort : (effort === 'low' ? 'high' : effort)  // fall back if unsupported
> ```

## 4.6 Three Development Disciplines for Newcomers

1. **Find the extension point first:** 90% of behaviors you want to change have official hooks (`agent/request`, `settings`, `conversationEvents`, `slots`). Don't fork the core.
2. **Extract logic into pure functions:** Decouple decision/computation logic from dsh. Unit tests run in milliseconds and cover every branch.
3. **Verify both the boundary and the runtime:** Contract tests prove `next()` forwarding and seed preservation; live logs prove that the real agent loop behaves as expected.

---

## Hands-on exercises

1. **Read the pure function**: open `src/effort-decision.ts`. Trace the logic: what does `ratio >= 0.75` mean? When does it return `'low'` vs `'max'`?
2. **Write a unit test**: add a test case for "mixed tools with heavy arguments." What effort should it return? Run it.
3. **Break it on purpose**: remove the `await` before `next()` in `src/index.ts`. Run the plugin live. What error do you see? Fix it.
4. **Add a new rule**: extend `decideEffort` to always return `'max'` when the tool name is `'bash'` and the args exceed 2000 characters. Write a test for it.
5. **Live verification**: mount the plugin (Chapter 3 method), restart `dsh web`, send a file-creation task, and watch the logs. Confirm you see `reasoningEffort=low` after the first tool call.
6. **Think**: why extract the decision logic into a pure function instead of putting it directly in the `apply(ctx)` handler? What are the testing and maintenance implications?

## FAQ

- **Q: Why not just set `reasoningEffort: low` globally?** Because complex tasks (planning, debugging) benefit from `high` or `max`. The plugin dynamically adjusts per step, giving you the best of both worlds.
- **Q: What if the plugin makes the wrong decision?** The plugin only downgrades when recent tool calls are simple (file ops, grep, etc.). If you're doing complex reasoning, the ratio drops and effort stays high. You can also disable downgrading via config.
- **Q: Can I use this plugin with other models?** The plugin hooks into dsh's `agent/request` waterfall, which is model-agnostic. It should work with any model dsh supports, though the speedup depends on the model's thinking behavior.
- **Q: Why is `next()` a Promise?** The waterfall is async: each listener may need to await the next one. Forgetting `await` breaks the chain and drops config.
- **Q: Where do I find more extension points?** Check `packages/AGENTS.md` in the official repo. The most common ones are listed in Chapter 3, Section 3.4.

---

**Next chapter**: [Chapter 5: Real-World Cases](./05-cases.en.md) (planned) — Git panel, HTML draft preview, speed-up plugin.
