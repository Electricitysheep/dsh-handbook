# 第 7 章：生态与资源

> 本章目标：给你一份"加入 dsh 生态"的地图——官方入口、社区现状、以及参与方式。

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

## 结语

dsh 是 2026-08-13 才开源的项目——**生态的每一天都是"早期"**。白皮书会随 dsh 演进持续更新。如果某章命令失效，大概率是 rc 版本迭代所致——以官方 changelog 为准。

祝你在这个全新的生态里，抢到自己的位置。🚀
