# 反馈沉淀日志（Feedback Log）

> 记录官方库讨论区反馈 → 白皮书的沉淀历史。新条目加在顶部。
> 流水线说明见 [feedback-pipeline.md](./feedback-pipeline.md)

## 2026-08-14 轮（首轮，含历史沉淀）

| 来源帖 | 分类 | 沉淀位置 | 状态 |
|---|---|---|---|
| [#380](https://github.com/deepseek-ai/deepseek-harness/discussions/380) 插件六坑 | 章节补充 + 作者授权 | FAQ 六坑收录（致谢作者）；第 3 章依赖线锁坑 | ✅ 已沉淀（PR #27） |
| [#380](https://github.com/deepseek-ai/deepseek-harness/discussions/380) 免装 Node 安装包 | 章节补充（作者提供） | 第 2 章安装方式加免 Node 选项 | ✅ 已沉淀（PR #27） |
| [#1169](https://github.com/deepseek-ai/deepseek-harness/discussions/1169) dsh-usage | 生态收录（作者授权） | 第 14 章工具推荐 + 生态章节 | ✅ 已沉淀（PR #27） |
| [#118](https://github.com/deepseek-ai/deepseek-harness/discussions/118) 子代理模型缺口 | 章节补充（社区反馈） | 第 9 章已知限制标注 | ✅ 已沉淀（PR #27） |
| [#113](https://github.com/deepseek-ai/deepseek-harness/discussions/113) 等 --expose-internals 家族 | FAQ 候选 | FAQ 已收录（多帖合并） | ✅ 已沉淀 |
| [#725](https://github.com/deepseek-ai/deepseek-harness/discussions/725) unknown tool "" | FAQ 候选 | FAQ 已收录（根因） | ✅ 已沉淀 |
| [#159](https://github.com/deepseek-ai/deepseek-harness/discussions/159) fs-sandbox 竞态 | 章节补充 | 第 12/13 章引用 | ✅ 已沉淀 |
| [#817](https://github.com/deepseek-ai/deepseek-harness/discussions/817) 安全审计 | 章节补充 | 第 13 章安全基线引用 | ✅ 已沉淀 |
| [#655](https://github.com/deepseek-ai/deepseek-harness/discussions/655) 社区五项目 | 生态收录 | 生态章节社区资产清单 | ✅ 已沉淀 |
| [#589](https://github.com/deepseek-ai/deepseek-harness/discussions/589) 端口保留区间 | 章节补充 | 第 12 章 Windows 速查表 | ✅ 已沉淀 |
| [#735](https://github.com/deepseek-ai/deepseek-harness/discussions/735) 每轮 token | 章节补充 | 第 14 章测量方法（关联 dsh-usage） | ✅ 已沉淀 |
| [#1153](https://github.com/deepseek-ai/deepseek-harness/discussions/1153) / [#1269](https://github.com/deepseek-ai/deepseek-harness/discussions/1269) 视觉方案 | 生态收录 | 生态章节（视觉桥家族） | ✅ 已沉淀 |
| [#681](https://github.com/deepseek-ai/deepseek-harness/discussions/681) 安全开关插件 | 生态收录 + 章节呼应 | 生态章节 + 第 13 章审计理念 | ✅ 已沉淀 |

## 2026-08-14 轮（第二轮：他人回复需求）

| 来源帖 | 分类 | 沉淀位置 | 状态 |
|---|---|---|---|
| [#118](https://github.com/deepseek-ai/deepseek-harness/discussions/118) WSL2 安装 | 章节补充 | 第 2 章 WSL 安装注意 | ✅ 已沉淀（PR #31） |
| [#725](https://github.com/deepseek-ai/deepseek-harness/discussions/725) unknown tool null 根因 | FAQ 深化 | FAQ + typeof 校验 workaround | ✅ 已沉淀（PR #31） |
| [#1052](https://github.com/deepseek-ai/deepseek-harness/discussions/1052) PTC 模式 | 章节补充 | 第 8 章 | ✅ 已沉淀（PR #31） |
| [#1052](https://github.com/deepseek-ai/deepseek-harness/discussions/1052) KVCache 前缀缓存规则 | 章节补充（weijiafu14 分析） | 第 14 章缓存机制 | ✅ 已沉淀（PR #31） |
| [#1052](https://github.com/deepseek-ai/deepseek-harness/discussions/1052) 记忆/压缩生态 | 生态收录 | 第 14 章 + 生态章节（dsh-sgme/pi-quiet-tools） | ✅ 已沉淀（PR #31） |
| [#735](https://github.com/deepseek-ai/deepseek-harness/discussions/735) provider/model 标识 | 章节补充 | 第 14 章测量方法 | ✅ 已沉淀（PR #31） |
| [#380](https://github.com/deepseek-ai/deepseek-harness/discussions/380) dsh-installers | 生态收录（作者提供） | 生态章节 | ✅ 已沉淀（PR #31） |

## 2026-08-14 轮（第三轮：高价值技术线索）

| 来源帖 | 分类 | 沉淀位置 | 状态 |
|---|---|---|---|
| [#739](https://github.com/deepseek-ai/deepseek-harness/discussions/739) 推理模式 reasoning 序列化 | 章节补充（根因确认） | 第 6 章推理档位坑位 | ✅ 已沉淀（PR #33） |
| [#1420](https://github.com/deepseek-ai/deepseek-harness/discussions/1420) Windows 转发空格路径 | 章节补充（runPlugin shell:true） | 第 3 章 Windows 坑位 | ✅ 已沉淀（PR #33） |
| [#1476](https://github.com/deepseek-ai/deepseek-harness/discussions/1476) run_code 异步回调丢弃 | 章节补充（执行模型） | 第 8 章工具链坑位 | ✅ 已沉淀（PR #33） |

## 待沉淀（下周轮次）

| 来源帖 | 分类 | 计划 |
|---|---|---|
| （每周五扫描填充） | | |
