# DeepSeek Harness（dsh）从 0 到 1 教程：官方开源 Agent 运行时，附 3 个 Agent 实测对比

**仓库**：https://github.com/Electricitysheep/dsh-handbook （中英双语 + PDF）

DeepSeek 8-13 开源了它的 Agent 运行时 **DeepSeek Harness（dsh）**——"一切皆插件"架构（基于 Cordis），自带 web + headless 两种形态。官方文档偏架构，缺一条新手路径，所以我写了这套从 0 到 1 的教程。

**7 章内容（命令全部实测验证）**：
1. 认识 dsh（什么是 harness、和 Claude Code/OpenCode 的区别）
2. 五分钟快速上手（web + headless、推理档位 low/high/max）
3. profile 与插件系统（扩展点 + 真实踩坑）
4. 插件开发实战（完整可运行代码：agent/request waterfall + 纯函数策略）
5. 实战案例（3 个真实开源 PR 拆解）
6. 进阶与性能调优（工具链任务 90% 时间在思考）
7. 生态与资源

**附加亮点：同模型 × 不同 Agent 实测**（统一 deepseek-v4-flash + 同一网关 + 同一 key，3 轮取中位数）：

| Agent | 3 任务总耗时 | 正确率 |
|---|---|---|
| omp | 36s | 27/27 |
| dsh | 85s | 27/27 |
| opencode | 114s | 27/27 |

同模型下能力打平（27/27），差异在 Agent 工程层的效率。

配套：[dsh-tool-turbo](https://github.com/Electricitysheep/dsh-tool-turbo) 提速插件（自动降推理档，日志验证 high→low 生效）。

欢迎 Star / issue 反馈 / 参与翻译。
