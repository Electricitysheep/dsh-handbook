# 同类 handbook 竞品差距分析（2026-08-13）

> 调研方式：对比 8 个高 star 标杆 README（build-your-own-x 380k / system-design-primer 310k / the-art-of-command-line 150k / awesome-deepseek-agent 官方同源 / claude-code / langchain / awesome-ai-agents / free-programming-books）+ 2026 README 元分析（n=100+）。调研时仓库 16 stars。

## 元数据基准（10k+ stars vs <10 stars）

| 指标 | 10k+ stars | <10 stars |
|---|---|---|
| 有 screenshot/GIF | 89% | 12% |
| 一行安装 | 94% | 34% |
| 快速上手 <5 行 | 91% | 23% |
| 徽章 | 78% | 15% |

**star 增长关联度排序**：Hero 图（+35%）> 快速上手代码 > Demo GIF > 徽章 > FAQ。Star History 图单独 +15%。

## 8 大差距与落地状态

| # | 差距 | 标杆做法 | 落地状态 |
|---|---|---|---|
| 1 | 首屏缺视觉资产 | system-design-primer 架构图 / claude-code demo GIF / awesome 横向图 | ⚠️ 部分：banner.svg 已有；Mermaid 图用户反馈不美观已移除；无 GIF |
| 2 | 缺徽章 + GitHub About | langchain 徽章行 + topics + description | ✅ 已落地（stars/release/license + 12 topics + description） |
| 3 | 缺英文 README | system-design-primer 16 语言切换条 / awesome 中英分离 | ✅ 已有 README.en.md |
| 4 | 缺 5 分钟快速上手 | claude-code 3 步 / langchain quickstart | ✅ 已有"快速体验（30 秒）" |
| 5 | 缺架构图/Mermaid | GitHub 原生 Mermaid | ❌ 用户明确不要（不美观） |
| 6 | 缺社区运营 | claude-code Discord / ROADMAP / CONTRIBUTING / Good First Issue | ⚠️ 部分：discussions 已开 + 官方库 3 帖响应；无 CONTRIBUTING/ROADMAP |
| 7 | 缺 llms.txt + Topics | llmstxt.org 标准 | ✅ 已落地（llms.txt + llms-full.txt） |
| 8 | 缺 Used by / 社会证明 | awesome logo 墙 / langchain 案例 | ⚠️ 部分：生态联动区有 2 个真实项目 |
| 9 | 缺 Star History badge | star-history.com SVG | ❌ 未加（+15% star 转化） |
| 10 | 缺 GitHub 原生警告框 | claude-code `> [!WARNING]` | ✅ 已落地（rc 版本警告） |

## 标杆可复用设计（摘要）

- **awesome-deepseek-agent**（同源官方）：中英切换条 + 第一屏对照表 + 官方资源出口——"用户带着工具名来"设计
- **system-design-primer**：首屏 16 语言切换 + Motivation 三问 + Study Guide 时间分档表 + Anki 闪卡
- **build-your-own-x**：首屏 Banner + 名人名言钩子 + 可机扫统一格式
- **the-art-of-command-line**：首屏 ASCII 艺术 + 17 语言 + 承认不完美（信任建立）
- **claude-code**：demo GIF + 4 安装方式平铺 + 原生警告框 + Discord

## 下一步建议（按 ROI）

1. ✅ 加 Star History badge（一行）
2. ✅ 写 CONTRIBUTING.md + ROADMAP.md（社区运营）
3. ✅ 强化"Used by / 生态联动"区
4. ⏳ Demo GIF（可选，长尾）
5. ⏳ 官方库讨论区持续响应（每周 2-3 帖）
