# DeepSeek Harness 白皮书 · dsh-handbook

> **从 0 到 1 玩转 DeepSeek Harness的新手百科全书。**
> ⭐ 如果你觉得有帮助，点个 Star 支持持续更新 · 中文 · [English](./README.en.md)

<p align="center">
  <img src="./docs/assets/banner.svg" alt="dsh-handbook banner" width="720"/>
</p>

<div align="center">

![dsh-handbook](https://img.shields.io/badge/dsh--handbook-白皮书-blue)
![chapters](https://img.shields.io/badge/章节-14-green)
![pdf](https://img.shields.io/badge/PDF-3.9MB-orange)
![license](https://img.shields.io/badge/license-CC--BY--NC--SA--4.0-lightgrey)
![dsh](https://img.shields.io/badge/dsh-0.1.0--rc.6-8A2BE2)

</div>

## 这是什么

**DeepSeek Harness（`dsh`）**是 DeepSeek 官方 2026-08-13 开源的 Agent 运行时——一个"一切皆插件"（everything is a plugin）的框架。

<img width="614" height="230" alt="image" src="https://github.com/user-attachments/assets/19482c24-2208-468e-ad38-9096d9270f8d" />

但官方文档以架构说明为主，**缺少一条从零上手的路径**。

**这本白皮书补上这条路**：从"什么是 Agent 运行时"讲起，到安装、使用、开发插件、性能调优——每一章都有可复制、可运行的命令，全部在本机实测验证。**目标是：任何一个开发者，跟着这本书都能从 0 到 1 用起来、写起来。**

## 这本能给你什么

| 如果你是… | 你会得到 |
|---|---|
| 🆕 **第一次接触 dsh** | 3 天从 0 到 1 学习路径（每天有目标+验收） |
| 🛠 **开发者** | 可克隆的插件模板 + 配置参考大全（照抄能跑） |
| ⚖️ **正在选型** | 14 个主流 Agent 对比（表格+文字）+ 同模型实测 benchmark |
| ⚡ **要调优** | 推理档位策略 + 缓存命中率专题（实测 97%） |
| 📚 **要案例** | 5 个真实复杂案例（含耗时/产物/验证） |
| 🌏 **英文读者** | 英文版 PDF + 第 3-11 章英文翻译 |

## 快速体验（30 秒）

```bash
# 1. 安装（需要 Node.js ≥ 22）
npx -y @deepseek-ai/dsh web

# 2. 浏览器打开 http://127.0.0.1:3080，开始对话
# 3. 或跑一次性任务（适合脚本/CI）
dsh --profile headless "你好，请用一句话介绍自己"
```

> 想系统学？看 [🗺 学习路径（3 天计划）](./docs/roadmap.md)；想先跑？[第 2 章：五分钟快速上手](./docs/02-quickstart.md)；想速查？[📇 一页速查卡](./docs/cheatsheet.md)

## 目录（从 0 到 1）

| # | 章节 | 你将学会|
|---|---|---|---|
| 🗺 | [学习路径（3 天计划）](./docs/roadmap.md) | 从 0 到 1：每天目标 + 验收标准 + 学习原则|
| 1 | [认识 DeepSeek Harness](./docs/01-intro.md) · [EN](./docs/01-intro.en.md) | 它是什么、为什么值得学、**与主流 Agent 全面对比**、FAQ|
| 2 | [五分钟快速上手](./docs/02-quickstart.md) · [EN](./docs/02-quickstart.en.md) | 安装、web/headless 双模式、模型与推理档位、排障|
| 3 | [profile 与插件系统](./docs/03-profiles.md) | 可定制骨架、插件挂载、host/client 双半、扩展点、真实坑|
| 4 | [插件开发实战](./docs/04-plugin-dev.md) | 从零写第一个插件（完整代码 + 测试 + 实机验证）|
| 5 | [dsh 应用场景](./docs/05-cases.md) | 5 大场景 + 高缓存命中率专题 + 5 行业视角 + 提示词法则|
| 6 | [进阶与性能调优](./docs/06-advanced.md) | 推理档位策略、耗时分析、踩坑清单|
| 7 | [生态与资源](./docs/07-ecosystem.md) | 官方入口、参与路径、阅读建议|
| 8 | [工具与上下文系统](./docs/08-tools-context.md) | 60+ 能力包地图、内置工具、上下文注入、compaction、安全模型|
| 9 | [MCP、子代理与工作流](./docs/09-mcp-subagent-workflow.md) | 外部工具接入、并行子代理、多步编排、Agent 系统蓝图|
| 10 | [复杂实战案例](./docs/10-complex-cases.md) | **dsh 真实跑出的**：数据清洗+可视化管线（186s）、5-bug 修复+49 测试（94s），含产物与判断力分析|
| 11 | [未来展望](./docs/11-future.md) | 技术/生态/竞争/行业/机会/风险 六角度演进预测 + 时间线|
| 附 | [术语表与命令速查](./docs/appendix-glossary.md) · [Benchmark](./docs/benchmark.md) | 30+ 术语、命令速查、3 Agent 实测|

## 内容精华速览（点开即看，不止链接）

<details>
<summary><b>📖 第 1 章：认识 DeepSeek Harness —— 三个直觉 + 能力矩阵</b></summary>

- **三个直觉**：dsh = Agent 的乐高底座；harness = 套在模型外的工程层；2026 = Agent 可编程时代
- **核心事实**：MIT 开源 · TypeScript · "一切皆插件" · 2026-08-13 发布
- **dsh vs 6 个主流 Agent 能力矩阵**（Claude Code / Codex / OpenCode / Gemini / Kimi）：开源✅、模型无关✅、**官方级插件体系**（独有）、自定义界面✅、headless CI✅
- **选型决策**：深度定制+生态 → dsh；开箱即用 → Claude Code
</details>

<details>
<summary><b>⚡ 第 2 章：五分钟快速上手 —— 30 秒跑起来</b></summary>

- **一条命令启动**：`npx -y @deepseek-ai/dsh web` → http://127.0.0.1:3080
- **双模式**：web（对话 UI）/ headless（`dsh --profile headless "任务"`，CI 友好）
- **推理档位三档**：low（最快/简单任务）· high（默认）· max（最强/复杂推理）——**性能关键：思考占工具链 90% 时间**
- **第一个插件**：Git 面板 4 步挂载
</details>

<details>
<summary><b>🧩 第 3 章：profile 与插件系统 —— 可定制骨架</b></summary>

- **profile** = bundle 栈 + 你的 patch 层（`package.json` + `cordis.patch.yml`）
- **挂载插件只需 2 处改动**（加依赖 + 加 insert 行）
- **host/client 双半**：一个 npm 包 = Node 侧工具/服务 + 浏览器侧 UI
- **5 大扩展点**：`agent/request` waterfall、`conversationEvents`、`ctx.slots`、`settings`、`ctx.provide`
- **6 个真实踩坑**：rc.1 依赖断裂、插件缺 main、`next()` 忘 await、类型不识别、ModuleLoader、端口占用
</details>

<details>
<summary><b>🛠 第 4 章：插件开发实战 —— 完整可运行代码</strong></summary>

- **从零写提速插件**（`dsh-tool-turbo` 完整拆解）：纯函数决策 + `agent/request` waterfall 注入
- **核心技巧**：决策逻辑抽纯函数（单测毫秒级）→ 实机只验证"注入是否发生"
- **3 条开发纪律**：先找扩展点 / 逻辑抽纯函数 / 实机验证不能省
- **实机日志证据**：`calls=[{name:"write"}] => reasoningEffort=low`
</details>

<details>
<summary><b>📦 第 5 章：实战案例 —— 三个真实开源 PR 的完整闭环</strong></summary>

- **Git 面板 push/pull/fetch**（PR #10）：`--force-with-lease` 安全红线 + 本地 bare-repo 集成测试 + Playwright 实机验证
- **HTML 草稿预览**（PR #11）：沙箱安全约束下的 srcdoc 决策纯函数
- **tool-turbo 提速插件**：长工具链每步思考降档
</details>

<details>
<summary><b>🚀 第 6 章：进阶与性能调优 —— 时间花在哪</strong></summary>

- **性能模型**：工具链任务 90% 时间在模型思考（每次工具调用前）
- **档位策略**：简单轮次 low / 日常 high / 复杂 max——降档是最高杠杆提速
- **7 个真实坑**：含"简单任务突然变快 = 缓存命中"的评测陷阱
- **看成绩单三问**：谁测的 / 什么 harness / 验证器多严
</details>

<details>
<summary><b>🧰 第 8 章：工具与上下文系统 —— 能力引擎</b></summary>

- **60+ 官方能力包地图**：工具/上下文/会话/子代理/MCP/工作流/安全
- **内置工具（实测）**：read/write/grep/glob/edit/bash/todo/skill
- **产物追踪**：工具返回 locations → 对话末尾可打开产物
- **上下文注入**：系统提示分层 + 技能目录
- **长对话自动压缩**（compaction）+ 沙箱/权限/审批安全层
</details>

<details>
<summary><b>🔗 第 9 章：MCP、子代理与工作流 —— Agent 系统化</b></summary>

- **MCP**：接入外部工具服务器（社区已有 token 追踪插件）
- **子代理**：并行委派任务（大仓库调研/长任务分解）
- **工作流**：确定性多步编排（拉取→清洗→报表→校验）
- **四阶段新手路径**：单 Agent → +MCP → +子代理 → +工作流
</details>

<details>
<summary><b>🧪 第 10 章：复杂实战案例 —— dsh 真实跑出来的</b></summary>

- **案例 A**：数据质量分析→清洗→可视化（186s，52→35 行归零，chart.png，含权衡说明）
- **案例 B**：5-bug 修复 + 49 测试（94s，pytest 49 passed，覆盖除零/负数/精度边界）
- **画像**：多步工具链自动编排 + 有判断力 + 产物可追踪
- 隐私声明：全部合成数据/自造代码
</details>

<details>
<summary><b>📚 附录：术语表 + 命令速查</b></summary>

- **30+ 术语**：harness/profile/bundle/cordis/扩展点/waterfall/compaction…
- **命令速查**：dsh 核心 / 环境 / 排障 / 插件开发
- **Benchmark**：同模型 3 Agent 实测（3 轮中位数）
</details>

<details>
<summary><b>🌐 第 7 章：生态与资源 —— 加入 dsh 生态的地图</strong></summary>

- **官方入口**：仓库 / API 文档 / Discord / Discussions
- **当前状态**：官方暂不收外部 PR → **做 dsh-plugin 生态项目是官方点名的贡献方式**
- **新手路径**：用起来 → 小 PR → 发插件 → 写内容
</details>

## 演示（Demo）—— 直接看效果

### ① Web UI 对话（`dsh web`）

```bash
dsh web    # → http://127.0.0.1:3080
```

![dsh Web UI 对话](./docs/assets/demo-web-chat.png)

### ② Headless CLI（一次性任务，适合脚本/CI）

```bash
dsh --profile headless "你好，请用一句话介绍你自己"
# → 你好！我是 DeepSeek 驱动的 AI 编程助手，可以帮你写代码、调试问题、
#    处理文件、搜索资料，以及完成各种开发和办公任务。
```

### ③ 插件生态（Git 面板，`dsh-better-sidebar`）

![dsh Git 面板（better-sidebar 插件）](./docs/assets/demo-git-panel.png)

> 完整图文演示见 [📺 30 秒看懂 dsh](./docs/demo.md)。

## 快速上手资产

| 资产 | 用途 |
|---|---|
| [📇 一页速查卡](./docs/cheatsheet.md) | 打印/收藏，日常不翻书 |
| [🔧 插件模板（可克隆）](./examples/plugin-template/README.md) | 照抄就能跑的 host 插件骨架（第 4 章配套） |
| [⚙️ 配置参考大全](./docs/config-reference.md) | settings/cordis.patch.yml/profile 全字段 |
| [❓ FAQ 速查](./docs/faq.md) | 入门/安装/性能/插件/安全/生态 六类高频问题 |

## DSH vs 主流 Agent（能力矩阵）

| 维度 | **dsh** | Claude Code | OpenAI Codex | OpenCode | Gemini CLI | Kimi CLI|
|---|---|---|---|---|---|---|
| 开源 | ✅ MIT | ❌ | ❌ | ✅ MIT | ❌ | ❌|
| 模型绑定 | 模型无关 | Claude 系 | GPT 系 | 任意 | Gemini 系 | Kimi 系|
| **插件体系** | **官方级：一切皆插件，60+ 官方包** | 配置/钩子 | 配置 | 配置 | 无 | 无|
| 自定义界面 | ✅（client 半） | ❌ | ❌ | 部分 | ❌ | ❌|
| 自动化/CI | ✅ headless | ✅ | ✅ | ✅ | ✅|
| TUI | 插件可做 | ✅ 内置 | ✅ 内置 | ✅ 内置 | ✅|
| 生态阶段 | 零日（2026-08-13） | 成熟 | 成熟 | 成熟 | 成熟 | 早期|
| 适合谁 | 深度定制+生态 | 开箱即用 | 开箱即用 | OpenCode 用户 | Google | Kimi|

> 实测案例、同模型多 Agent 对比数据见 [第 1 章](./docs/01-intro.md) 与 benchmark 章节。

## 同模型 × 不同 Agent 实测（2026-08-13）

> 模型统一 `deepseek-v4-flash`（同一网关、同一 key），只对比 Agent 工程层。3 任务全部正确完成，差异在效率：

| Agent | 总耗时 | 正确率|
|---|---|---|
| **omp** | **36s** | 27/27 ✅|
| **dsh** | **85s** | 27/27 ✅|
| **opencode** | 114s | 27/27 ✅|

> 3 轮采样中位数，27/27 全对。完整方法/解读见 [📊 Benchmark 附录](./docs/benchmark.md)。

## 白皮书 PDF

- **中文完整版**：[DeepSeek-Harness-白皮书.pdf](./DeepSeek-Harness-白皮书.pdf)（13 章节，109k 字符，3.9MB）
- **英文完整版**：[DeepSeek-Harness-Handbook.pdf](./DeepSeek-Harness-Handbook.pdf)（10 章，54k 字符）

## 为什么值得读（而不是只看官方文档）

| 官方文档 | 本白皮书|
|---|---|
| 架构视角（AGENTS.md / architecture.md） | **新手视角**：一条从 0 到 1 的路径|
| 零散示例 | **每章可运行**，命令全部实测|
| 无中文教程 | **中文优先**，英文同步|
| 无生态实操 | **真实插件/PR 拆解**（含踩坑与安全约束）|

## 与生态联动

本白皮书的方法论来自真实开源实践：
- [dsh-tool-turbo](https://github.com/Electricitysheep/dsh-tool-turbo) —— 工具调用提速插件（第 4/6 章源码）
- [DSH-better-sidebar](https://github.com/omdsh-dev/DSH-better-sidebar) —— 社区侧边栏插件（第 5 章案例）

## 贡献与反馈

- 章节/命令失效？rc 版本迭代所致，欢迎 issue 指正
- 想参与？见 [第 7 章：生态与资源](./docs/07-ecosystem.md)

## 版本说明

- 基于 dsh `0.1.0-rc.6` / DeepSeek-V4-Flash-0731（2026-08-13 开源）
- 示例环境：Windows 11 + Node 24

## 许可

内容 [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) · 示例代码 MIT
