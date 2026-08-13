# DeepSeek Harness（dsh）从 0 到 1 深度手册：12 章 + 同模型多 Agent 实测对比

**仓库**：https://github.com/Electricitysheep/dsh-handbook （中英双语 + PDF + 一页速查卡）

DeepSeek 8-13 开源了它的 Agent 运行时 **DeepSeek Harness（dsh）**——"一切皆插件"架构（基于 Cordis），自带 web + headless 两种形态。官方文档偏架构，缺一条新手路径，所以我写了这套从 0 到 1 的深度手册。

**12 章内容（命令全部实测验证）**：
1. 认识 dsh（什么是 harness、和 Claude Code/Codex/OpenCode 的区别）
2. 五分钟快速上手（web + headless、推理档位 low/high/max）
3. profile 与插件系统（扩展点 + 6 个真实踩坑）
4. 插件开发实战（完整可运行代码：agent/request waterfall + 纯函数策略）
5. 实战案例（3 个真实开源 PR 拆解 + 高缓存命中率专题）
6. 进阶与性能调优（工具链任务 90% 时间在思考——降档是最高杠杆提速）
7. 生态与资源（官方暂不收外部 PR，做插件是点名的贡献方式）
8. 工具与上下文系统（60+ 官方能力包地图）
9. MCP、子代理与工作流（Agent 系统化四阶段）
10. 复杂实战案例（dsh 真实跑出的：数据清洗管线 186s、5-bug 修复 94s）
11. 未来展望（技术/生态/竞争/风险预测）
12. **已知不足与边界（诚实版）**——rc 阶段不稳定性、Windows 路径 bug、生态早期

**为什么值得看（vs 官方文档）**：
- 官方文档：架构视角、零散示例、无中文
- 本手册：新手视角的完整路径、每章可运行、中文优先、真实踩坑

**Bonus：同模型 × 多 Agent 实测 benchmark**（deepseek-v4-flash 同网关同 key，3 轮中位数）：

| Agent | 总耗时 | 正确率 |
|---|---|---|
| omp | 36s | 27/27 ✅ |
| dsh | 85s | 27/27 ✅ |
| opencode | 114s | 27/27 ✅ |

同模型 → 能力持平（27/27 全对），差异在 Agent 工程层的效率——这对"选型 Agent"很有参考价值。

**还有**：中英双语 PDF、一页速查卡（打印即用）、可克隆插件模板、配置参考大全、FAQ。

适合：想用 DeepSeek 做 Agent 的开发者、插件开发者、做技术选型的人。欢迎 Star + Issue 共建。
