# DeepSeek Harness 新手教程白皮书

> 从零上手 DeepSeek Harness（dsh）——DeepSeek 官方开源的 Agent 运行时与插件生态。
> 本白皮书面向**第一次接触 dsh 的开发者**，用真实可跑的示例带你走完：安装 → 使用 → 开发插件 → 实战调优。

[English](./docs/README.en.md)（规划中）· [GitHub](https://github.com/Electricitysheep/dsh-handbook)

## 为什么需要这本白皮书

2026-08-13，DeepSeek 正式开源 **DeepSeek Harness（`dsh`）**——一个"everything is a plugin"的 Agent 运行时（基于 Cordis）。它的定位介于 Claude Code 与自建 Agent 框架之间：官方提供 Web UI 与 headless CLI，同时开放了完整的插件体系，让社区开发自己的工具、界面与工作流。

但官方文档以架构说明为主，**缺少一条面向新手的上手路径**。这本白皮书补上这条路——每章都有可复制、可运行的示例，所有命令均在本机（Windows/macOS/Linux）实测验证。

## 目录

| 章节 | 内容 | 状态 |
|---|---|---|
| [第 1 章：认识 DeepSeek Harness](./docs/01-intro.md) | 它是什么、架构、与 Claude Code / OpenCode 的差异、插件生态定位 | ✅ |
| [第 2 章：五分钟快速上手](./docs/02-quickstart.md) | 安装、web / headless 双模式、第一个对话、模型与推理档位 | ✅ |
| [第 3 章：profile 与插件系统](./docs/03-profiles.md) | profile 结构、cordis.patch.yml、插件注册、host/client 双半 | 规划中 |
| [第 4 章：插件开发实战](./docs/04-plugin-dev.md) | 从零写第一个插件：settings、agent/request waterfall、事件监听 | 规划中 |
| [第 5 章：实战案例](./docs/05-cases.md) | Git 面板、HTML 草稿预览、tool 加速插件——真实代码讲原理 | 规划中 |
| [第 6 章：进阶与性能调优](./docs/06-advanced.md) | MCP、subagent、workflow、reasoning_effort 策略、常见坑 | 规划中 |
| [第 7 章：生态与资源](./docs/07-ecosystem.md) | dsh-plugin、官方 Discussions/Discord、社区插件清单 | 规划中 |

## 白皮书 PDF

- [DeepSeek-Harness-白皮书.pdf](./DeepSeek-Harness-白皮书.pdf)（随章节更新重新生成）

## 版本说明

- 基于 dsh `0.1.0-rc.6` / DeepSeek-V4-Flash-0731 系列（2026-08-13 开源）
- 所有示例命令在 Windows 11 + Node 24 环境实测

## 许可

[CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/)（内容）· 示例代码 MIT
