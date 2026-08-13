# 第 6 章：进阶与性能调优

> 本章目标：从"能跑"到"跑得好"——推理档位策略、工具调用耗时分析、真实踩坑清单。

## 6.1 性能模型：dsh 的时间花在哪

实测一个"创建文件"任务的耗时分布：

| 阶段 | 占比 | 说明 |
|---|---|---|
| 模型思考（Think） | ~90% | **每次工具调用前**都会重新思考，是绝对大头 |
| 工具执行 | <1% | 文件写入等毫秒级 |
| 网络/渲染 | ~10% | API 往返 + UI 更新 |

**推论**：
- 简单任务 → 优化思考时间（降推理档）
- 长工具链任务 → 每步都省思考时间，累计收益最大
- 工具本身慢（搜索/大文件）→ 优化工具实现，不是调档

## 6.2 reasoning_effort 策略（官方三档）

| 档位 | 场景建议 |
|---|---|
| `low` | 简单/确定性轮次：文件操作、批量、工具链中的廉价步 |
| `high` | 日常 Agent 任务（默认） |
| `max` | 复杂推理、长链规划、debug |

**手动**：UI 的"推理等级"选择器，或 `~/.dsh/settings.yaml` 的 `reasoningEffort`。
**自动**：插件按工具轮次动态降档（`dsh-tool-turbo`，第 4 章）。

## 6.3 工具调用耗时可视化

dsh 的会话统计行（Web UI 底部）显示：`N 轮 · M 步 | LLM Xs · 工具调用 Ys | 首 token 平均 ...`——这是最快的瓶颈定位手段。

进阶：host 插件监听工具事件做 per-tool 计时（tool-turbo 已内置 host 日志版本），把"哪个工具最慢"暴露出来。

## 6.4 常见坑清单（真实踩过，含解法）

| # | 坑 | 现象 | 解法 |
|---|---|---|---|
| 1 | rc.1 依赖断裂 | `pnpm install` 404（`dsh-type-meta` 等从未发布） | 依赖用 `^0.1.0-rc.6` 线 |
| 2 | 插件缺 main | `No "exports" main defined` | 暴露 `.` 入口；`"main": "src/index.ts"` 可被 tsx 加载 |
| 3 | `next()` 忘 await | provider/model 丢失报错 | `agent/request` 的 `next()` 返回 Promise，必须 await |
| 4 | 事件类型不识别 | `'agent/request' is not assignable to keyof Events` | npm 未 re-export 类型增强，边界放宽签名 |
| 5 | client 测试跑不了 | jsdom 报 `window.__ModuleLoader__` undefined | client 产物依赖 dsh 引导机制，组件测试在官方 CI 跑 |
| 6 | 简单任务"突然变快"的误判 | 1s vs 110s 差异被误归因 | DeepSeek context cache 命中也会提速——A/B 测试要用全新 prompt |
| 7 | 端口占用 | `dsh web` 起不来 | `netstat -ano | findstr 3080` 找 PID kill |

## 6.5 评测视角：官方成绩单 vs 独立实测

（结合 0813 正式版发布）看 Agent 模型成绩单要三问：
1. **谁测的**？官方自测（自家 Harness）vs 独立第三方（AA 等）
2. **什么 harness**？框架不同分数差很大（官方 Terminal-Bench 87.9 vs AA 独立 79）
3. **验证器多严**？宽松验证器（SWE-bench Verified 8.5% 假阳性）vs 严格（DeepSWE 0.3%）

dsh 的 `agent/request` waterfall 让模型跑分可复现——这是它相比闭源产品的工程优势。

---

**下一章**：[第 7 章：生态与资源](./07-ecosystem.md)（规划中）。
