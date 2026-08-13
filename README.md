# DeepSeek Harness 白皮书 · dsh-handbook

> **从 0 到 1 玩转 DeepSeek Harness——官方开源 Agent 运行时的新手百科全书。**
> 中文 · [English](./README.en.md) · 持续更新（随 dsh rc 版本迭代）

<div align="center">

![dsh-handbook](https://img.shields.io/badge/dsh--handbook-白皮书-blue)
![chapters](https://img.shields.io/badge/章节-7-green)
![pdf](https://img.shields.io/badge/PDF-1.25MB-orange)
![license](https://img.shields.io/badge/license-CC--BY--NC--SA--4.0-lightgrey)
![dsh](https://img.shields.io/badge/dsh-0.1.0--rc.6-8A2BE2)

</div>

## 这是什么

**DeepSeek Harness（`dsh`）**是 DeepSeek 官方 2026-08-13 开源的 Agent 运行时——一个"一切皆插件"（everything is a plugin）的框架。但官方文档以架构说明为主，**缺少一条从零上手的路径**。

**这本白皮书补上这条路**：从"什么是 Agent 运行时"讲起，到安装、使用、开发插件、性能调优——每一章都有可复制、可运行的命令，全部在本机实测验证。**目标是：任何一个开发者，跟着这本书都能从 0 到 1 用起来、写起来。**

## 快速体验（30 秒）

```bash
# 1. 安装（需要 Node.js ≥ 22）
npx -y @deepseek-ai/dsh web

# 2. 浏览器打开 http://127.0.0.1:3080，开始对话
# 3. 或跑一次性任务（适合脚本/CI）
dsh --profile headless "你好，请用一句话介绍自己"
```

> 详细步骤见 [第 2 章：五分钟快速上手](./docs/02-quickstart.md)

## 目录（从 0 到 1）

| # | 章节 | 你将学会 | 状态 |
|---|---|---|---|
| 1 | [认识 DeepSeek Harness](./docs/01-intro.md) · [EN](./docs/01-intro.en.md) | 它是什么、为什么值得学、**与主流 Agent 全面对比**、FAQ | ✅ 双语 |
| 2 | [五分钟快速上手](./docs/02-quickstart.md) | 安装、web/headless 双模式、模型与推理档位、排障 | ✅ |
| 3 | [profile 与插件系统](./docs/03-profiles.md) | 可定制骨架、插件挂载、host/client 双半、扩展点、真实坑 | ✅ |
| 4 | [插件开发实战](./docs/04-plugin-dev.md) | 从零写第一个插件（完整代码 + 测试 + 实机验证） | ✅ |
| 5 | [实战案例](./docs/05-cases.md) | 三个真实开源 PR 的完整闭环 | ✅ |
| 6 | [进阶与性能调优](./docs/06-advanced.md) | 推理档位策略、耗时分析、踩坑清单 | ✅ |
| 7 | [生态与资源](./docs/07-ecosystem.md) | 官方入口、参与路径、阅读建议 | ✅ |

## 演示（Demo）

| 演示 | 说明 |
|---|---|
| [📺 30 秒看懂 dsh](./docs/demo.md) | 图文演示：安装 → Web UI → Headless → 插件（真实截图） |
| [⚡ 社区插件演示](./docs/demo-plugin.md)（规划中） | Git 面板 / 工具加速插件实操 |

## 白皮书 PDF

- **中文完整版**：[DeepSeek-Harness-白皮书.pdf](./DeepSeek-Harness-白皮书.pdf)（7 章合订，1.25MB）
- 英文版 PDF 随英文章节完成度更新

## 为什么值得读（而不是只看官方文档）

| 官方文档 | 本白皮书 |
|---|---|
| 架构视角（AGENTS.md / architecture.md） | **新手视角**：一条从 0 到 1 的路径 |
| 零散示例 | **每章可运行**，命令全部实测 |
| 无中文教程 | **中文优先**，英文同步 |
| 无生态实操 | **真实插件/PR 拆解**（含踩坑与安全约束） |

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
