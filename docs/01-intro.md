# 第 1 章：认识 DeepSeek Harness

> 本章目标：回答三个问题——**它是什么？它和 Claude Code 有什么区别？我为什么要用它？**

## 1.1 一句话定义

**DeepSeek Harness（`dsh`）是 DeepSeek 官方开源的 Agent 运行时**：一个"一切皆插件"（everything is a plugin）的框架，用于构建、运行和扩展 AI Agent。它基于 Cordis（一个为可组合系统设计的插件容器）构建。

官方仓库的一句话定位：

> "DeepSeek Harness (`dsh`) is an open-source agent harness developed by DeepSeek AI. It uses an architecture where **everything is a plugin**."

2026-08-13 开源，MIT 协议，TypeScript 编写。版本线 `0.1.0-rc.x`（当前 rc.6，迭代极快，官方明示"将有破坏性变更"）。

## 1.2 它解决什么问题

| 痛点 | dsh 的答案 |
|---|---|
| 想要一个能**自由定制**的 Agent，而不是被闭源工具锁死 | 官方开源 + MIT + 插件体系，任何行为都可替换 |
| 想要"模型 + 工具 + 界面"**解耦**，各层独立演进 | 分层：llm（模型）/ tools（工具）/ client（界面）/ session（会话）各自是插件 |
| 想要在**服务器/CI/终端**跑 Agent，而不只是 GUI | 官方提供 `web`（Web UI）与 `headless`（一次性 CLI）两个 profile |
| 想给社区贡献能力，而不是只能提 issue | CONTRIBUTING 明确鼓励做 `dsh-plugin` 生态项目 |

一句话：**dsh 是"你自己 Agent 的乐高底座"**——官方搭好运行时，能力由插件堆出来。

## 1.3 核心架构：一切皆插件

```
┌─────────────────────────────────────────────────┐
│                  你的 profile                    │
│  (如 dsh web / dsh headless / 你的自定义 profile)  │
├─────────────────────────────────────────────────┤
│  profile = bundle 栈 + 你的 patch 层              │
│  bundle 例子: @deepseek-ai/dsh-base (核心)        │
│              @deepseek-ai/dsh-web-app (Web UI)   │
│              dsh-better-sidebar (社区插件)        │
├─────────────────────────────────────────────────┤
│  Cordis 插件容器：每个能力 = 一个插件              │
│  llm / tools / session / client / settings ...   │
└─────────────────────────────────────────────────┘
```

关键概念（第 3 章展开）：

- **profile**：一个可启动的配置栈（`$DSH_HOME/profiles/<name>/`），包含 `package.json`（插件依赖 + 清单）+ `cordis.patch.yml`（你的覆盖层）。
- **bundle**：一组插件的集合（官方预置 `dsh-base`、`dsh-web-app`、`dsh-headless`）。
- **插件（plugin）**：cordis 插件，分 **host 半**（Node 侧：工具、服务、事件）与 **client 半**（浏览器侧：UI、交互）——一个 npm 包可以同时携带两半。
- **extension point（扩展点）**：官方为"不改核心、只加插件"设计的钩子——如 `agent/request` waterfall、`conversationEvents`、`settings` 命名空间。**新手最容易忽略的是：改行为优先找扩展点，而不是 fork 核心**。

## 1.4 与同类工具的差异

| 维度 | dsh | Claude Code / Codex | OpenCode | 自建框架（LangGraph 等） |
|---|---|---|---|---|
| 定位 | Agent **运行时 + 生态** | 闭源/半开源的 Agent 产品 | 开源 Agent 客户端 | 开发者自己拼 |
| 可定制性 | **一切皆插件**，官方鼓励改 | 有限（配置/钩子） | 中等（配置为主） | 完全自由但费时 |
| 官方开源 | ✅ MIT | ❌（闭源或受限） | ✅ | — |
| 开箱即用 | web + headless + 插件市场雏形 | ✅ 成熟 | ✅ | 需自建 |
| 生态现状 | **零日起步**（2026-08-13 开源） | 成熟 | 成熟 | — |
| 适合谁 | 想深度定制 + 玩生态的开发者 | 开箱即用 | 熟悉 OpenCode 的用户 | 需要完全控制的团队 |

**现实定位**：dsh 目前在"开箱即用"上不如 Claude Code 成熟（迭代快、有破坏性变更、中文教程此前为零），但在**"可控性 × 开源 × 官方背书"**这个组合上是独特的——这是它值得早入场的核心原因，也是生态项目的机会窗口。

## 1.5 生态现状（2026-08-13 快照）

- **官方**：仓库 12k+ commits、`dsh-plugin` topic 已建立、Discord 社区、CONTRIBUTING 鼓励生态。
- **社区**：插件生态刚萌芽——最完整的社区插件（DSH-better-sidebar：文件管理/终端/Git 面板）仅十位数 stars。
- **文档**：官方 README/架构文档完整，但**系统性新手教程为零**（本白皮书填补此空白）。

## 1.6 什么时候用它（选型建议）

**推荐入场的场景**：
- 你想要一个**模型无关、界面可选、行为可改**的 Agent 底座
- 你想开发 dsh 插件并成为生态早期贡献者（先发优势）
- 你需要在服务器/CI 跑 Agent（headless profile）

**暂时观望的场景**：
- 只要"开箱即用的编码助手"——Claude Code 等更成熟
- 不能接受快速迭代期的破坏性变更——生产核心依赖建议等 `0.1.0` 正式版

---

**下一章**：[第 2 章：五分钟快速上手](./02-quickstart.md) —— 装起来，跑起来。
