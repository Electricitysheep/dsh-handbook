[English](./04-plugin-dev.en.md) | [中文](./04-plugin-dev.md) · [← Back](../README.md)

# Chapter 4: Plugin Development, Hands-On

> **Goal of this chapter:** Build a **real, working host plugin** from scratch, one that automatically adjusts reasoning effort via the `agent/request` extension point. This is a full breakdown of the community project `dsh-tool-turbo`. All code is runnable and testable.

## 4.1 What We're Building

**Problem:** Before every tool call, the dsh model re-thinks from scratch (`reasoning_effort`). In a 50-step tool-chain task, "thinking" accounts for 90%+ of wall-clock time.

**Solution:** A host plugin that listens on the `agent/request` waterfall and downgrades `reasoning_effort` from `high` to `low` for simple turns, based on the most recent tool calls.

## 4.2 Project Skeleton

```
dsh-tool-turbo/
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
  "name": "dsh-tool-turbo",
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

export interface ToolTurboConfig {
  enabled: boolean
  allowDowngrade: boolean
  allowUpgrade: boolean
  baseline: 'low' | 'high' | 'max'
}

export const DEFAULT_CONFIG: ToolTurboConfig = {
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

export function apply(ctx: Context, config: ToolTurboConfig = DEFAULT_CONFIG): void {
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
    console.log(`[tool-turbo] calls=${JSON.stringify(calls)} => reasoningEffort=${effort}`)
    return { ...seed, reasoningEffort: effort }
  })
}
```

**Three critical points** (all learned the hard way):

1. **`next()` is a Promise:** `await next()` retrieves the current config. Spreading without awaiting yields an empty object, which drops the provider/model and causes errors.
2. **Waterfall semantics:** The listener's **return value** is passed to the next listener and ultimately to the request. Returning `{...seed, reasoningEffort}` means "keep the original config, but override the reasoning effort."
3. **`agent/request` fires every step:** The `agent-loop`'s `buildRequest` runs through this waterfall at every step, so dynamic decisions naturally take effect per-step.

## 4.5 Testing

**Unit tests** (pure function, zero dependencies):

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

**Live verification** (critical, proves "the injection actually happens"):

Mount the plugin (Chapter 3 method) → restart `dsh web` → send a file-creation task → watch the dsh process logs:

```
[tool-turbo] agent/request: calls=[]                    => reasoningEffort=high
[tool-turbo] agent/request: calls=[{"name":"write",…}] => reasoningEffort=low
```

First turn has no tool calls → stays at baseline `high`. After detecting the `write` tool → next turn drops to `low`. **The injection pipeline works end to end.**

> Full runnable code: https://github.com/Electricitysheep/dsh-tool-turbo

## 4.6 Three Development Disciplines for Newcomers

1. **Find the extension point first:** 90% of behaviors you want to change have official hooks (`agent/request`, `settings`, `conversationEvents`, `slots`). Don't fork the core.
2. **Extract logic into pure functions:** Decouple decision/computation logic from dsh. Unit tests run in milliseconds and cover every branch. Live verification only needs to confirm "the injection happened."
3. **Never skip live verification:** Unit tests prove the logic; live logs prove the wiring. Both must pass before you're done.

---

**Next chapter**: [Chapter 5: Real-World Cases](./05-cases.en.md) (planned) — Git panel, HTML draft preview, speed-up plugin.
