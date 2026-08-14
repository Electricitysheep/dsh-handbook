# 附录 B：官方包速查大全（@deepseek-ai/*）

> **本清单为「已知包」清单**：收录白皮书正文实测/提及过、且能在 npm registry 上核实的官方包（`@deepseek-ai/dsh-*` 与 `@deepseek-ai/cordis`），包描述来自 `npm view` 实测结果。dsh 处于 `0.1.0-rc` 快速迭代期，**包名与描述随版本更新**——若与官方仓库 `packages/AGENTS.md` 或 npm 最新描述不一致，以官方为准。未能核实的包标注「（待补全）」，不虚构包名。
>
> 包名与仓库布局对应关系：npm 包 `@deepseek-ai/dsh-xxx` ≈ 官方仓库 `packages/<group>/xxx`（如 `dsh-tool-fs` ↔ `fs/tool-fs`）。
>
> 验证方式：`npm view @deepseek-ai/<name> description`（2026-08 快照）。

**能力域取值**：`工具`（模型可调用的工具/执行管道）· `上下文`（请求上下文组装与压缩）· `会话`（会话持久化/标题/遥测）· `子代理`（委派子任务）· `MCP`（外部工具服务器接入）· `工作流`（多步编排）· `安全`（沙箱/审批/循环卫生）· `LLM`（模型接入与策略）· `UI`（浏览器界面与客户端服务）· `核心`（CLI/骨架 bundle，不属上述能力域）。

---

## 核心（Core）：CLI 与骨架 bundle

dsh 的"地基"：装一个 `@deepseek-ai/dsh` 就能跑，profile 由内置 bundle 栈堆出来（`dsh-base` → `dsh-headless` / `dsh-web-app`）。

| 包名 | 用途 | 能力域 |
|---|---|---|
| `@deepseek-ai/dsh` | dsh CLI：profile 启动、插件管理、浏览器 UI 别名（`npx -y @deepseek-ai/dsh web`） | 核心 |
| `@deepseek-ai/dsh-base` | 共享 dsh 核心 profile bundle：每个 profile 的第一层补丁，在空 profile 根上插入基础插件行 | 核心 |
| `@deepseek-ai/dsh-headless` | headless 一次性 bundle：无 Host/HTTP/浏览器层的直接 core Agent/Session 运行器 | 核心 |
| `@deepseek-ai/dsh-agent` | Agent 接口、注册表、发起者作用域与事件词汇（插件开发常直接依赖） | 核心 |
| `@deepseek-ai/dsh-web-app` | dsh 浏览器面 bundle：web patch 层（前端 dist 服务、web 面提示词、bash 运行时变量、URL 行） | 核心 |
| `@deepseek-ai/cordis` | 底层元框架：现代 JavaScript 应用的依赖注入/事件/生命周期容器（dsh 的插件底座） | 核心 |

## 工具（Tools）：模型可调用的能力

模型实际看到的工具名是**简短动词**（`read`/`write`/`grep`/`glob`/`edit`/`bash`/`web_search`/`todo_write`…），底层由本组包提供实现。

| 包名 | 用途 | 能力域 |
|---|---|---|
| `@deepseek-ai/dsh-tools` | 工具注册表与执行管道（tool registry + execution pipeline） | 工具 |
| `@deepseek-ai/dsh-fs` | 抽象文件系统能力 seam（`ctx.fs`）：词汇类型、FileSystem 服务（文本 IO + 可选版本守卫原子写）、`fs/*` 策略事件词汇 | 工具 |
| `@deepseek-ai/dsh-tool-fs` | 模型侧文件系统工具（`read`、`write`、`edit`），基于 `ctx.fs` | 工具 |
| `@deepseek-ai/dsh-tool-fs-search` | 模型侧文件发现工具（`glob`、`grep`），内置打包的 ripgrep 二进制 | 工具 |
| `@deepseek-ai/dsh-tool-str-replace-editor` | 模型侧编辑工具：查看、创建、字面量替换、行插入（工具结果含 `locations` → 产物追踪） | 工具 |
| `@deepseek-ai/dsh-shell` | 抽象 bash 执行器 seam（`ctx.shell`） | 工具 |
| `@deepseek-ai/dsh-tool-bash` | 模型侧 bash 工具，可选通用后台任务与沙箱升级支持 | 工具 |
| `@deepseek-ai/dsh-web` | 抽象 web 访问能力 seam（`ctx.web`）：search/fetch 提供者注册表、与注册顺序无关的选择、请求/结果词汇、WebError 分类 | 工具 |
| `@deepseek-ai/dsh-tool-web` | 模型侧 web 工具（`web_search`、`web_fetch`），基于 `ctx.web` | 工具 |
| `@deepseek-ai/dsh-tool-todo` | 模型侧待办工具 `todo_write`，基于事件溯源会话日志 | 工具 |
| `@deepseek-ai/dsh-tool-skill` | 模型侧技能加载工具（skill 调用入口） | 工具 |

## 上下文（Context）：上下文组装与压缩

"装什么"（系统提示 + 技能目录 + 历史 + 工具 schema）与"装不下时怎么压缩"。

| 包名 | 用途 | 能力域 |
|---|---|---|
| `@deepseek-ai/dsh-system-prompt` | 系统提示组装注册表（官方插件经 `systemPrompt.section()` 注册提示片段） | 上下文 |
| `@deepseek-ai/dsh-compaction` | 抽象压缩服务 seam（`ctx.compaction`） | 上下文 |
| `@deepseek-ai/dsh-compaction-basic` | token 计量驱动的压缩策略 + LLM 摘要后端（检测溢出 → 修剪 → 摘要） | 上下文 |
| `@deepseek-ai/dsh-skill` | Agent 技能提供者注册表（技能目录注入上下文，模型按需调用） | 上下文 |

## 会话（Session）：持久化、标题、遥测

| 包名 | 用途 | 能力域 |
|---|---|---|
| `@deepseek-ai/dsh-session` | 事件溯源会话存储（event-sourced session store） | 会话 |
| `@deepseek-ai/dsh-session-title` | 基于日志的会话标题服务与提供者注册表 | 会话 |
| `@deepseek-ai/dsh-session-telemetry` | 遥测 seam：会话事件捕获、投影、脱敏、交接给上报后端 | 会话 |

## 子代理（Subagent）：委派子任务

| 包名 | 用途 | 能力域 |
|---|---|---|
| `@deepseek-ai/dsh-subagent` | 抽象子代理 seam（`ctx.subagents`）：委派子代理的命名提供者注册表 | 子代理 |

## MCP：外部工具服务器接入

| 包名 | 用途 | 能力域 |
|---|---|---|
| `@deepseek-ai/dsh-mcp-client` | MCP 客户端桥：连接 MCP 服务器并把其工具注册到 `ctx.tools` | MCP |

## 工作流（Workflow）：多步确定性编排

| 包名 | 用途 | 能力域 |
|---|---|---|
| `@deepseek-ai/dsh-workflow` | 工作流能力 seam：`ctx.workflows` 服务、run 词汇、`workflow/*` 事件 | 工作流 |

## 安全（Safety）：沙箱、审批、循环卫生

| 包名 | 用途 | 能力域 |
|---|---|---|
| `@deepseek-ai/dsh-sandbox` | 抽象进程沙箱 seam（`ctx.sandbox`）：同世界隔离词汇 + SandboxProvider 契约 | 安全 |
| `guard/*` | 循环卫生与工具超时（白皮书 8.5 提及；npm 上具体包名待补全） | 安全 |
| `interaction/*` | 权限/审批（危险操作确认；npm 上具体包名待补全） | 安全 |

## LLM：模型接入与策略

| 包名 | 用途 | 能力域 |
|---|---|---|
| `@deepseek-ai/dsh-llm` | Provider 无关的 LLM 服务接口 | LLM |
| `@deepseek-ai/dsh-llm-deepseek` | DeepSeek chat-completions 适配器（默认 `provider=deepseek-official`，接受 off/high/max 档位） | LLM |
| `@deepseek-ai/dsh-llm-retry` | Provider 路由的 LLM 请求重试策略 | LLM |

## UI：浏览器界面与客户端服务

| 包名 | 用途 | 能力域 |
|---|---|---|
| `@deepseek-ai/dsh-client-runtime` | 客户端核心服务：SlotsService、SessionsService（作用域树 + 对象层） | UI |
| `@deepseek-ai/dsh-client-locale` | 语言包插件：Host 端 zh/en 偏好、浏览器端回退、语言快照、类型化命名空间字典 | UI |
| `ui-conversation` / `ui-tool` 等 | Web UI 各部件（白皮书 8.1 提及 `client/*`；npm 上具体包名待补全） | UI |

---

## 已知名但 npm 未发布（历史 404 包）

以下包名仅存在于白皮书踩坑记录中，**在 npm 上无法安装**（rc.1 时代依赖断裂的根源），遇到 404 属正常：

| 包名 | 说明 |
|---|---|
| `@deepseek-ai/dsh-pty` | rc.1 时代依赖，从未发布（`pnpm dlx` 404 的根因，见第 2 章 FAQ） |
| `@deepseek-ai/dsh-type-meta` | rc.1 时代依赖，从未发布（rc.1 依赖断裂的根因，见第 3 章 3.5 节） |

> 规避方式：依赖统一走 `^0.1.0-rc.6` 线。

---

**相关章节**：[第 8 章 · 工具与上下文系统](./08-tools-context.md)（60+ 能力包地图）· [第 9 章 · MCP 子代理与工作流](./09-mcp-subagent-workflow.md) · [术语表与命令速查](./appendix-glossary.md)
