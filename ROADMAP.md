# 🗺️ 路线图（ROADMAP）

> 公开计划 = 社区信任。所有条目按"已完成 / 进行中 / 规划中"三栏追踪，更新时保持本文件与 README 的"章节数"徽章同步。

## ✅ 已完成

| 条目 | 说明 | 佐证 |
|---|---|---|
| 12 章手册（中文） | 从 0 到 1：入门 → 开发 → 实战 → 生态 → 进阶，每章可运行、命令全实测 | [docs/](./docs/) |
| 英文版 | 前 10 章同步英文（EN 版 + 英文 PDF） | [docs/*.en.md](./docs/) |
| Benchmark 附录 | 同模型 × 3 Agent 实测（5 任务 × 3 轮中位数，45/45 全对） | [docs/benchmark.md](./docs/benchmark.md) |
| 快速上手资产 | 一页速查卡 / 插件模板 / 配置参考 / FAQ | [docs/cheatsheet.md](./docs/cheatsheet.md) 等 |
| 双语 README | 中文 README + 英文 README（README.en.md） | [README.md](./README.md) |
| 第 12 章 · 已知不足与边界 | rc 版诚实视角：不稳定性 / 生态早期 / 跨平台短板 | [docs/12-limitations.md](./docs/12-limitations.md) |
| PDF 专业排版 | 中文完整版（12 章节，3.2MB）+ 英文版 | 仓库根目录 `*.pdf` |
| llms.txt | 面向 LLM 的索引（llms.txt + llms-full.txt） | [llms.txt](./llms.txt) |

## 🚧 进行中

| 条目 | 内容 | 状态 |
|---|---|---|
| QC 核验轮次 | 对 12 章 + 附录逐一做链接健康检查 / 数据一致性 / 渲染检查（对照 README-REVIEW.md 遗留项） | 逐章推进中 |
| 官方讨论区推广 | 在 [deepseek-ai/deepseek-harness](https://github.com/deepseek-ai/deepseek-harness) Discussions 响应新手提问并同步白皮书内容（已响应 #380 插件踩坑 / #392 TUI examples / #118） | 每周 2-3 帖 |

## 🔭 规划中

| 条目 | 说明 | 优先级 |
|---|---|---|
| 插件模板扩展 | 在 [examples/plugin-template/](./examples/plugin-template/) 基础上补充更多可克隆模板（如 TUI / cost-tracker / MCP 接入） | P1 |
| 视频教程 | 将快速上手 / 插件开发拆成 3-5 分钟短视频（配文字稿，同步进正文） | P2 |
| 社区案例征集 | 公开征集真实使用案例，合入第 5 / 10 章（含耗时 / 产物 / 验证） | P1 |
| GitHub Actions CI | 链接健康检查 + Markdown 规范（中英空格 / 标题层级 / 代码块标注）自动校验，PR 强制过检 | P1 |

## 📌 更新规则

- 条目**完成**后，从对应栏移入"已完成"，并同步更新 README 徽章（章节数 / PDF 大小等）
- 进行中条目每周更新一次状态；规划中条目按优先级推进
- 重大变更（新增章节 / 结构调整）先提 Issue 讨论，再动手

> 想参与其中某项？见 [CONTRIBUTING.md](./CONTRIBUTING.md)。
