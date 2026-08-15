# DeepSeek Harness 白皮书 · dsh-handbook

> **DeepSeek Harness 中文手册 × 生态观察中心**——从 0 到 1 玩转 dsh，跟着 780 帖讨论区看懂生态 · 中文 · [English](./README.en.md)

**📖 [在线阅读](https://electricitysheep.github.io/dsh-handbook/) · 📄 [下载 PDF](./DeepSeek-Harness-白皮书.pdf) · ⭐ [点 Star 支持](https://github.com/Electricitysheep/dsh-handbook/stargazers)**

**1804 插件 · 780 帖讨论区 · 15 章手册 · 195 帖社区响应 · 280+ Stars**

<p align="center">
  <img src="./docs/assets/banner.svg" alt="dsh-handbook banner" width="720"/>
</p>

<div align="center">

![GitHub stars](https://img.shields.io/github/stars/Electricitysheep/dsh-handbook?style=flat&color=yellow)
![GitHub release](https://img.shields.io/github/v/tag/Electricitysheep/dsh-handbook?label=release&color=success)
![dsh-handbook](https://img.shields.io/badge/dsh--handbook-白皮书-blue)
![chapters](https://img.shields.io/badge/章节-15-green)
![pdf](https://img.shields.io/badge/PDF-5.5MB-orange)
![license](https://img.shields.io/badge/license-CC--BY--NC--SA--4.0-lightgrey)
![dsh](https://img.shields.io/badge/dsh-0.1.0--rc.6-8A2BE2)

</div>

> [!WARNING]
> dsh 当前为 `0.1.0-rc.6`（预发布阶段），生产环境请谨慎评估，详见 [ℹ️ 版本说明](#ℹ️-版本说明)。

## 🚀 快速体验（30 秒）

```bash
# 1. 安装（需要 Node.js ≥ 22）
npx -y @deepseek-ai/dsh web

# 2. 浏览器打开 http://127.0.0.1:3080，开始对话
# 3. 或跑一次性任务（适合脚本/CI）
dsh --profile headless "你好，请用一句话介绍自己"
```

> 想系统学？看 [🗺 学习路径（3 天计划）](./docs/roadmap.md)；想先跑？[第 2 章：五分钟快速上手](./docs/02-quickstart.md)；想速查？[📇 一页速查卡](./docs/cheatsheet.md)

<p align="center">
  <img src="./docs/assets/demo-webui.gif" alt="dsh Web UI 实测演示" width="720"/>
  <br/>
  <sub><b>30 秒看懂 dsh Web UI</b>：新建会话 → 输入任务 → 模型选择 → 发送 → AI 回复</sub>
</p>

## 🎯 这是什么

**DeepSeek Harness（`dsh`）**是 DeepSeek 官方 2026-08-13 开源的 Agent 运行时——一个"一切皆插件"（everything is a plugin）的框架。

<img width="614" height="230" alt="image" src="https://github.com/user-attachments/assets/19482c24-2208-468e-ad38-9096d9270f8d" />

但官方文档以架构说明为主，**缺少一条从零上手的路径**。

**这本白皮书补上这条路**：从"什么是 Agent 运行时"讲起，到安装、使用、开发插件、性能调优——每一章都有可复制、可运行的命令，全部在本机实测验证。**目标是：任何一个开发者，跟着这本书都能从 0 到 1 用起来、写起来。**

### 为什么值得读（而不是只看官方文档）

| 官方文档 | 本白皮书|
|---|---|
| 架构视角（AGENTS.md / architecture.md） | **新手视角**：一条从 0 到 1 的路径|
| 零散示例 | **每章可运行**，命令全部实测|
| 无中文教程 | **中文优先**，英文同步|
| 无生态实操 | **真实插件/PR 拆解**（含踩坑与安全约束）|

## 🎁 这本能给你什么


| 如果你是… | 你会得到 |
|---|---|
| 🆕 **第一次接触 dsh** | 3 天从 0 到 1 学习路径（每天有目标+验收） |
| 🛠 **开发者** | 可克隆的插件模板 + 配置参考大全（照抄能跑） |
| ⚖️ **正在选型** | 6 个主流 Agent 对比（表格+文字）+ 同模型实测 benchmark |
| ⚡ **要调优** | 推理档位策略 + 缓存命中率专题（实测 97%） |
| 📚 **要案例** | 5 个真实复杂案例（含耗时/产物/验证） |

## 🌟 感谢与社区

首先要感谢每一位 Star、回复和投稿——这本手册不是一个人的作品，是 dsh 社区一起"长"出来的。

发布两天，很幸运得到了这些反馈：

- ⭐ **280+ Stars**——对一份刚发布的教程来说远超预期，感谢大家认可
- 💬 **官方库 195 帖回应**——我们持续在[讨论区](https://github.com/deepseek-ai/deepseek-harness/discussions)和大家一起踩坑、排障、交流
- 🧠 **FAQ 里的 39 条问题大多来自真实提问**——社区问什么，我们沉淀什么（#380/#817/#1052…）
- 📦 已向 [awesome-dsh-plugin](https://github.com/awesome-dsh-plugin/awesome-dsh-plugin) 提交收录 PR（[#33](https://github.com/awesome-dsh-plugin/awesome-dsh-plugin/pull/33)，待合并）；阮一峰周刊自荐已提交
- 🤝 与 30+ 社区项目互链（dsh-usage / dsh-sgme / AgentSoul / dsh-vault / egress-guard / agentmemory…）

> 内容随讨论区持续更新（[沉淀流水线](./docs/research/feedback-pipeline.md)，19 项可追踪）。如果你觉得有用，Star 是对我们最大的支持。

## 🔭 生态观察（第 15 章·全景报告）

> 把 **1804 个插件仓库**的数据盘点 × **780 帖讨论区**定性观察交叉验证，5 个关键结论：

| 结论 | 一句话 |
|---|---|
| 🪟 **Windows 是第一痛点** | 中文路径（15+ 帖同根因）/ koffi / 端口 / 子进程——数据讨论双证实 |
| 🧩 **"官方没做，社区全做"** | 桌面壳 140+ / TUI / 记忆 77 / 视觉 132——健康互补 |
| 🛡️ **安全审计活跃，工具稀缺** | sandbox 分类仅 9 个插件——**供给缺口** |
| 🐛 **序列化 bug 家族** | unknown tool / reasoning 省略 / run_code 丢弃——rc 期主战场 |
| 💰 **成本透明化是刚需** | 缓存命中 97% 实测 + 成本工具雨后春笋 |

**6 个能力缝**（官方可优先建）：视觉通道 · 记忆 seam · 桌面 TUI 协议 · 评测闭环 · Windows 一等支持 · 插件 registry
> 完整报告（含对开发者/选型者/观望者的建议）：[第 15 章](./docs/15-ecosystem-report.md)

## 📚 目录（从 0 到 1）

<div align="center">

| 🗺️ **[学习路径（3 天计划）](./docs/roadmap.md)** | 从 0 到 1：每天目标 + 验收标准 + 学习原则 |
|---|---|

</div>

### 🟢 阶段 1 · 入门：认知与上手

<div align="center">

| 📖 **[第 1 章 · 认识 Harness](./docs/01-intro.md)** | ⚡ **[第 2 章 · 五分钟上手](./docs/02-quickstart.md)** |
|---|---|
| 与主流 Agent 全面对比 · FAQ · [EN](./docs/01-intro.en.md) | 安装 · web/headless 双模式 · 推理档位 · [EN](./docs/02-quickstart.en.md) |

</div>

### 🔵 阶段 2 · 开发：骨架与插件

<div align="center">

| 🧩 **[第 3 章 · profile 与插件系统](./docs/03-profiles.md)** | 🛠️ **[第 4 章 · 插件开发实战](./docs/04-plugin-dev.md)** |
|---|---|
| 可定制骨架 · 插件挂载 · 扩展点 · 真实坑 | 从零写第一个插件（完整代码 + 测试 + 实机验证） |

</div>

### 🟠 阶段 3 · 实战：场景与调优

<div align="center">

| 📦 **[第 5 章 · dsh 应用场景](./docs/05-cases.md)** | 🚀 **[第 6 章 · 进阶与性能调优](./docs/06-advanced.md)** |
|---|---|
| 5 大场景 · 高缓存命中率专题 · 5 行业视角 | 推理档位策略 · 耗时分析 · 踩坑清单 |

</div>

### 🟣 阶段 4 · 生态：能力与编排

<div align="center">

| 🌐 **[第 7 章 · 生态与资源](./docs/07-ecosystem.md)** | 🧰 **[第 8 章 · 工具与上下文系统](./docs/08-tools-context.md)** | 🔗 **[第 9 章 · MCP 子代理与工作流](./docs/09-mcp-subagent-workflow.md)** |
|---|---|---|
| 官方入口 · 参与路径 · 阅读建议 | 60+ 能力包地图 · 内置工具 · compaction | 外部工具接入 · 并行子代理 · 多步编排 |

</div>

### 🔴 阶段 5 · 进阶：复杂案例与展望

<div align="center">

| 🧪 **[第 10 章 · 复杂实战案例](./docs/10-complex-cases.md)** | 🔮 **[第 11 章 · 未来展望](./docs/11-future.md)** | ⚠️ **[第 12 章 · 已知不足与边界](./docs/12-limitations.md)** |
|---|---|---|
| dsh 真实跑出：数据清洗管线 186s · 5-bug 修复 94s | 技术/生态/竞争/机会/风险 预测 + 时间线 | rc 版诚实版：不稳定性 · 生态早期 · 跨平台短板 |

</div>

<div align="center">

| 🛡️ **[第 13 章 · 安全与沙箱](./docs/13-security.md)** | 💰 **[第 14 章 · 缓存与成本](./docs/14-cost.md)** |
|---|---|
| 沙箱机制 · 权限模型 · 审批流 · 插件安全审计清单 | 缓存命中率实测 97% · 成本模型 · 推理档位联动 · 预算实战 |

</div>

| 📊 **[第 15 章 · 生态全景报告](./docs/15-ecosystem-report.md)** | |
|---|---|
| 1804 插件 × 780 帖交叉验证：5 大洞察 + 6 个能力缝 + 生态参与者建议 |

### 📎 附录

<div align="center">

| 📚 **[附录 A·术语表](./docs/appendix-glossary.md)** · 📦 **[附录 B·官方包速查](./docs/appendix-packages.md)** · 📊 **[附录 C·Benchmark](./docs/benchmark.md)** |
|---|
| 30+ 术语 · 命令速查 · 官方 @deepseek-ai/* 包清单 · 同模型 3 Agent 实测 |

</div>

## 💎 内容精华速览（点开即看，不止链接）

<details>
<summary><b>📖 第 1 章：认识 DeepSeek Harness —— 三个直觉 + 能力矩阵</b></summary>

- **三个直觉**：dsh = Agent 的乐高底座；harness = 套在模型外的工程层；2026 = Agent 可编程时代
- **核心事实**：MIT 开源 · TypeScript · "一切皆插件" · 2026-08-13 发布
- **dsh vs 5 个主流 Agent 能力矩阵**（Claude Code / Codex / OpenCode / Gemini / Kimi）：开源✅、模型无关✅、**官方级插件体系**（独有）、自定义界面✅、headless CI✅
- **选型决策**：深度定制+生态 → dsh；开箱即用 → Claude Code
</details>

<details>
<summary><b>⚡ 第 2 章：五分钟快速上手 —— 30 秒跑起来</b></summary>

- **一条命令启动**：`npx -y @deepseek-ai/dsh web` → http://127.0.0.1:3080
- **双模式**：web（对话 UI）/ headless（`dsh --profile headless "任务"`，CI 友好）

- **推理档位三档**：`low`（最快/简单任务）· `high`（默认）· `max`（最强/复杂推理）——**性能关键：思考占工具链 90% 时间**。>注：`low` 为本白皮书实测网关（pi-ai/opencode-go）档位；**DeepSeek 官方适配器为 `off`（关闭思考/最快）/ `high` / `max`**（见 02-quickstart 2.3 注）
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
<summary><b>🛠 第 4 章：插件开发实战 —— 完整可运行代码</b></summary>

- **从零写提速插件**（完整拆解）：纯函数决策 + `agent/request` waterfall 注入
- **核心技巧**：决策逻辑抽纯函数（单测毫秒级）→ 实机只验证"注入是否发生"
- **3 条开发纪律**：先找扩展点 / 逻辑抽纯函数 / 实机验证不能省
- **实机日志证据**：`calls=[{name:"write"}] => reasoningEffort=low`
</details>

<details>
<summary><b>📦 第 5 章：实战案例 —— 三个真实开源 PR 的完整闭环</b></summary>

- **Git 面板 push/pull/fetch**（PR #10）：`--force-with-lease` 安全红线 + 本地 bare-repo 集成测试 + Playwright 实机验证
- **HTML 草稿预览**（PR #11）：沙箱安全约束下的 srcdoc 决策纯函数
- **提速插件示例**：长工具链每步思考降档
</details>

<details>
<summary><b>🚀 第 6 章：进阶与性能调优 —— 时间花在哪</b></summary>

- **性能模型**：工具链任务 90% 时间在模型思考（每次工具调用前）
- **档位策略**：简单轮次 low / 日常 high / 复杂 max——降档是最高杠杆提速
- **7 个真实坑**：含"简单任务突然变快 = 缓存命中"的评测陷阱
- **看成绩单三问**：谁测的 / 什么 harness / 验证器多严
</details>

<details>
<summary><b>🌐 第 7 章：生态与资源 —— 加入 dsh 生态的地图</b></summary>

- **官方入口**：仓库 / API 文档 / Discord / Discussions
- **当前状态**：官方暂不收外部 PR → **做 dsh-plugin 生态项目是官方点名的贡献方式**
- **新手路径**：用起来 → 小 PR → 发插件 → 写内容
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
<summary><b>🔮 第 11 章：未来展望 —— 五个维度的预测</b></summary>

- **技术/生态/竞争/机会/风险** 五维度预测 + 时间线
- **机会点**：官方生态早期，做 dsh-plugin 项目是入场红利
</details>

<details>
<summary><b>⚠️ 第 12 章：已知不足与边界 —— rc 版诚实说</b></summary>

- **不稳定性**：rc 迭代快、破坏性变更频繁
- **生态早期**：官方包 60+ 但插件生态刚起步
- **跨平台短板**：Windows 家族踩坑记录（含 Node 版本红线）
</details>

<details>
<summary><b>🛡️ 第 13 章：安全与沙箱模型 —— 敢上生产的关键</b></summary>

- **沙箱机制**：进程隔离（bwrap/Landlock/Seatbelt）+ 权限分级 + 审批流
- **社区审计边界**：node:vm 非安全边界、approval 回环、workspace-write 递归删除等真实逃逸面
- **插件安全审计清单**：第三方审计方法论（[#454](https://github.com/deepseek-ai/deepseek-harness/discussions/454)）
</details>

<details>
<summary><b>💰 第 14 章：缓存与成本工程 —— 把"便宜"变工程</b></summary>

- **缓存机制**：上下文缓存 + 命中率实测 97%（Flash 折扣 98% / Pro 99%+）
- **成本模型**：token 花在哪 + 推理档位联动 + 真实任务预算
- **可视化**：session log / 余额插件看每笔成本
</details>

## 🖥 演示（Demo）—— 直接看效果

### ① Web UI 对话（`dsh web`）

```bash
dsh web    # → http://127.0.0.1:3080
```

![dsh Web UI 对话](./docs/assets/demo-web-chat.png)

### ② Headless CLI（一次性任务，适合脚本/CI）

运行 `dsh --profile headless "你好，请用一句话介绍你自己"`（命令见 [🚀 快速体验](#-快速体验30-秒)）：

```bash
# → 你好！我是 DeepSeek 驱动的 AI 编程助手，可以帮你写代码、调试问题、
#    处理文件、搜索资料，以及完成各种开发和办公任务。
```

### ③ 插件生态（Git 面板，`dsh-better-sidebar`）

![dsh Git 面板（better-sidebar 插件）](./docs/assets/demo-git-panel.png)

> 完整图文演示见 [📺 30 秒看懂 dsh](./docs/demo.md)。

## 🧰 快速上手资产（精华直接看）

<details>
<summary><b>📇 一页速查卡</b> —— 安装 · 命令 · 推理档位 · 排障</summary>

```bash
npx -y @deepseek-ai/dsh web          # 安装即启动 Web UI
dsh --profile headless "任务"        # 一次性任务（脚本/CI）
```

推理档位：`low`（最快/简单轮次）· `high`（默认）· `max`（最强/复杂推理）——`low` 为实测网关（pi-ai）档位，**官方适配器用 `off`/`high`/`max`**
> 工具链任务 90% 时间在思考——降档是最高杠杆提速
> 完整卡：[docs/cheatsheet.md](./docs/cheatsheet.md)
</details>

<details>
<summary><b>🔧 插件模板</b> —— 挂载只需 2 步</summary>

```yaml
# ① package.json 加依赖
"my-plugin": "link:C:\\path\\to\\my-plugin"
# ② cordis.patch.yml 加挂载
- insert:
    - id: my-plugin
      name: my-plugin
```
```bash
cd ~/.dsh/profiles/web && pnpm install && dsh web
```
> 可克隆模板（含纯函数+waterfall+测试）：[examples/plugin-template/](./examples/plugin-template/README.md)
</details>

<details>
<summary><b>⚙️ 配置参考</b> —— settings.yaml 核心</summary>

```yaml
agent-default-model:
  model: deepseek-v4-flash    # 或 deepseek-v4-pro
  reasoningEffort: high       # off（关闭思考/最快）/ high（默认）/ max（最强）
```
> 全字段（profile/cordis.patch.yml/常用场景）：[docs/config-reference.md](./docs/config-reference.md)
</details>

<details>
<summary><b>❓ FAQ Top 5</b></summary>

1. **dsh 是模型吗？** 不是——是运行时，模型通过 llm 插件接入
2. **和 Claude Code 区别？** Claude Code 是"整车"，dsh 是"乐高底座"（开源可定制）
3. **要花钱吗？** dsh 免费开源；对话按量付费（缓存折扣：Flash 档 98% / Pro 档 99%+，实测会话缓存命中率 97%）
4. **插件装不上 404？** rc.1 依赖断裂——用 `^0.1.0-rc.6` 线
5. **能进生产吗？** rc 阶段有破坏性变更；生态玩法现在可入
> 完整 FAQ（六类）：[docs/faq.md](./docs/faq.md)
</details>

## ⚖️ DSH vs 主流 Agent（能力矩阵）

| 维度 | **dsh** | Claude Code | OpenAI Codex | OpenCode | Gemini CLI | Kimi CLI |
|---|---|---|---|---|---|---|
| 开源 | ✅ MIT | ❌ | ❌ | ✅ MIT | ❌ | ❌ |
| 模型绑定 | 模型无关 | Claude 系 | GPT 系 | 任意 | Gemini 系 | Kimi 系 |
| **插件体系** | **官方级：一切皆插件，60+ 官方包** | 配置/钩子 | 配置 | 配置 | 无 | 无 |
| 自定义界面 | ✅（client 半） | ❌ | ❌ | 部分 | ❌ | ❌ |
| 自动化/CI | ✅ headless | ✅ | ✅ | ✅ | ✅ | ✅ |
| TUI | 插件可做 | ✅ 内置 | ✅ 内置 | ✅ 内置 | ✅ | ✅ |
| 生态阶段 | 零日（2026-08-13） | 成熟 | 成熟 | 成熟 | 成熟 | 早期 |
| 适合谁 | 深度定制+生态 | 开箱即用 | 开箱即用 | OpenCode 用户 | Google | Kimi |

> 实测案例、同模型多 Agent 对比数据见 [第 1 章](./docs/01-intro.md) 与 benchmark 章节。

## 📊 同模型 × 不同 Agent 实测（2026-08-13）

> 模型统一 `deepseek-v4-flash`（同一网关、同一 key），只对比 Agent 工程层。5 任务全部正确完成，差异在效率：

| Agent | 总耗时 | 正确率|
|---|---|---|
| **omp** | **70s** | 45/45 ✅|
| **dsh** | **130s** | 45/45 ✅|
| **opencode** | 172s | 45/45 ✅|

> 5 任务 × 3 轮采样中位数（T1 创建文件 → T5 多文件重构），45/45 全对。完整方法/解读见 [📊 Benchmark 附录](./docs/benchmark.md)。

<p align="center">
  <img src="./docs/assets/benchmark-bar.svg" alt="benchmark 柱状图：omp 70s / dsh 130s / opencode 172s" width="720"/>
</p>


## 📄 白皮书 PDF

- **中文完整版**：[DeepSeek-Harness-白皮书.pdf](./DeepSeek-Harness-白皮书.pdf)（15 章 + 附录 ABC，~130k+ 字符，5.5MB）
- **英文完整版**：[DeepSeek-Harness-Handbook.pdf](./DeepSeek-Harness-Handbook.pdf)（15 章 + 附录，83 页，约 160k 字符，1.7MB）

## 🌐 与生态联动

本白皮书的方法论来自真实开源实践：
- [DSH-better-sidebar](https://github.com/omdsh-dev/DSH-better-sidebar) —— 社区侧边栏插件（第 5 章案例）

### 🧩 社区插件推荐（来自官方讨论区 / [awesome-dsh-plugin](https://github.com/awesome-dsh-plugin/awesome-dsh-plugin) 精选）

| 插件 | 用途 |
|---|---|
| [dsh-specflow](https://github.com/lonelymoon87/dsh-specflow) | 规格驱动开发：技能+命令+目标实现+进度上下文 |
| [dsh-gitflow](https://github.com/lonelymoon87/dsh-gitflow) | 审批门控的 Git 工作流（status/diff/commit/branch） |
| [dsh-guardian](https://github.com/lonelymoon87/dsh-guardian) | 危险操作策略检查 + 输出脱敏 + 安全审查 |
| [dsh-code-intel](https://github.com/lonelymoon87/dsh-code-intel) | Tree-sitter 符号索引 + 混合搜索 |
| [dsh-tianshu-tui](https://github.com/huiliyi37/dsh-tianshu-tui) | 终端 UI（TUI） |
| [dsh-computer-use](https://github.com/Anionex/dsh-computer-use) | 无障碍优先的 macOS 电脑控制 |
| [dsh-data-agent](https://github.com/omdsh-dev/dsh-data-agent) | 连数据库写 SQL 的数据 Agent |
| [dsh-balance-meter](https://github.com/Ghost011118/dsh-balance-meter) | 余额 + 会话成本实时显示 |
| [dsh-usage](https://github.com/kestiany/dsh-usage) | Token 用量 + 费用估算 + 52 周热力图（#1169） |
| [dsh-sgme](https://github.com/freehul/sgme) | 记忆引擎：按场景注入 + 自动剪枝（省 65-96% 会话，#1052） |
| [AgentSoul](https://github.com/yuhui-sama/dsh-agentsoul) | 本地人格 + 长期记忆 + 记忆蒸馏（#1478） |
| [dsh-vault](https://github.com/akslcw/dsh-vault) | 加密凭据保险库：TOTP/API Key/SSH 加密存储（#1457） |

> 完整列表见 [awesome-dsh-plugin](https://github.com/awesome-dsh-plugin/awesome-dsh-plugin)（122+ 插件）。想被收录？[社区案例征集](https://github.com/Electricitysheep/dsh-handbook/discussions/12)

### 📣 官方讨论区活跃响应

已在 [deepseek-ai/deepseek-harness](https://github.com/deepseek-ai/deepseek-harness) Discussions 持续活跃响应（100+ 帖）：插件踩坑 #380 / 安全审计 #817 / 缓存成本 #1052/#1234 / 生态洞察帖 #839 等（[沉淀流水线](./docs/research/feedback-pipeline.md) 持续收录反馈）

## 🙏 贡献与反馈

- ⭐ 觉得有帮助？点个 Star 支持持续更新
- 📝 **跑过真实案例？** 投稿收录进白皮书（署名 + 季度精选 PDF）：[社区案例征集](https://github.com/Electricitysheep/dsh-handbook/discussions/12) ← 直接回帖，模板已备好
- 章节/命令失效？rc 版本迭代所致，欢迎 issue 指正
- 想参与？见 [🤝 贡献指南（CONTRIBUTING）](./CONTRIBUTING.md) · 想看计划？[🗺️ 路线图（ROADMAP）](./ROADMAP.md) · 生态参与见 [第 7 章](./docs/07-ecosystem.md)

## ℹ️ 版本说明

- 基于 dsh `0.1.0-rc.6` / DeepSeek-V4-Flash-0731（2026-08-13 开源）
- 示例环境：Windows 11 + Node 24

### 🔄 最近更新

- **15 章完整版**（第 13 安全沙箱 / 第 14 缓存成本 / 第 15 生态全景报告）+ 附录 A/B/C
- 讨论区反馈持续沉淀：FAQ 39 条 / KVCache 规则 / 内置 Agent 预设 / run_code 异步坑（[沉淀流水线](./docs/research/feedback-pipeline.md)）

## 📜 许可

内容 [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) · 示例代码 MIT
