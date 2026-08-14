# 第 7 章：生态与资源

> 本章目标：给你一份"加入 dsh 生态"的地图——官方入口、社区现状、插件实操、以及参与方式。

## TL;DR（本章核心，30 秒版）

1. **官方入口**：GitHub 仓库（源码 + issue）、API 文档、Discord、Discussions——当前贡献入口以 Discussions 为主
2. **外部 PR 暂不接受**（2026-08-13 时点），但官方鼓励做 dsh-plugin 生态项目、写教程/博客
3. **插件生态快照**：`DSH-better-sidebar`（最完整社区插件）、`dsh-tool-turbo`（提速插件）、本白皮书——发现插件搜 `topic:dsh-plugin`
4. **新手参与路径**：用起来 → 小改进（给社区插件提 PR）→ 发插件 → 写内容
5. **生态零日 = 先发优势**：每个早期生态都有"第一个吃螃蟹的人"的红利，现在入场正是时候

<details><summary>本章导航</summary>
- [7.1 官方入口](#71-官方入口)
- [7.2 插件生态（2026-08-13 快照）](#72-插件生态2026-08-13-快照)
- [7.3 如何参与生态（新手路径）](#73-如何参与生态新手路径)
- [7.4 推荐阅读路径](#74-推荐阅读路径)
- [7.5 真实插件安装实操](#75-真实插件安装实操)
- [7.6 发现插件的方法](#76-发现插件的方法)
- [7.7 参与生态的完整流程](#77-参与生态的完整流程)
- [7.8 生态里程碑时间线](#78-生态里程碑时间线)
- [7.9 与官方讨论区的联动](#79-与官方讨论区的联动)
</details>

## 7.1 官方入口

| 资源 | 地址 | 用途 |
|---|---|---|
| 官方仓库 | https://github.com/deepseek-ai/deepseek-harness | 源码、架构文档、issue |
| API 文档 | https://api-docs.deepseek.com | 模型、定价、API 指南 |
| Discord | 官方 README 内链接 | 社区讨论 |
| Discussions | 官方仓库 Discussions | 提案/求助（官方当前建议的贡献入口） |

**注意**：官方 CONTRIBUTING 明确"目前不接受外部 PR"（2026-08-13 时点）——但鼓励：
- 在 Discussions 提建议（官方会评估）
- **做 dsh-plugin 生态项目**（官方点名认可的方式）
- 写教程/博客

## 7.2 插件生态（2026-08-13 快照）

| 项目 | 定位 | 状态 |
|---|---|---|
| `DSH-better-sidebar` | 文件管理/终端/Git/浏览器侧边栏 | 社区最完整插件 |
| `dsh-tool-turbo` | 工具调用提速（reasoning_effort 自动调节） | 社区提速插件 |
| `dsh-handbook`（本白皮书） | 新手教程 | 生态文档 |

**发现插件**：GitHub 搜 `topic:dsh-plugin`。
**发布插件**：给你的仓库加 `dsh-plugin` topic + npm 发布。

## 7.3 如何参与生态（新手路径）

1. **用起来**：`dsh web` + 装两个社区插件，跑通日常
2. **小改进**：给社区插件提 PR（读第 5 章的三个案例，那是完整的 PR 范式）
3. **发插件**：从第 4 章的最小 host 插件起步，挂 `dsh-plugin` topic
4. **写内容**：教程/测评/避坑文（官方鼓励），与本白皮书互相引用

## 7.4 推荐阅读路径

| 目标 | 路径 |
|---|---|
| 快速上手 | 第 2 章 → 装 better-sidebar → 日常用 |
| 开发插件 | 第 3 章 → 第 4 章 → 抄第 5 章案例 |
| 性能调优 | 第 6 章 → tool-turbo 源码 |
| 深度定制 | 官方 AGENTS.md（架构）→ docs/architecture.md → packages/ 源码 |

## 7.5 真实插件安装实操

以下给出两个代表性插件的**完整挂载步骤**（语法与第 3 章 3.2 节一致）。

### 安装 `DSH-better-sidebar`

**① `package.json` 加依赖**（`~/.dsh/profiles/web/package.json`）：

```json
{
  "dependencies": {
    "dsh-better-sidebar": "link:C:\\path\\to\\DSH-better-sidebar"
  }
}
```

**② `cordis.patch.yml` 加挂载行**：

```yaml
- insert:
    - id: better-sidebar
      name: dsh-better-sidebar
```

**③ 安装并验证**：

```bash
cd ~/.dsh/profiles/web && pnpm install && dsh web
```

重启后观察左侧是否出现文件管理/终端/Git/浏览器四个标签页。

### 安装 `dsh-tool-turbo`

**① `package.json` 加依赖**：

```json
{
  "dependencies": {
    "dsh-tool-turbo": "link:C:\\path\\to\\dsh-tool-turbo"
  }
}
```

**② `cordis.patch.yml` 加挂载行**：

```yaml
- insert:
    - id: tool-turbo
      name: dsh-tool-turbo
```

**③ 安装并验证**：

```bash
cd ~/.dsh/profiles/web && pnpm install && dsh web
```

发一个"创建 3 个文件"的任务，观察日志是否出现 `[tool-turbo] calls=[...] => reasoningEffort=low`（参考第 4 章 4.5 节）。

> ⚠️ 两个插件均要求 `@deepseek-ai/dsh-agent ^0.1.0-rc.6`，若 `pnpm install` 报 404，请检查版本线（见第 3 章 3.5 节）。

## 7.6 发现插件的方法

| 渠道 | 具体操作 | 预期结果 |
|---|---|---|
| **GitHub topic** | https://github.com/topics/dsh-plugin 或搜索 `topic:dsh-plugin` | 所有打了 topic 的仓库 |
| **GitHub 全局搜索** | `dsh-plugin` + 语言过滤 `TypeScript` | 含关键词的仓库与代码 |
| **npm 搜索** | `npm search dsh-plugin` 或 https://www.npmjs.com/search?q=dsh-plugin | 已发布的包（rc 阶段以 GitHub 为主） |
| **官方讨论区 Show and tell** | https://github.com/deepseek-ai/deepseek-harness/discussions/categories/show-and-tell | 社区自荐项目 |
| **本白皮书引用链** | 第 4/5/10 章案例中的仓库链接 | 经实机验证的插件 |

**技巧**：`topic:dsh-plugin` 是最精准的过滤方式。2026-08-13 时点结果仅个位数——正是入场机会。

## 7.7 参与生态的完整流程

把 7.3 节的"四步走"展开为**可操作的决策树**：

```text
用起来 → 提 Issue 反馈 → 发插件（npm publish） → 写内容
```

**npm publish 流程简述**：

1. 确保 `package.json` 有 `"name": "dsh-xxx"` + `"main": "src/index.ts"` + 正确 `peerDependencies`
2. `npm login` → `npm publish --access public`
3. 给 GitHub 仓库加 `dsh-plugin` topic
4. 到官方 Discussions 的 Show and tell 分类发帖

> 参考 CONTRIBUTING.md：案例需含"场景 / 命令 / 耗时或产物 / 验证方式"——发插件时附上这些信息，转化率更高。

## 7.8 生态里程碑时间线

| 时间 | 事件 | 意义 |
|---|---|---|
| **2026-08-13** | dsh 开源（零日） | MIT 协议发布，Agent 可编程时代起点 |
| **2026-08-13** | 60+ 官方包同步放出 | `packages/` 下工具/上下文/会话/子代理/MCP/工作流/安全/模型/界面全覆盖 |
| **2026-08-13 当天** | 社区插件爆发 | 官方讨论区单日 30+ 帖，含插件踩坑、TUI 示例、Windows 路径 bug 等 |
| **2026-08-13 当周** | 本白皮书发布 | 11 章中文教程 + Benchmark + 插件模板，补零日文档缺口 |
| **进行中** | 官方讨论区持续活跃 | 每周 2-3 帖响应，已覆盖插件/路径/TUI/vision 等方向（见 7.9 节） |
| **规划中** | 插件模板扩展 / 视频教程 / CI 校验 | ROADMAP.md P1 优先级 |

**关键认知**：2026-08-13 不是"发布日"而是"生态零日"——官方包、社区插件、中文教程同一天就位。对参与者而言，**现在入场 = 和官方基建同步成长**。

## 7.9 与官方讨论区的联动

本白皮书已在官方 Discussions 响应 5 帖，以下是**有效参与的实例**：

| 帖子 | 主题 | 响应方式 | 可复用模式 |
|---|---|---|---|
| [#380](https://github.com/deepseek-ai/deepseek-harness/discussions/380) | 插件踩坑 | 结论整理进第 3 章 3.5 节"常见坑" | 问题 → 复现 → 写教程 → 回帖引用 |
| [#392](https://github.com/deepseek-ai/deepseek-harness/discussions/392) | TUI examples | 补进 docs/config-reference.md | 官方缺示例 → 跑通 → 写参考 → 分享链接 |
| [#401](https://github.com/deepseek-ai/deepseek-harness/discussions/401) | Windows 路径 bug | 记录进第 12 章跨平台短板 | 平台 bug → 记录边界 → 帮官方分流 |
| [#384](https://github.com/deepseek-ai/deepseek-harness/discussions/384) | visionDS | 更新能力矩阵中 vision 支持状态 | 新能力 → 调研 → 更新表格 → 确认 |
| [#118](https://github.com/deepseek-ai/deepseek-harness/discussions/118) | 通用讨论 | 沉淀进 FAQ（docs/faq.md 六类问答） | 高频问答 → 分类沉淀 → 给链接 |

**有效参与的 3 个原则**：① 先自己跑通再回帖（带环境信息和报错日志）；② 把结论写成可引用内容（单条回复会沉底，写成章节/FAQ 才能持续产生价值）；③ 链接代替重复（回帖给链接，如"详见第 7 章 7.5 节"）。

## 结语

dsh 是 2026-08-13 才开源的项目——**生态的每一天都是"早期"**。白皮书会随 dsh 演进持续更新。如果某章命令失效，大概率是 rc 版本迭代所致——以官方 changelog 为准。

祝你在这个全新的生态里，抢到自己的位置。🚀

---

## 动手练习（检验你是否真懂了）

1. **理解题**：不看原文，说出 dsh 生态的 3 个官方入口（仓库/API 文档/社区）各自的用途
   > 自查：参考本章 7.1 节官方入口表格
2. **理解题**：官方当前"不接受外部 PR"，但鼓励哪三种参与方式？为什么"做 dsh-plugin 生态项目"是官方点名认可的方式？
   > 自查：参考本章 7.1 节"但鼓励"段落
3. **动手题**：在 GitHub 搜索 `topic:dsh-plugin`，列出你找到的 3 个社区插件，说出每个插件的定位
   > 自查：参考本章 7.2 节"发现插件"段落 + 7.6 节搜索渠道表格
4. **动手题**：按本章 7.5 节的步骤，完整挂载 `DSH-better-sidebar` 或 `dsh-tool-turbo`，记录 `pnpm install` 的输出和验证结果
   > 自查：参考本章 7.5 节两处改动的完整代码片段
5. **动手题**：给 `DSH-better-sidebar` 或 `dsh-tool-turbo` 的 README 提一个改进 PR（比如加一个安装步骤、修一个 typo），体验社区 PR 流程
   > 自查：参考本章 7.3 节第 2 步 + 第 5 章案例的 PR 范式
6. **思考题**：本章 7.8 节时间线显示"60+ 官方包同步放出"和"社区插件爆发"发生在同一天。这对开源项目的生态策略有什么启示？
   > 自查：参考本章 7.8 节时间线表格 + 7.9 节联动模式

## 常见疑问 FAQ

**Q1：官方说"不接受外部 PR"，那我的插件代码放哪？**
放在你自己的 GitHub 仓库，作为独立的 dsh-plugin 生态项目。官方鼓励这种方式——通过插件扩展能力，无需改 dsh 核心。给仓库加 `dsh-plugin` topic，npm 发布即可。

**Q2：Discord 和 Discussions 有什么区别？**
Discord 适合实时讨论；Discussions 适合正式提案、功能建议、求助（有记录可查）。官方当前建议的贡献入口是 Discussions。

**Q3：我想写中文教程/博客，有格式要求吗？**
没有官方格式要求。建议包含安装步骤、代码示例、实机截图/日志。可参考本白皮书结构（TL;DR + 分步讲解 + 练习）。

**Q4：生态零日是什么意思？为什么说是"先发优势"？**
生态零日 = 生态刚起步，内容/插件/教程几乎为零。先发优势 = 早期入场者容易成为"某个方向的标杆"。类比：2015 年写 React 教程的人、2018 年做 VS Code 插件的人。

**Q5：rc 阶段迭代快，我的插件会不会刚写完就过时？**
有可能。降低风险：① 依赖用 `^0.1.0-rc.6` 线；② 关注官方 changelog；③ 逻辑用纯函数隔离，接入层薄一点，升级时只改接入层。

**Q6：我想做 dsh 生态项目，但从哪开始？**
从"自己的痛点"开始。比如：① 想要 TUI → 做 tui profile 插件；② 想要 token 追踪 → 做 cost-tracker 插件；③ 想要 diff 视图 → 做 diff 插件。参考本章 7.4 节阅读路径。

**Q7：7.5 节的 `link:` 路径在 Windows 和 macOS 下写法一样吗？**
不一样。Windows 用反斜杠（`link:C:\path\to\plugin`），macOS/Linux 用正斜杠（`link:/path/to/plugin`）。建议社区插件最终走 npm 发布，消除路径差异。

**Q8：官方讨论区发帖有什么技巧，能让官方更快响应？**
参考 7.9 节 3 个原则：带环境信息、带复现步骤、先搜索避免重复。功能建议说明"解决什么问题"比"怎么实现"更重要。
