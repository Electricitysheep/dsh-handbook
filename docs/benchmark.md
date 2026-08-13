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

## 结果

| Agent | T1 创建文件 | T2 搜索统计 | T3 修 bug+验证 | 总耗时 | 正确率 |
|---|---|---|---|---|---|
| **omp** | 9s ✅ | 9s ✅ | 13s ✅ | **31s** | 3/3 |
| **dsh** | 11s ✅ | 11s ✅ | 27s ✅ | **49s** | 3/3 |
| **opencode** | 18s ✅ | 19s ✅ | 50s ✅ | **87s** | 3/3 |

## 解读

1. **正确率三家持平（3/3）**——同模型下，Agent 工程层的差异主要体现在**效率**而非**能力上限**（对这三个任务而言）。
2. **复杂任务差异放大**：T3（多步：读→改→运行验证）opencode 50s vs omp 13s（3.8x）。任务越复杂，Agent 的轮次管理/工具效率差异越明显。
3. **dsh 定位**：dsh 居中（49s），且 headless 是"运行时 + 插件生态"——**同样的模型，通过插件（如 tool-turbo 降推理档）可进一步优化耗时**（见第 6 章）。
4. **样本警示**：单次运行、每任务 1 例，耗时含网络抖动/网关负载——结论方向可信，绝对值需多次取中位数。

## 可复现

```bash
# 三个 agent 的命令（独立目录）
dsh --profile headless "任务"
opencode run "任务" --model opencode-go/deepseek-v4-flash
omp "任务" --model deepseek-v4-flash --print
```

> 完整任务定义与产物见本仓库 `benchmark/` 目录（规划中）。
