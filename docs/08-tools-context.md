# 第 8 章：工具与上下文系统

> 本章目标：理解 dsh 的"能力引擎"——模型能调用哪些工具、上下文是怎么喂给模型的、以及长对话怎么处理。**这是从"能跑"到"跑得明白"的关键一章。**

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
| **安全（safety）** | `sandbox/*`、`guard/*`、`interaction/*` | 沙箱、循环卫生、权限/审批 |
| **模型（llm）** | `llm/*`、`llm-deepseek`、`llm-retry` | 模型接入、重试 |
| **技能（skill）** | `skill/*` | 技能提供者注册表 |
| **界面（client）** | `client/*`（ui-conversation、ui-tool…） | Web UI 各部件 |

> 完整清单见官方仓库 `packages/AGENTS.md`。

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

```
上下文注入 @deepseek-ai/dsh-system-prompt   ← 官方系统提示
上下文注入 skill-catalog                    ← 技能目录
```

dsh 的上下文机制：
- **系统提示分层**：官方插件通过 `systemPrompt.section()` 注册提示片段（如 ui-deliverables 注册"产物文件引用"指导）
- **技能目录注入**：可用技能列表进入上下文，模型按需调用
- **工具 schema**：每步请求携带工具定义

## 8.4 长对话：compaction（压缩）

长对话会撑爆上下文。dsh 的 `compaction` 插件（如 `compaction-basic`）负责：
- 检测上下文溢出（`agent/request-error` 的 `CONTEXT_WINDOW_EXCEEDED`）
- 压缩历史（模型无关的修剪 + 可选摘要）
- 失败时路由到"溢出代理"（overflow agent）

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

---

**下一章**：[第 9 章：MCP、子代理与工作流](./09-mcp-subagent-workflow.md)
