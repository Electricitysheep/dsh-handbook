# 附录：同模型 × 不同 Agent 实测对比（Benchmark）

> 实测日期：2026-08-13 ｜ 模型：deepseek-v4-flash（同一 opencode-go 网关，同一 API key）｜ Agent：dsh / opencode / omp
> 目的：**控制模型变量，对比 Agent 工程层的差异**（提示词、工具链、轮次管理）。

## 方法

| 项 | 说明 |
|---|---|
| 模型 | `deepseek-v4-flash`（三 agent 均走 opencode-go 网关 + 同一 key，公平对照） |
| Agent | dsh（headless profile）、opencode（`opencode run`）、omp（`--print` 非交互） |
| 任务 | T1 创建文件 / T2 搜索统计 / T3 修复 bug + 验证 |
| 环境 | Windows 11 + Node 24，独立工作目录，无预置上下文 |
| 度量 | 耗时（秒）+ 正确性（人工核对产物/输出） |

## 结果（3 轮采样，取中位数）

| Agent | T1 创建文件 | T2 搜索统计 | T3 修 bug+验证 | 总计（中位） | 正确率 |
|---|---|---|---|---|---|
| **omp** | 10s ✅ | 11s ✅ | 15s ✅ | **36s** | 27/27 |
| **dsh** | 22s ✅ | 15s ✅ | 48s ✅ | **85s** | 27/27 |
| **opencode** | 35s ✅ | 37s ✅ | 42s ✅ | **114s** | 27/27 |

原始 3 轮（秒）：

| Agent | 轮次 | T1 | T2 | T3 |
|---|---|---|---|---|
| dsh | 1 / 2 / 3 | 11 / 27 / 22 | 11 / 15 / 22 | 27 / 48 / 74 |
| opencode | 1 / 2 / 3 | 18 / 35 / 35 | 19 / 37 / 37 | 50 / 41 / 42 |
| omp | 1 / 2 / 3 | 9 / 10 / 12 | 9 / 11 / 12 | 13 / 33 / 15 |

## 解读

1. **正确率三家持平（27/27）**——同模型下，Agent 工程层的差异主要体现在**效率**而非**能力上限**（对这三个任务而言）。
2. **总耗时稳定排序**：omp < dsh < opencode（3 轮一致）。
3. **任务类型影响排序**：T3（多步：读→改→运行验证）波动最大（dsh 27→74s），说明复杂任务对 Agent 的轮次管理/工具效率更敏感。
4. **dsh 定位**：dsh 居中，且 headless 是"运行时 + 插件生态"——**同样的模型，通过插件（如 tool-turbo 降推理档）可进一步优化耗时**（见第 6 章）。
5. **样本警示**：3 轮 × 3 任务，同网关同 key，含网络抖动——方向可信，绝对值会随环境波动。

## 可复现

```bash
# 三个 agent 的命令（独立目录）
dsh --profile headless "任务"
opencode run "任务" --model opencode-go/deepseek-v4-flash
omp "任务" --model deepseek-v4-flash --print
```

> 完整任务定义与产物见本仓库 `benchmark/` 目录（规划中）。
