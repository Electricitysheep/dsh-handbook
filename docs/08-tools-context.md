# 第 8 章：工具与上下文系统

> 本章目标：理解 dsh 的"能力引擎"——模型能调用哪些工具、上下文是怎么喂给模型的、以及长对话怎么处理。**这是从"能跑"到"跑得明白"的关键一章。**

## TL;DR（本章核心，30 秒版）

1. **60+ 官方能力包**：工具（fs/shell/web/skill/todo）、上下文（context/compaction）、会话、子代理、MCP、工作流、安全、模型、界面——一切皆插件
2. **内置工具名是简短动词**：`read`/`write`/`grep`/`glob`/`edit`/`bash`/`todo`/`skill`——写提示词直接说"读文件""搜索"即可
3. **工具返回 locations → 产物追踪**：模型改了什么文件，UI 能直接看到并可打开（对话末尾的产物 chips）
4. **上下文 = 系统提示 + 技能目录 + 对话历史 + 工具结果**：分层注入，每步请求携带工具 schema
5. **长对话自动压缩（compaction）**：检测溢出 → 修剪历史 → 可选摘要 → 失败路由到溢出代理。重要信息建议写进提示词
6. **插件行为可零成本验证**：mock llm + headless + 审计 dump（#462）——没有 API key 也能验证 waterfall 透传与工具注入
7. **工具链有三个已知坑**：code 模式 run_code/bash 的 description required 死循环（#558/#581/#689）；流式下工具名被抹空（#725 同族，见 FAQ）；run_code 内交互式工具异步结果被丢弃（#1476）

<details><summary>本章导航</summary>
- [8.1 官方能力包地图（60+ 包一览）](#81-官方能力包地图60-包一览)
- [8.2 内置工具（实测观察）](#82-内置工具实测观察)
- [8.3 上下文是怎么喂给模型的](#83-上下文是怎么喂给模型的)
  - [8.3.1 PTC 模式（Code mode）：一段代码编排多轮工具调用](#831-ptc-模式code-mode一段代码编排多轮工具调用)
- [8.4 长对话：compaction（压缩）](#84-长对话compaction压缩)
- [8.5 权限与安全模型（了解即可）](#85-权限与安全模型了解即可)
- [8.6 新手最该记住的三件事](#86-新手最该记住的三件事)
- [8.7 插件运行时验证方法论（零成本）](#87-插件运行时验证方法论零成本)
- [8.8 工具链踩坑](#88-工具链踩坑)
</details>

## 8.1 官方能力包地图（60+ 包一览）

dsh 的能力全部以包形式提供（`packages/<group>/<name>`）。新手最需要认识的：

| 能力域 | 官方包 | 作用 |
|---|---|---|
| **工具（tools）** | `fs/tool-fs`、`fs/tool-fs-search`、`fs/tool-str-replace-editor`、`shell/tool-bash`、`web`、`skill`、`todo` | 文件/终端/网页/技能/待办等可调用工具 |
| **上下文（context）** | `context/*`、`compaction/*` | 请求上下文组装、长对话压缩 |
| **会话（session）** | `session/*` | 持久化、标题、遥测 |
| **子代理（subagent）** | `subagent/*` | 委派子任务 |
| **MCP** | `mcp/*` | MCP 客户端（外部工具服务器） |
| **工作流（workflow）** | `workflow/*` | 多步工作流编排 |
| **安全（safety）** | `sandbox/*`、`guard/*`、`interaction/*`、`credentials/*` | 沙箱、循环卫生、权限/审批、凭证隔离（注：官方无独立 `safety/` 组，安全策略分散在多个包组） |
| **模型（llm）** | `llm/*`、`llm-deepseek`、`llm-retry` | 模型接入、重试 |
| **技能（skill）** | `skill/*` | 技能提供者注册表 |
| **界面（client）** | `client/*`（ui-conversation、ui-tool…） | Web UI 各部件 |

> **完整清单与包数口径**：官方仓库 `packages/README.md` 是包清单权威表（47 组）；`@deepseek-ai/dsh` CLI 的 0.1.0-rc.6 声明 **53 个 `@deepseek-ai/dsh-*` 直接依赖**（+CLI 自身 = 54），家族发布总量约 **221 个**（含 devDeps 与历史 0.0.1-rc.1 列车，官方构建 commit 提及）。白皮书/官方所称"60+"指 `packages/` 下全部子目录。**npm 包名写法**（`@deepseek-ai/dsh-*`）与**仓库路径写法**（`fs/tool-fs`）的对应关系，以及每个包的实测描述，见 [附录 B：官方包速查大全](./appendix-packages.md)。
>
> 📚 **想深入架构**：官方 `docs/subsystems/`（session / system-prompt / tools / agent / agent-loop / scope / llm-streaming / subagent）是各子系统的设计文档，比本节的"能力域分组"更系统化；自动生成的权威清单见官方 `docs/tool-catalog.md`、`docs/config-catalog.md`、`docs/module-graph.md`。

## 8.2 内置工具（实测观察）

模型实际可调用的工具名是**简短动词**（实测记录，来自 dsh web 会话与 agent/request 日志）：

| 工具名 | 作用 | 备注 |
|---|---|---|
| `read` | 读文件 | fs 能力 |
| `write` | 写文件 | fs 能力 |
| `grep` | 内容搜索 | fs-search |
| `glob` | 文件模式匹配 | fs-search |
| `edit` / `str_replace_editor` | 精准编辑 | 工具结果含 locations（用于产物追踪） |
| `bash` / `pwsh` | 执行命令 | 沙箱隔离 |
| `todo` | 待办管理 | 长任务规划 |
| `skill` | 技能调用 | skill-catalog 注入 |

**工具结果与产物追踪**（重要概念）：工具的返回里带有 `locations`（文件路径），dsh 用它们做"产物文件行"（对话结尾的产物 chips 就是从这里来的）——**模型改了什么文件，UI 能直接看到并可打开**。

## 8.3 上下文是怎么喂给模型的

一次模型请求的上下文 = 系统提示 + 技能目录 + 对话历史 + 工具结果。实测在会话日志中可见：

<!-- [style] 示意图代码块统一补 text 语言标签 -->
```text
上下文注入 @deepseek-ai/dsh-system-prompt   ← 官方系统提示
上下文注入 skill-catalog                    ← 技能目录
```

dsh 的上下文机制：
- **系统提示分层**：官方插件通过 `systemPrompt.section()` 注册提示片段（如 ui-deliverables 注册"产物文件引用"指导）
- **技能目录注入**：可用技能列表进入上下文，模型按需调用
- **工具 schema**：每步请求携带工具定义

### 8.3.1 PTC 模式（Code mode）：一段代码编排多轮工具调用

**PTC = Programmatic Tool Calling（程序化工具调用）**——官方中文站称「PTC 模式」，官方英文页面对应 **Code mode**（[#1052](https://github.com/deepseek-ai/deepseek-harness/discussions/1052) 评论区社区详解；官方站点原文："PTC 模式通过模型生成的一段代码组合多轮工具调用"）。

**与传统方式的区别**：标准模式下模型**每步发一次工具调用**（一步一往返）；PTC 模式下模型**生成一段 TypeScript 程序**，在单次程序内编排多轮工具调用（循环、分支、`Promise.all` 并行），整段程序一次往返执行完毕：

| 维度 | 标准模式 | PTC 模式（Code mode） |
|---|---|---|
| 调用形态 | 每步一次工具调用 | 一段程序编排多轮调用 |
| 模型往返 | 5 次调用 ≈ 5 次往返 | 合并为 1 次往返 |
| 中间结果 | 逐步回灌上下文 | 仅 `return`/`console.log` 回灌 |
| 典型场景 | 日常对话、单步任务 | 长链路自动化、确定性执行 |

**执行机制**：程序交给 `@deepseek-ai/dsh-code-runtime-worker-thread` 在**全新 Node worker 线程**里执行（类型剥离后可擦除 TS；空环境 + 堆/耗时/输出预算 + 硬终止）；程序内每个子工具调用仍走完整工具流水线（权限、沙箱、审计照常生效）。

**收益**：多步调用一次往返 + 中间结果不再全部塞回上下文 → **token 开销大幅下降**（#1052 评论区实测经验：PTC 模式是长任务降本手段之一）。

> 注意：PTC 模式仍有社区反馈的已知坑——`run_code`/`bash` 的 description required 死循环（见 8.8 坑 1）；且长会话中多轮工具调用的中间产物仍会留在上下文（#1052 原帖实测 70M→100M token 暴涨即发生在 PTC 模式下，见 8.4 节自动压缩需求）。

## 8.4 长对话：compaction（压缩）

长对话会撑爆上下文。dsh 的 `compaction` 插件（如 `compaction-basic`）负责：
- 检测上下文溢出（`agent/request-error` 的 `CONTEXT_WINDOW_EXCEEDED`）
- 压缩历史（模型无关的修剪 + 可选摘要）
- 失败时路由到"溢出代理"（overflow agent）

> **自动压缩是社区高频需求**（[#1052](https://github.com/deepseek-ai/deepseek-harness/discussions/1052)）：用户反馈长会话 token 暴涨后"要开新会话"很痛苦，希望**自动压缩而非手动新会话**——社区回复确认"现在内置应该是没有自动压缩"（需装 compaction 插件/手动 compact）。想低成本延续长会话的临时做法：换新会话 + 按需注入记忆（记忆分层方案见第 7 章 7.3 节与第 14 章 14.7 节生态工具）。

> 对新手：**知道"长对话会自动压缩"即可**，细节是进阶话题。生产环境注意：压缩会丢细节，重要上下文建议手动写进提示词。

## 8.5 权限与安全模型（了解即可）

- **访问模式**：UI 里可见「Workspace Write」等模式（权限预设）
- **交互审批**：`interaction/*` 提供权限/审批能力（危险操作可要求确认）
- **沙箱**：`sandbox/*` 隔离命令执行（如 pwsh 沙箱有 ACL 约束——实测中遇到过 temp 目录权限问题）
- **工具超时**：`guard/*` 提供 loop 卫生与工具超时

> 安全配置的深度话题超出本白皮书范围；核心认知：**dsh 的工具执行默认有隔离与审批层**，不是裸执行。

## 8.6 新手最该记住的三件事

1. **工具名是简短动词**（read/write/grep/glob/edit/bash）——写提示词/插件时直接说"读文件""搜索"即可
2. **工具返回 locations → 产物追踪**——模型改的文件会出现在对话产物区
3. **长对话自动压缩**——不必手动清理历史（但重要信息要写进提示词）

## 8.7 插件运行时验证方法论（零成本）

> 出处：官方讨论区 [#462](https://github.com/deepseek-ai/deepseek-harness/discussions/462)「DSH 插件运行时验证方法论：无 API Key 验证 waterfall 行为」（实证 74 事件 / 12 waterfall）。FAQ 已有一句话版本，本节展开。

**痛点**：静态检查只能证明"插件能加载"，证明不了"插件在真实 agent 循环里不破坏行为"。尤其 waterfall 事件监听器（`tools/execute`、`approval/request`、`fs/write-intent` 等）必须正确透传 `next()`，否则会**静默吞掉下游默认行为**——这类错误只在运行时暴露；而传统验证要真实 LLM API key + token 成本。

**零成本方案**（dsh 仓库自带，无需 API key）：
1. **mock llm**：脚本化返回——让第一个请求返回"调用 bash 工具"、第二个正常回复（`--sequence tool_call_success,success`），以此注入工具调用
2. **headless profile**：走真实 agent 循环，你的插件挂监听
3. **审计 dump**：`DSH_EVENT_AUDIT_DUMP` 导出事件审计快照

```sh
# 1. 启动 mock-llm（脚本化注入"调用 bash 工具"）
pnpm run mock:llm --port 8000 --api-key mock-key \
  --sequence tool_call_success,success --repeat-last \
  --tool-name bash --tool-arguments '{"command":"ls"}'

# 2. 跑 headless agent（指向 mock-llm，导出审计）
DEEPSEEK_BASE_URL=http://127.0.0.1:8000/v1 \
DEEPSEEK_API_KEY=mock-key \
DSH_EVENT_AUDIT_DUMP=/tmp/audit.json \
pnpm dsh --profile headless "run the bash tool once and report"
```

**判定通过**：审计快照 `byMode` 同时含 emit + waterfall、waterfall 链完整出现、agent 正常跑完（`mock response recovered`）。实证：74 事件 / 12 waterfall 全部捕获，完整生命周期 `session/created → … → tools/pre-execute(wf) → tools/execute(wf) → tools/post-execute(wf) → tools/result`；关键安全证明是**所有 waterfall 监听器正确透传 `next()`、零副作用**——插件既不吞默认行为，mock 注入的工具调用也完整走完链路。

**从源码跑的三点提醒**（#462 作者实测踩坑）：sparse clone 一次加全（缺 `vendor/` 会报 `Cannot find package '@deepseek-ai/cordis'`）；`build:lib:host` + `build:lib:client` + web-frontend dist 三层构建缺一不可；`mock:llm` 参数前不要多传 `--`（会被当位置参数）。

## 8.8 工具链踩坑

rc.6 时代的工具链已知坑（坑 1/2 已入 [FAQ](./faq.md)）：

**坑 1：code 模式 `run_code`/`bash` 的 description required 死循环**（[#558](https://github.com/deepseek-ai/deepseek-harness/discussions/558) [#581](https://github.com/deepseek-ai/deepseek-harness/discussions/581) [#689](https://github.com/deepseek-ai/deepseek-harness/discussions/689)）
`code` 模式下 `run_code` 与 `bash` 都把 UI 摘要字段叫 `description` 且标成 required：模型常把内层 `bash.description` 当成已传过，外层 JSON 只剩 `{"code":"..."}` → 反复报 `missing required property "description"`，看起来像"随机丢参数"。`#581` 补根因：`ToolArgsError` 不带工具名，模型无法定位错在哪个工具 → 死循环重试（附可 cherry-pick 修复）；`#689` 显示同族问题让 run_code 内所有 `tools.*` 调用都被拒绝。规避：手动补外层 description 或换标准模式。

**坑 2：流式下工具调用被抹空名**（[#725](https://github.com/deepseek-ai/deepseek-harness/discussions/725) 同族，已入 [FAQ](./faq.md)）
现象：所有工具调用报 `Error: unknown tool ""`。根因：SSE 流式解析用覆盖赋值而非累加，把工具名/ID 抹成空串（[#725](https://github.com/deepseek-ai/deepseek-harness/discussions/725) 根因 + 修复；[#161](https://github.com/deepseek-ai/deepseek-harness/discussions/161) [#615](https://github.com/deepseek-ai/deepseek-harness/discussions/615) [#694](https://github.com/deepseek-ai/deepseek-harness/discussions/694) [#741](https://github.com/deepseek-ai/deepseek-harness/discussions/741) 同族）。官方修复前只能降级/等版本；模型会反复重试，注意及时中止。

**坑 3：`run_code` 内调用交互式工具被"吞"**（[#1476](https://github.com/deepseek-ai/deepseek-harness/discussions/1476)）
`run_code` 程序内调用交互式工具（如 `ask_user_question`）时：同步执行不等异步——4ms 就返回空；异步结果约 12s 后回来时会话帧已结束，被直接丢弃。判断为 `run_code` 执行模型的问题（应支持异步工具回调或返回 pending 状态），AGENTS.md 里"别在代码里调交互式工具"的约定只能治标。

---

> **记忆方向提案（#1822 社区设计）**：社区提出"记忆体"（Memory Body）——跨会话、隔离、用户显式挂载的记忆单元，解决"记忆一锅乱炖"（会话结束日志即失效 / session-reference 仅 @提及 3 源且不搜正文）。与记忆家族（dsh-sgme 按场景注入 / dsh-memory / AgentSoul）同向互补：记忆体做底层挂载单元，上层插件可复用。

## 动手练习（检验你是否真懂了）

1. **理解题**：不看原文，列出 dsh 内置的 8 个工具名（简短动词）及各自作用
   > 自查：参考本章 8.2 节工具表格
2. **理解题**：解释"工具返回 locations → 产物追踪"是什么意思。模型改了什么文件，UI 怎么知道？
   > 自查：参考本章 8.2 节"工具结果与产物追踪"段落
3. **动手题**：在 `dsh web` 里发一个"创建一个 hello.py 文件"的任务，观察对话末尾的"产物 chips"，点击打开文件，验证产物追踪是否工作
   > 自查：参考本章 8.2 节"产物文件行"说明
4. **动手题**：在 `dsh web` 里进行一个长对话（20+ 轮），观察是否触发 compaction（看会话日志有没有"上下文溢出"或"压缩"相关日志）
   > 自查：参考本章 8.4 节"长对话自动压缩"段落
5. **思考题**：为什么"重要信息要写进提示词"而不是依赖对话历史？compaction 压缩时会丢什么？
   > 自查：参考本章 8.4 节"压缩会丢细节"警告
6. **思考题**：本章 8.5 节说"dsh 的工具执行默认有隔离与审批层"。如果你要做一个"允许模型自动执行所有 bash 命令"的插件，应该用哪个扩展点？有什么安全风险？
   > 自查：参考本章 8.5 节"交互审批" + `interaction/*` 包说明

## 常见疑问 FAQ

> 本章针对工具/上下文的高频问答见下；更多通用问题见 [FAQ 速查](./faq.md)。

**Q1：工具名是 `read`/`write` 这些简短动词，我写提示词时也要用这些名字吗？**
不需要。你写"读一下这个文件""搜索包含 foo 的行"，模型会自动映射到对应工具。简短动词名是插件内部实现细节，提示词用自然语言即可。

**Q2：`edit` 和 `str_replace_editor` 是同一个工具吗？**
是。`str_replace_editor` 是内部包名，模型调用时可能显示为 `edit`。功能一样：精准替换文件中的某段文本。工具结果里的 `locations` 用于产物追踪。

**Q3：compaction 压缩后，模型还能记得之前对话的内容吗？**
记得"摘要"，但会丢细节。compaction 会修剪历史 + 可选生成摘要，关键信息保留，细节丢失。所以重要上下文（如项目约束、特殊要求）建议写进系统提示或提示词，不要只依赖对话历史。

**Q4：`context/*` 和 `compaction/*` 有什么区别？**
`context/*` 负责"组装每次请求的上下文"（系统提示 + 技能目录 + 对话历史 + 工具 schema）。`compaction/*` 负责"长对话压缩"（检测溢出 → 修剪 → 摘要）。一个是"装什么"，一个是"装不下时怎么压缩"。

**Q5：安全模型里"沙箱"和"交互审批"有什么区别？**
沙箱（`sandbox/*`）隔离命令执行环境（如 pwsh 沙箱有 ACL 约束，限制文件访问）。交互审批（`interaction/*`）是"危险操作前要求用户确认"（如删除文件、执行未知命令）。一个管"在哪执行"，一个管"能不能执行"。

**Q6：我想给 dsh 加一个新工具（比如"查数据库"），应该怎么做？**
两种方式：① 写一个 host 插件，用 `ctx.provide` 注册工具服务（参考第 3 章 3.4 节扩展点）；② 用 MCP 接入外部工具服务器（第 9 章 9.1 节）。前者适合深度集成，后者适合快速接入现有系统。

---

**下一章**：[第 9 章：MCP、子代理与工作流](./09-mcp-subagent-workflow.md)
