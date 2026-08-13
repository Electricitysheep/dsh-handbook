# 第 4 章：插件开发实战

> 本章目标：从零写一个**真实可用的 host 插件**——通过 `agent/request` 扩展点自动调节推理档位。这是社区项目 `dsh-tool-turbo` 的完整拆解，所有代码可运行、可测试。

## TL;DR（本章核心，30 秒版）

1. **核心问题**：dsh 每次工具调用前模型都重新思考，50 步任务 90%+ 时间在思考——降档是最快提速
2. **架构三板斧**：纯函数（决策逻辑，零依赖可单测）→ 插件主体（接入 waterfall）→ 实机验证（日志证明注入发生）
3. **`agent/request` waterfall**：每次模型请求前触发，监听者返回值传给下一个监听者，实现"保留原配置 + 覆盖某字段"
4. **`next()` 是 Promise，必须 await**：不 await 直接 spread 会得到空对象，provider/model 丢失报错
5. **开发纪律**：先找扩展点（90% 行为有官方钩子）、逻辑抽纯函数、实机验证不能省

<details><summary>本章导航</summary>
- [4.1 我们要做什么](#41-我们要做什么)
- [4.2 项目骨架](#42-项目骨架)
- [4.3 纯函数：决策逻辑（零依赖，可单测）](#43-纯函数决策逻辑零依赖可单测)
- [4.4 插件主体：接入 `agent/request` waterfall](#44-插件主体接入-agentrequest-waterfall)
- [4.5 测试](#45-测试)
- [4.6 给新手的三条开发纪律](#46-给新手的三条开发纪律)
</details>

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

## 动手练习（检验你是否真懂了）

1. **理解题**：不看原文，说出 `dsh-tool-turbo` 的三层架构（纯函数层 / 插件主体层 / 测试层）各自负责什么
   > 自查：参考本章 4.2-4.5 节的文件结构
2. **理解题**：解释为什么 `decideEffort` 要设计成纯函数而不是直接在 `apply(ctx)` 里写逻辑。如果决策逻辑依赖了 `ctx.session`，还能单测吗？
   > 自查：参考本章 4.3 节"为什么拆成纯函数"段落
3. **动手题**：给 `decideEffort` 写一个新的测试用例：当 `recentCalls` 里有 3 个简单工具 + 1 个超大参数（`argsSize = 5000`）时，应该返回什么档位？写出测试代码并运行
   > 自查：参考本章 4.5 节单元测试示例，预期结果取决于 `allowUpgrade` 配置
4. **动手题**：在 `apply(ctx)` 里，如果把 `await next()` 改成 `const seed = next()`（不 await），会发生什么？写出你的推理，然后在实机中验证
   > 自查：参考本章 4.4 节"三个关键点"第 1 条
5. **动手题**：假设你要写一个类似的插件，但改为根据"当前会话的工具调用总次数"来决定档位（超过 20 次自动降为 low），写出纯函数签名和核心逻辑
   > 自查：参考本章 4.3 节纯函数设计模式，关键是输入输出类型定义
6. **思考题**：`agent/request` waterfall 可以有多个监听者。如果 tool-turbo 和另一个插件都监听了 `agent/request`，谁先执行？返回值怎么传递？
   > 自查：参考本章 4.4 节"waterfall 语义"段落 + 第 3 章 3.4 节扩展点说明

## 常见疑问 FAQ

**Q1：`next()` 返回的 seed 里到底包含什么字段？**
seed 是当前 waterfall 链上游累积的请求配置，通常包含 `provider`、`model`、`reasoningEffort`、`tools` 等字段。你的监听者拿到 seed 后，spread 覆盖想改的字段，其余原样传递。具体字段以官方 `agent-loop` 包的类型定义为准（rc 阶段可能变动）。

**Q2：为什么 npm 包的类型签名要"放宽"？不能直接用官方类型吗？**
因为 npm 发布的 `@deepseek-ai/dsh-agent` 等包没有 re-export 内部的事件类型增强（`Events` 接口没有被 module augmentation 扩展）。直接用 `ctx.on('agent/request', ...)` 会报类型错误。解决方案是在边界用 `as unknown as` 转换，这是 rc 阶段的临时方案，正式版可能修复。

**Q3：我的插件需要在每个工具调用后都触发决策，`agent/request` 够吗？**
够。`agent/request` 在每次模型请求前触发（包括工具调用后的下一轮请求）。你只需要在监听者里读取最近的工具调用历史（从 `payload.agent.session.events` 里倒序找 `tool/call` 事件），就能做按步决策。

**Q4：纯函数测试通过了，实机验证也通过了，但用户反馈"有时候没效果"，可能是什么原因？**
几种可能：① 用户的 `settings.yaml` 里 `reasoningEffort` 是 `low`，降档无效果（已经最低了）；② 用户的任务全是简单工具，本来就快，感知不到差异；③ waterfall 里有其他插件覆盖了你的返回值。建议加日志记录每步的输入/输出档位。

**Q5：我想给插件加一个用户可配置的开关（设置页里能开关），怎么做？**
用 `settings` 服务注册一个命名空间（如 `tool-turbo`），声明配置项（enabled、baseline 等）。dsh 的设置页会自动渲染表单，用户修改后通过 `ctx.get` 读取。具体 API 参考官方 `dsh-settings` 包文档。

**Q6：`recentToolCalls` 函数里为什么要 `reverse()`？**
因为从 events 数组末尾往前遍历（取最近的 N 个），结果是倒序的（最新的在前）。reverse 后恢复时间正序（最旧的在前），和实际调用顺序一致，方便决策逻辑按"最近窗口"理解。

---

**下一章**：[第 5 章：实战案例](./05-cases.md)（规划中）—— Git 面板、HTML 草稿预览、提速插件。
