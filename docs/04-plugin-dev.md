# 第 4 章：插件开发实战

> 本章目标：从零写一个**真实可用的 host 插件**——通过 `agent/request` 扩展点自动调节推理档位。这是社区项目 `dsh-tool-turbo` 的完整拆解，所有代码可运行、可测试。

## 4.1 我们要做什么

**问题**：dsh 在每次工具调用前模型都会重新思考（`reasoning_effort`）。一个 50 步工具链任务，"思考"占 90%+ 墙钟时间。

**方案**：一个 host 插件，监听 `agent/request` waterfall，根据当前步骤最近的工具调用，把简单轮次的 `reasoning_effort` 从 `high` 降到 `low`。

## 4.2 项目骨架

```
dsh-tool-turbo/
├── package.json          # host 插件声明
├── tsconfig.json
├── src/
│   ├── effort-decision.ts  # 纯函数：决策逻辑（零依赖，可单测）
│   └── index.ts            # apply(ctx)：接入扩展点
└── tests/
    └── effort-decision.spec.ts
```

`package.json` 关键字段：

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

> ⚠️ 依赖版本务必用 `^0.1.0-rc.6` 线——rc.1 线的 npm 依赖链是断的（见第 3 章常见坑）。

## 4.3 纯函数：决策逻辑（零依赖，可单测）

`src/effort-decision.ts`：

```ts
export type EffortId = 'low' | 'high' | 'max'

export interface ToolCallSample {
  name: string      // 工具名，如 'write'、'read'、'bash'
  argsSize: number  // 参数大小（字符数）
}

export interface EffortDecisionInput {
  recentCalls: readonly ToolCallSample[]
  selected: EffortId      // 用户基线档
  allowDowngrade: boolean
  allowUpgrade: boolean
}

const SIMPLE_TOOL_RE = /^(fs|bash|terminal|read|write|grep|glob|edit|ls|cat|rm|cp|touch|mkdir|pwd)/i
const HEAVY_ARGS = 800

export function decideEffort(input: EffortDecisionInput): EffortId {
  const { recentCalls, selected, allowDowngrade, allowUpgrade } = input
  if (recentCalls.length === 0) return selected   // 全新提示：保持基线

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

**为什么拆成纯函数**：决策逻辑与 dsh 运行时解耦——单元测试零依赖、毫秒级、覆盖所有分支，实机只需要验证"注入是否真的发生"。

## 4.4 插件主体：接入 `agent/request` waterfall

`src/index.ts`：

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

  // 边界适配：npm 包未 re-export 官方事件类型增强，这里放宽签名（第 3 章常见坑）
  const on = ctx.on as unknown as (
    event: string,
    handler: (payload: Record<string, unknown>, next: () => unknown) => unknown | Promise<unknown>,
  ) => void

  on('agent/request', async (payload, next) => {
    const seed = await next() as { reasoningEffort?: unknown }   // ⚠️ 必须 await！
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

**三个关键点**（都是真实踩过的坑）：

1. **`next()` 是 Promise**：`await next()` 拿到当前配置；不 await 直接 spread 会得到空对象 → provider/model 丢失 → 报错。
2. **waterfall 语义**：监听者的**返回值**传给下一个监听者/最终请求。返回 `{...seed, reasoningEffort}` 就是"保留原配置 + 覆盖推理档位"。
3. **`agent/request` 每步都触发**：`agent-loop` 的 `buildRequest` 在每一步都会走这个 waterfall——所以动态决策天然按步生效。

## 4.5 测试

**单元测试**（纯函数，零依赖）：

```ts
import { describe, expect, it } from 'vitest'
import { decideEffort } from '../src/effort-decision.ts'

it('downgrades to low for simple tool chains', () => {
  expect(decideEffort({
    recentCalls: [{ name: 'write', argsSize: 40 }],
    selected: 'high', allowDowngrade: true, allowUpgrade: true,
  })).toBe('low')
})
// ... 更多分支：全新提示保持基线 / 禁用降档 / 超大载荷升 max / 混合工具升 high
```

**实机验证**（关键——证明"注入真的发生"）：

挂载插件（第 3 章方法）→ 重启 `dsh web` → 发一个创建文件的任务 → 观察 dsh 进程日志：

```
[tool-turbo] agent/request: calls=[]                    => reasoningEffort=high
[tool-turbo] agent/request: calls=[{"name":"write",…}] => reasoningEffort=low
```

第一轮无工具调用 → 保持基线 `high`；检测到 `write` 工具 → 下一轮降为 `low`。**注入链路完整工作。**

> 完整可运行代码：https://github.com/Electricitysheep/dsh-tool-turbo

## 4.6 给新手的三条开发纪律

1. **先找扩展点**：要改的行为 90% 有官方钩子（`agent/request`、`settings`、`conversationEvents`、`slots`）——不要 fork 核心。
2. **逻辑抽纯函数**：决策/计算逻辑与 dsh 解耦 → 单测毫秒级、覆盖全分支；实机只需验证"注入发生"。
3. **实机验证不能省**：单测证明逻辑，实机日志证明接线——两个都过才算完成。

---

**下一章**：[第 5 章：实战案例](./05-cases.md)（规划中）—— Git 面板、HTML 草稿预览、提速插件。
