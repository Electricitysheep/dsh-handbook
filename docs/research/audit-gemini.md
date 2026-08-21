# DeepSeek Harness 白皮书 · 独立审计报告 (Audit Report)

> **审计员**：独立审计员 (Independent Auditor)  
> **审计日期**：2026-08-14  
> **审计基线版本**：dsh `0.1.0-rc.8` / deepseek-v4-flash-0731  
> **审计范围**（只读）：
> 1. `README.md`
> 2. `docs/02-quickstart.md`
> 3. `docs/06-advanced.md`
> 4. `docs/12-limitations.md`
> 5. `docs/07-ecosystem.md`
> 6. `README.en.md`  
> **报告输出目标**：`docs/research/audit-gemini.md`

---

## Executive Summary (审计执行摘要)

本审计报告对 `dsh-handbook` 白皮书项目的 6 个核心中英文档进行了深度静态代码与文本审计，重点审查**文字质量（Text Quality）**、**数据一致性（Data Consistency）**与**中英同步（Bilingual Synchronization）**三大核心维度。

### 整体审计结论 (Overall Verdict)
- **总体评级**：**良好 (Grade: B+)**
- **优势**：
  - 内容实操性极强，具备真实的工程细节（如 `cordis.patch.yml`、`agent/request` waterfall、Windows Hyper-V 端口冲突、UTF-16 0x00 截断等）。
  - 各章节结构设计规范（TL;DR、分节讲解、动手练习、FAQ、版本说明）。
  - 对 rc 预发布阶段的局限性有诚实的披露（第 12 章）。
- **主要问题**：
  1. **结构错位**：`docs/06-advanced.md` 将核心正文小节 6.6 错置于“动手练习”、“FAQ”和“下一章导航”之后。
  2. **交叉引用漂移**：`docs/07-ecosystem.md` 练习与 FAQ 内部引用的自查小节编号多处错位（偏离 1~2 节）。
  3. **中英脱节**：`README.en.md` 滞后于 `README.md`，遗漏了 8 个社区推荐插件表格、3 个 Discussions 联动帖、插件挂载实操命令以及推理档位官方 provider 关键限制说明。
  4. **数据冲突**：全书宣称的“对比 Agent 数量”（14 vs 6）、“案例数量”（8 vs 5）、“全书章节数”（11 vs 12）以及“Discussions 响应帖数”（5 vs 8）存在多处内部不一致。
  5. **排版语法瑕疵**：`README.md` 存在标题行与正文粘连（行 390 缺少换行）、Markdown 表格内管道符未转义、部分本地相对链接无效。

---

## 缺陷与优化统计 (Issue Metrics)

| 优先级 | 文字质量与排版 | 数据一致性 | 中英同步 | 合计 |
|:---|:---:|:---:|:---:|:---:|
| 🔴 **高优先级 (High)** | 2 | 2 | 2 | **6** |
| 🟡 **中优先级 (Medium)** | 3 | 3 | 2 | **8** |
| 🟢 **低优先级 (Low)** | 3 | 1 | 1 | **5** |
| **总计** | **8** | **6** | **5** | **19** |

---

## 🔴 高优先级问题 (High Priority Issues)
> **判定标准**：破坏 Markdown 渲染/页面结构错位、破坏命令执行/导致运行时错误、严重误导用户、关键技术说明缺失。

---

### [H-01] 标题行与上一行文字粘连导致 Markdown 标题渲染失效
- **文件**：`README.md`
- **位置**：第 390 行
- **维度**：文字质量 / Markdown 渲染
- **现状分析**：
  第 390 行末尾写为：
  ```markdown
  已在 [deepseek-ai/deepseek-harness](https://github.com/deepseek-ai/deepseek-harness) Discussions 回应 8 帖：#380 插件踩坑 / #401 Windows 路径 / #392 TUI 建议 / #384 visionDS / #118 / #655 社区五项目 / #735 token 成本 / #781 LSP 提议## 🙏 贡献与反馈
  ```
  二级标题 `## 🙏 贡献与反馈` 直接紧贴在“#781 LSP 提议”后面，缺少换行符。这会导致：
  1. GFM / CommonMark 解析器无法识别二级标题，将其作为普通文本渲染。
  2. 页面目录（TOC）、侧边栏导航和锚点链接 `#🙏-贡献与反馈` 完全失效。
- **具体修改建议**：
  在 `#781 LSP 提议` 之后插入一个空行，然后再输出二级标题：
  ```diff
  - 已在 [deepseek-ai/deepseek-harness](https://github.com/deepseek-ai/deepseek-harness) Discussions 回应 8 帖：#380 插件踩坑 / #401 Windows 路径 / #392 TUI 建议 / #384 visionDS / #118 / #655 社区五项目 / #735 token 成本 / #781 LSP 提议## 🙏 贡献与反馈
  + 已在 [deepseek-ai/deepseek-harness](https://github.com/deepseek-ai/deepseek-harness) Discussions 回应 8 帖：#380 插件踩坑 / #401 Windows 路径 / #392 TUI 建议 / #384 visionDS / #118 / #655 社区五项目 / #735 token 成本 / #781 LSP 提议
  + 
  + ## 🙏 贡献与反馈
  ```

---

### [H-02] 章节结构严重错位：6.6 节被放置在 FAQ 和“下一章”之后
- **文件**：`docs/06-advanced.md`
- **位置**：第 115 ~ 130 行
- **维度**：文字质量 / 文档结构
- **现状分析**：
  文档导航中列出：
  `- [6.6 缓存策略：让每次调用都更便宜](#66-缓存策略让每次调用都更便宜)`
  但实际物理排版顺序为：
  1. `## 6.5 评测视角：官方成绩单 vs 独立实测` (第 67 行)
  2. `## 动手练习（检验你是否真懂了）` (第 78 行)
  3. `## 常见疑问 FAQ` (第 93 行)
  4. `**下一章**：[第 7 章：生态与资源](./07-ecosystem.md)（规划中）。` (第 115 行)
  5. `## 6.6 缓存策略：让每次调用都更便宜` (第 117 行)
  
  **影响**：读者在看到“下一章”后往往停止阅读，导致 6.6 节的核心缓存优化方法论被遗漏，且违背了全书所有章节“正文 → 练习 → FAQ → 下一章”的统一步骤规范。
- **具体修改建议**：
  将 6.6 节完整移至 6.5 节之后、动手练习之前。同时修正第 115 行中“（规划中）”的不准确表述（第 7 章已完成）：
  ```markdown
  ## 6.5 评测视角：官方成绩单 vs 独立实测
  ...（原 6.5 内容）

  ## 6.6 缓存策略：让每次调用都更便宜
  第 5 章讲了高缓存命中率的价值（实测 97%、98% 折扣），这里给出**可操作策略**：

  | 目标 | 做法 |
  |---|---|
  | 提高命中 | 长任务**保持会话延续**（避免频繁新建会话） |
  | 提高命中 | 系统提示/技能目录等**前缀保持稳定**（不要频繁改配置） |
  | 提高命中 | 批量任务放同一会话/同前缀（如同一批文件分析） |
  | 降低成本 | 简单轮次用 `low` 档（思考 token 减少 → 总 token 下降） |
  | 监控 | 会话统计行看"缓存命中 %"（Web UI 底部）——低于预期就检查前缀稳定性 |

  **成本模型速记**：`总成本 ≈ 输出token×输出价 + 输入未命中×未命中价 + 输入命中×命中价`——Agent 工作负载输入占比高，**缓存命中率是成本的第一变量**。

  ---

  ## 动手练习（检验你是否真懂了）
  ...

  ## 常见疑问 FAQ
  ...

  ---

  **下一章**：[第 7 章：生态与资源](./07-ecosystem.md) —— 加入 dsh 生态的完整地图。
  ```

---

### [H-03] 章节自查小节编号大面积漂移（错位 1~2 节）
- **文件**：`docs/07-ecosystem.md`
- **位置**：第 234、237、239、260、261、264 行
- **维度**：文字质量 / 交叉引用
- **现状分析**：
  在编写 7.6 ~ 7.10 节时，由于小节插入/重新编号，文末的“动手练习”与“常见疑问 FAQ”中的自查定位未同步更新，导致全部指向错误章节：
  - 第 234 行（练习 4）：“参考本章 7.5 节两处改动的完整代码片段” → 实际代码在 **7.6 节**（7.5 节是“推荐阅读路径”）。
  - 第 237 行（练习 5）：“参考本章 7.3 节第 2 步” → 实际在 **7.4 节**（7.3 节是“插件生态快照”）。
  - 第 239 行（练习 6）：“参考本章 7.8 节时间线表格 + 7.9 节联动模式” → 实际时间线在 **7.9 节**，联动模式在 **7.10 节**。
  - 第 260 行（FAQ Q6）：“参考本章 7.4 节阅读路径” → 实际在 **7.5 节**。
  - 第 261 行（FAQ Q7）：“Q7：7.5 节的 `link:` 路径...” → 实际在 **7.6 节**。
  - 第 264 行（FAQ Q8）：“参考 7.9 节 3 个原则” → 实际在 **7.10 节**。
- **具体修改建议**：
  逐行校准小节自查锚点：
  ```diff
  - 4. **动手题**：按本章 7.5 节的步骤，完整挂载 `DSH-better-sidebar`...
  -    > 自查：参考本章 7.5 节两处改动的完整代码片段
  + 4. **动手题**：按本章 7.6 节的步骤，完整挂载 `DSH-better-sidebar`...
  +    > 自查：参考本章 7.6 节两处改动的完整代码片段

  - 5. **动手题**：给 `DSH-better-sidebar` 或自己写的提速插件的 README 提一个改进 PR...
  -    > 自查：参考本章 7.3 节第 2 步 + 第 5 章案例的 PR 范式
  + 5. **动手题**：给 `DSH-better-sidebar` 或自己写的提速插件的 README 提一个改进 PR...
  +    > 自查：参考本章 7.4 节第 2 步 + 第 5 章案例的 PR 范式

  - 6. **思考题**：本章 7.8 节时间线显示...
  -    > 自查：参考本章 7.8 节时间线表格 + 7.9 节联动模式
  + 6. **思考题**：本章 7.9 节时间线显示...
  +    > 自查：参考本章 7.9 节时间线表格 + 7.10 节联动模式

  - Q6：...参考本章 7.4 节阅读路径。
  + Q6：...参考本章 7.5 节阅读路径。

  - **Q7：7.5 节的 `link:` 路径在 Windows 和 macOS 下写法一样吗？**
  + **Q7：7.6 节的 `link:` 路径在 Windows 和 macOS 下写法一样吗？**

  - Q8：...参考 7.9 节 3 个原则：...
  + Q8：...参考 7.10 节 3 个原则：...
  ```

---

### [H-04] 英文版缺失官方 provider 不支持 `low` 档位的严重限制说明
- **文件**：`README.en.md`
- **位置**：第 283 行
- **维度**：中英同步 / 技术准确性
- **现状分析**：
  在 `README.md` 第 311~315 行和 `docs/02-quickstart.md` 第 137 行中均有重要核验提示：
  > 官方 DeepSeek 适配器（`llm-deepseek`，默认 `provider=deepseek-official`）仅接受 `off` / `high` / `max` 三档，配置为 `low` 会直接抛出 `UNSUPPORTED_REASONING_EFFORT` 异常；`low` 是 `pi-ai`（opencode-go）等第三方网关档位。
  
  但在 `README.en.md` 第 283 行：
  ```yaml
  agent-default-model:
    model: deepseek-v4-flash    # or deepseek-v4-pro
    reasoningEffort: high       # low / high / max
  ```
  英文版未包含此关键技术约束，用户按英文说明将 `reasoningEffort` 改为 `low` 会导致启动或请求抛错崩溃。
- **具体修改建议**：
  在 `README.en.md` 的配置示例中对齐中文版的注释与警告：
  ```diff
    agent-default-model:
      model: deepseek-v4-flash    # or deepseek-v4-pro
  -   reasoningEffort: high       # low / high / max
  +   reasoningEffort: high       # off (fastest/no thinking) / high (default) / max (strongest)
  +                               # Note: 'low' is only for custom gateways (pi-ai); official adapter uses 'off'
  ```

---

### [H-05] 英文版 README 遗漏社区插件推荐表与讨论区关键联动
- **文件**：`README.en.md`
- **位置**：第 334 ~ 340 行
- **维度**：中英同步
- **现状分析**：
  - `README.md` 第 373~386 行收录了完整的 **社区插件推荐表**（精选 8 个核心插件：`dsh-specflow`、`dsh-gitflow`、`dsh-guardian`、`dsh-code-intel`、`dsh-tianshu-tui`、`dsh-computer-use`、`dsh-data-agent`、`dsh-balance-meter`），并附带了 GitHub 链接与功能说明。
  - `README.md` 第 390 行包含了 8 个官方 Discussions 联动帖（新增了 `#655`、`#735`、`#781`）。
  - `README.en.md` 对应位置完全缺失该插件推荐表，且 Discussions 仅列出 5 个，遗漏了 3 个关键讨论帖。
- **具体修改建议**：
  将社区插件推荐表与全部 8 个 Discussions 讨论帖完整同步翻译至 `README.en.md`：
  ```markdown
  ### 🧩 Recommended Community Plugins (from Official Discussions / [awesome-dsh-plugin](https://github.com/awesome-dsh-plugin/awesome-dsh-plugin))

  | Plugin | Description |
  |---|---|
  | [dsh-specflow](https://github.com/lonelymoon87/dsh-specflow) | Spec-driven development: skills, commands, target tracking, progress context |
  | [dsh-gitflow](https://github.com/lonelymoon87/dsh-gitflow) | Approval-gated Git workflows (status/diff/commit/branch) |
  | [dsh-guardian](https://github.com/lonelymoon87/dsh-guardian) | Guardrails: dangerous operation policy check + output sanitization |
  | [dsh-code-intel](https://github.com/lonelymoon87/dsh-code-intel) | Tree-sitter code symbol indexing + hybrid search |
  | [dsh-tianshu-tui](https://github.com/huiliyi37/dsh-tianshu-tui) | Terminal UI (TUI) for dsh |
  | [dsh-computer-use](https://github.com/Anionex/dsh-computer-use) | Accessibility-first macOS computer control |
  | [dsh-data-agent](https://github.com/omdsh-dev/dsh-data-agent) | Database connection & SQL-writing agent |
  | [dsh-balance-meter](https://github.com/Ghost011118/dsh-balance-meter) | Real-time balance and session cost tracking |

  > Full list at [awesome-dsh-plugin](https://github.com/awesome-dsh-plugin/awesome-dsh-plugin) (122+ plugins).
  ```

---

### [H-06] 全书章节数、案例数与对比 Agent 数量在主页与正文中冲突
- **文件**：`README.md`、`README.en.md`、`docs/07-ecosystem.md`
- **位置**：`README.md` 行 75/77；`README.en.md` 行 69/71；`docs/07-ecosystem.md` 行 198
- **维度**：数据一致性
- **现状分析**：
  1. **对比 Agent 数量**：`README.md` 第 75 行宣称“**14 个主流 Agent 对比**”，但第 333 行能力矩阵表格中只列出了 **6 个**（dsh、Claude Code、OpenAI Codex、OpenCode、Gemini CLI、Kimi CLI）；`README.en.md` 第 69 行写为“**6-agent comparison**”。
  2. **案例数量**：`README.md` 第 77 行宣称“**8 个真实复杂案例**”，而 `README.en.md` 第 71 行写为“**5 real complex cases**”，实际全书正文为第 5 章（3 个 PR 案例）+ 第 10 章（2 个端到端复杂案例）= 5 个案例。
  3. **章节总数**：`docs/07-ecosystem.md` 第 198 行写为“**11 章中文教程**”，而 `README.md` 徽章和目录均明确为 **12 章节**（增加了第 12 章《已知不足与边界》）。
- **具体修改建议**：
  统一全部主页宣传数据与正文一致：
  - `README.md` 第 75 行改为：`6 个主流 Agent 对比（表格+文字）+ 同模型实测 benchmark`。
  - `README.md` 第 77 行改为：`5 个真实复杂案例（含耗时/产物/验证）`。
  - `docs/07-ecosystem.md` 第 198 行改为：`12 章中文教程 + Benchmark + 插件模板`。

---

## 🟡 中优先级问题 (Medium Priority Issues)
> **判定标准**：破坏外部链接可达性、缺失关键操作命令、术语不规范、表述自相矛盾。

---

### [M-01] `README.md` 内部使用相对路径链接 GitHub Discussions 导致 404
- **文件**：`README.md`
- **位置**：第 386 行、第 393 行
- **维度**：文字质量 / 链接健康
- **现状分析**：
  第 386 行和第 393 行包含链接 `[社区案例征集](./discussions/12)`。
  `./discussions/12` 是相对路径，在本地文件系统或 Docsify / GitHub Pages 静态文档站点中，该路径会被解析为本地不存在的文件路径 `.../docs/discussions/12`，导致 404 错误。
- **具体修改建议**：
  替换为完整的 GitHub 官方 Discussions URL：
  ```diff
  - > 完整列表见 [awesome-dsh-plugin](https://github.com/awesome-dsh-plugin/awesome-dsh-plugin)（122+ 插件）。想被收录？[社区案例征集](./discussions/12)
  + > 完整列表见 [awesome-dsh-plugin](https://github.com/awesome-dsh-plugin/awesome-dsh-plugin)（122+ 插件）。想被收录？[社区案例征集](https://github.com/Electricitysheep/dsh-handbook/discussions/12)
  ```
  （第 393 行同理替换）。

---

### [M-02] `README.en.md` 插件模板缺失关键运行与挂载命令
- **文件**：`README.en.md`
- **位置**：第 268 ~ 275 行
- **维度**：中英同步 / 实操完整性
- **现状分析**：
  中文版 `README.md` 在“🔧 插件模板”中包含关键的安装启动命令：
  ```bash
  cd ~/.dsh/profiles/web && pnpm install && dsh web
  ```
  而在英文版 `README.en.md` 中，只给出了 `package.json` 和 `cordis.patch.yml` 的代码片段，漏掉了这一行终端执行命令，导致英文读者修改完配置后不知道下一步需要进入 profile 目录执行 `pnpm install`。
- **具体修改建议**：
  在 `README.en.md` 第 273 行后补充该命令：
  ```diff
    - insert:
        - id: my-plugin
          name: my-plugin
    ```
  + ```bash
  + cd ~/.dsh/profiles/web && pnpm install && dsh web
  + ```
    > Clone-and-run template (pure functions + waterfall + tests): [examples/plugin-template/](./examples/plugin-template/README.md)
  ```

---

### [M-03] `docs/07-ecosystem.md` 响应 Discussions 帖数与 README 不一致
- **文件**：`docs/07-ecosystem.md`
- **位置**：第 206 行
- **维度**：数据一致性
- **现状分析**：
  `docs/07-ecosystem.md` 第 206 行写道：“本白皮书已在官方 Discussions 响应 **5 帖**”（表格仅列出 #380, #392, #401, #384, #118）。
  而 `README.md` 第 390 行明确更新为 **8 帖**（增加了 #655 社区五项目、#735 token 成本、#781 LSP 提议）。
- **具体修改建议**：
  在 `docs/07-ecosystem.md` 7.10 节表格中补充 3 个新增帖，并将总数更新为 8 帖：
  ```diff
  - 本白皮书已在官方 Discussions 响应 5 帖，以下是**有效参与的实例**：
  + 本白皮书已在官方 Discussions 响应 8 帖，以下是**有效参与的实例**：
  ```
  在表格中追加：
  ```markdown
  | [#655](https://github.com/deepseek-ai/deepseek-harness/discussions/655) | 社区五项目 | 梳理生态全景进第 7 章 7.3 节 | 整合碎片项目 → 形成生态地图 |
  | [#735](https://github.com/deepseek-ai/deepseek-harness/discussions/735) | token 成本 | 沉淀进第 6 章 6.6 节成本模型 | 成本测算 → 公式化沉淀 |
  | [#781](https://github.com/deepseek-ai/deepseek-harness/discussions/781) | LSP 提议 | 记录进第 11 章未来展望 | 前瞻特性 → 跟踪架构演进 |
  ```

---

### [M-04] `docs/02-quickstart.md` TL;DR 与动手练习未提示 `off` 档位
- **文件**：`docs/02-quickstart.md`
- **位置**：第 9 行、第 249 行
- **维度**：文字质量 / 逻辑严密性
- **现状分析**：
  第 2.3 节第 137 行的注记已清晰说明“官方适配器只接受 `off` / `high` / `max`，`low` 会抛 `UNSUPPORTED_REASONING_EFFORT`”。
  但第 9 行 TL;DR 仍写“推理档位三档：low（最快）/ high（默认）/ max（最强）”，且第 249 行练习 4 要求读者“把 settings.yaml 的 `reasoningEffort` 改为 `low`”。如果读者使用的是官方 API，执行练习 4 将直接遭遇报错。
- **具体修改建议**：
  在 TL;DR 和练习 4 中增加说明：
  - 第 9 行修改为：`3. **推理档位三档**：off / low（关闭或弱思考/最快，官方 provider 用 off，网关用 low）/ high（默认）/ max（最强）`。
  - 第 249 行修改为：`4. **推理档位实验**：把 settings.yaml 的 reasoningEffort 改为 off（官方 provider）或 low（第三方网关），重新跑一个简单任务，感受速度差异`。

---

### [M-05] 缓存折扣率与命中率表述在各章节细节存在歧义
- **文件**：`README.md`、`docs/06-advanced.md`、`README.en.md`
- **位置**：`README.md` 行 70, 325；`docs/06-advanced.md` 行 119；`README.en.md` 行 293
- **维度**：数据一致性
- **现状分析**：
  - `README.md` 行 70 内部注释指出：“缓存命中率实测为 97%，99% 是 Pro 档缓存折扣（99%+）”。
  - `README.md` 行 325 FAQ 指出：“缓存命中 98% 折扣，实测命中率 97%”。
  - `docs/06-advanced.md` 行 119 指出：“实测 97%、98% 折扣”。
  - 差异原因在于：DeepSeek 官方定价中，Flash 模型的 Context Cache 命中折扣为 98%（0.002 / 0.0004），Pro 模型的 Cache 命中折扣为 99%+（0.008 / 0.00016）。混写“98% 折扣”或“99% 折扣”未标明模型档位时容易引起读者困惑。
- **具体修改建议**：
  统一在正文明确模型对应关系：如标注“Flash 档 98% 缓存折扣 / Pro 档 99% 缓存折扣，实测会话缓存命中率达 97%”。

---

### [M-06] `README.en.md` 英文版缺失“社区案例征集”行动呼吁 (CTA)
- **文件**：`README.en.md`
- **位置**：第 340 ~ 345 行
- **维度**：中英同步
- **现状分析**：
  中文版 `README.md` 在“🙏 贡献与反馈”中设有专门的高亮投稿通道：
  `- 📝 **跑过真实案例？** 投稿收录进白皮书（署名 + 季度精选 PDF）：[社区案例征集](...)`
  英文版 `README.en.md` 仅有 3 条简略的通用贡献提示，缺失了这一面向海外社区的关键用户案例收集入口。
- **具体修改建议**：
  在 `README.en.md` 的 Contribute 章节中补齐：
  ```diff
    ## 🙏 Contribute

    - ⭐ Found it useful? Star it — it drives continued updates
  + - 📝 **Run a real case?** Submit it to be featured in the handbook (with author credit + quarterly curated PDF): [Community Case Submissions](https://github.com/Electricitysheep/dsh-handbook/discussions/12)
    - Commands broken? rc releases iterate fast — open an issue
  ```

---

### [M-07] `docs/12-limitations.md` 与主页版本信息的互引强化
- **文件**：`docs/12-limitations.md`
- **位置**：第 139 行
- **维度**：文字质量 / 链接指引
- **现状分析**：
  第 139 行写道：“先跑一遍 [roadmap 学习路径](./roadmap.md) 的验收标准”。
  虽然该相对路径在 `docs/` 下有效，但建议同时提示读者参考 [附录速查卡](./cheatsheet.md) 快速验证本地基础命令。
- **具体修改建议**：
  扩展为：`先跑一遍 [roadmap 学习路径](./roadmap.md) 与 [速查卡](./cheatsheet.md) 的验收标准`。

---

### [M-08] 英文 PDF 规格描述与主页徽章的潜在矛盾
- **文件**：`README.en.md`
- **位置**：第 17 行、第 331~333 行
- **维度**：数据一致性 / 中英同步
- **现状分析**：
  - `README.en.md` 顶部徽章写着 `![chapters](https://img.shields.io/badge/chapters-12-green)`。
  - 但在 `README.md` 第 366 行明确说明英文 PDF 为 10 章（`DeepSeek-Harness-Handbook.pdf（10 章，54k 字符）`）。
  - `README.en.md` 第 332 行只有链接 `[DeepSeek-Harness-Handbook.pdf](./DeepSeek-Harness-Handbook.pdf)`，未注明英文 PDF 的具体章节和字符体量。
- **具体修改建议**：
  在 `README.en.md` 第 332 行补充具体规格说明：
  ```diff
  - - **English full edition**: [DeepSeek-Harness-Handbook.pdf](./DeepSeek-Harness-Handbook.pdf)
  + - **English edition**: [DeepSeek-Harness-Handbook.pdf](./DeepSeek-Harness-Handbook.pdf) (10 chapters, ~54k chars; web doc covers all 12 chapters)
  ```

---

## 🟢 低优先级问题 (Low Priority Issues)
> **判定标准**：排版格式、转义字符规范、微小语法瑕疵、中英文混排空格优化。

---

### [L-01] Markdown 表格内未转义管道符 `|`
- **文件**：`docs/06-advanced.md`
- **位置**：第 65 行
- **维度**：文字质量 / Markdown 排版规范
- **现状分析**：
  在第 6.4 节排障表格中：
  `| 7 | 端口占用 | dsh web 起不来 | netstat -ano | findstr 3080 找 PID kill |`
  其中的 `netstat -ano | findstr 3080` 包含未转义的管道符 `|`，在严格模式的 Markdown 解析器中会破坏列解析。而在 `docs/02-quickstart.md` 第 233 行中正确采用了转义 `\|`。
- **具体修改建议**：
  转义管道符或加反引号：
  ```diff
  - | 7 | 端口占用 | `dsh web` 起不来 | `netstat -ano | findstr 3080` 找 PID kill |
  + | 7 | 端口占用 | `dsh web` 起不来 | `netstat -ano \| findstr 3080` 找 PID kill |
  ```

---

### [L-02] `docs/07-ecosystem.md` 行首多余空格导致缩进异常
- **文件**：`docs/07-ecosystem.md`
- **位置**：第 158 行
- **维度**：文字质量 / 排版
- **现状分析**：
  第 158 行为：
  ` 发一个"创建 3 个文件"的任务，观察日志是否出现...`
  行首有一个无序前导空格，且缺少列表序号 `④` 或 `-`，与上方的 `①`、`②`、`③` 步骤排版不匹配。
- **具体修改建议**：
  统一加上序号 `④`：
  ```diff
  -  发一个"创建 3 个文件"的任务，观察日志是否出现 `[speed-plugin] calls=[...] => reasoningEffort=low`（参考第 4 章 4.5 节）。
  + **④ 验证效果**：发一个"创建 3 个文件"的任务，观察日志是否出现 `[speed-plugin] calls=[...] => reasoningEffort=low`（参考第 4 章 4.5 节）。
  ```

---

### [L-03] YAML 路径反斜杠转义缺失
- **文件**：`docs/07-ecosystem.md`
- **位置**：第 262 行 (FAQ Q7)
- **维度**：文字质量 / 代码精确性
- **现状分析**：
  FAQ Q7 解答中写为：`Windows 用反斜杠（link:C:\path\to\plugin）`。
  由于 `\p` 和 `\t` 在 JSON/YAML 中可能被解析为转义序列（`\t` 变为制表符），全书其他位置（如 `README.md` 行 296、`02-quickstart.md` 行 175、`07-ecosystem.md` 行 111）均已统一修正为 `link:C:\\path\\to\\plugin`。
- **具体修改建议**：
  统一转义为双反斜杠：
  ```diff
  - 不一样。Windows 用反斜杠（`link:C:\path\to\plugin`），macOS/Linux 用正斜杠（`link:/path/to/plugin`）。
  + 不一样。Windows 用双反斜杠转义（`link:C:\\path\\to\\plugin`），macOS/Linux 用正斜杠（`link:/path/to/plugin`）。
  ```

---

### [L-04] Windows PowerShell 终端路径波浪号 `~` 展开提示
- **文件**：`docs/02-quickstart.md`
- **位置**：第 183 行
- **维度**：文字质量 / 跨平台兼容
- **现状分析**：
  第 183 行给出命令：`cd ~/.dsh/profiles/web && pnpm install`。
  在 Windows 原生 `cmd.exe` 下不支持 `~` 展开（会报找不到路径），虽然 PowerShell 和 Git Bash 支持，但白皮书在 Windows 下作为推荐环境，建议加一条小提示或标注。
- **具体修改建议**：
  在代码块上方或注释中补充说明：`(Windows cmd 请使用 cd %USERPROFILE%\.dsh\profiles\web)`。

---

### [L-05] 英文版标题大小写规范 (Title Case Consistency)
- **文件**：`README.en.md`
- **位置**：第 27, 46, 63, 229, 250 行
- **维度**：文字质量 / 英文规范
- **现状分析**：
  英文版二级标题存在 Sentence case 与 Title case 混用现象：
  - `## 🚀 30-second quickstart` (小写) vs `## 📚 Table of contents`
  - `## 🎯 What this is` vs `## 🧰 Quick assets`
- **具体修改建议**：
  保持全篇统一为 Title Case：
  - `## 🚀 30-Second Quickstart`
  - `## 🎯 What Is DeepSeek Harness`
  - `## 🎁 What You Get`
  - `## 📚 Table of Contents`
  - `## 🧰 Quick Assets`

---

## 分文件优化实施清单 (File-by-File Action Matrix)

为便于维护团队精准修改，以下按文件整理所有待修改行号与操作：

### 1. `README.md`
| 行号 | 优先级 | 修改项 | 对应条目 |
|:---|:---:|:---|:---:|
| 75 | 🔴 高 | 将 `14 个主流 Agent 对比` 改为 `6 个主流 Agent 对比` | [H-06] |
| 77 | 🔴 高 | 将 `8 个真实复杂案例` 改为 `5 个真实复杂案例` | [H-06] |
| 386 | 🟡 中 | 将 `./discussions/12` 改为完整 GitHub Discussions URL | [M-01] |
| 390 | 🔴 高 | 在 `#781 LSP 提议` 与 `## 🙏 贡献与反馈` 之间添加空行换行 | [H-01] |
| 393 | 🟡 中 | 将 `./discussions/12` 改为完整 GitHub Discussions URL | [M-01] |

### 2. `docs/06-advanced.md`
| 行号 | 优先级 | 修改项 | 对应条目 |
|:---|:---:|:---|:---:|
| 65 | 🟢 低 | 转义表格内管道符：`netstat -ano \| findstr 3080` | [L-01] |
| 115 | 🔴 高 | 去掉“（规划中）”：改为指向已有的 `07-ecosystem.md` | [H-02] |
| 117-130 | 🔴 高 | 将 6.6 节整体移动到 6.5 节之后、动手练习之前 | [H-02] |

### 3. `docs/07-ecosystem.md`
| 行号 | 优先级 | 修改项 | 对应条目 |
|:---|:---:|:---|:---:|
| 158 | 🟢 低 | 补充序号 `**④ 验证效果**：` 并去除行首多余空格 | [L-02] |
| 198 | 🔴 高 | 将 `11 章中文教程` 改为 `12 章中文教程` | [H-06] |
| 206 | 🟡 中 | 将 `响应 5 帖` 改为 `响应 8 帖` 并补齐 3 个讨论帖 | [M-03] |
| 234 | 🔴 高 | 练习 4 自查定位由 7.5 节修正为 **7.6 节** | [H-03] |
| 237 | 🔴 高 | 练习 5 自查定位由 7.3 节修正为 **7.4 节** | [H-03] |
| 239 | 🔴 高 | 练习 6 自查定位由 7.8/7.9 节修正为 **7.9/7.10 节** | [H-03] |
| 260 | 🔴 高 | FAQ Q6 引用由 7.4 节修正为 **7.5 节** | [H-03] |
| 261 | 🔴 高 | FAQ Q7 标题由 7.5 节修正为 **7.6 节** | [H-03] |
| 262 | 🟢 低 | 将 `link:C:\path\to\plugin` 修正为转义路径 `link:C:\\path\\to\\plugin` | [L-03] |
| 264 | 🔴 高 | FAQ Q8 引用由 7.9 节修正为 **7.10 节** | [H-03] |

### 4. `docs/02-quickstart.md`
| 行号 | 优先级 | 修改项 | 对应条目 |
|:---|:---:|:---|:---:|
| 9 | 🟡 中 | TL;DR 中补充 `off` 档位与官方适配器差异说明 | [M-04] |
| 183 | 🟢 低 | 补充 Windows cmd 下路径提示说明 | [L-04] |
| 249 | 🟡 中 | 练习 4 明确官方 provider 使用 `off`、网关使用 `low` | [M-04] |

### 5. `docs/12-limitations.md`
| 行号 | 优先级 | 修改项 | 对应条目 |
|:---|:---:|:---|:---:|
| 139 | 🟡 中 | 在引用 roadmap 处补充 cheatsheet 速查链接 | [M-07] |

### 6. `README.en.md`
| 行号 | 优先级 | 修改项 | 对应条目 |
|:---|:---:|:---|:---:|
| 27, 46... | 🟢 低 | 统一二级标题英文大小写规范为 Title Case | [L-05] |
| 273 | 🟡 中 | 在插件模板后补充 `cd ~/.dsh/profiles/web && pnpm install && dsh web` | [M-02] |
| 283 | 🔴 高 | 补充 `off` 档位注释及官方 provider 不支持 `low` 的警告 | [H-04] |
| 332 | 🟡 中 | 补充英文版 PDF 规格（10 chapters, ~54k chars） | [M-08] |
| 334-340 | 🔴 高 | 补充 8 个社区推荐插件表格与 3 个缺失的 Discussions 帖号 | [H-05] |
| 340-345 | 🟡 中 | 补充英文版“Community Case Submissions”投稿通道 | [M-06] |

---

## 结论与复审建议 (Conclusion & Verification)

`dsh-handbook` 白皮书在内容质量、架构透视和实操避坑方面具备极高的实用价值。上述发现的问题主要源于快速迭代中的小节拆分与中英异步更新，未涉及底层技术逻辑硬伤。

建议维护团队按以下顺序完成修复与验收：
1. **第一阶段（即时修复）**：修复 `README.md` 的粘连标题 [H-01]、`06-advanced.md` 的 6.6 结构错位 [H-02] 与 `07-ecosystem.md` 的交叉引用漂移 [H-03]。
2. **第二阶段（中英对齐）**：补齐 `README.en.md` 缺失的插件表格 [H-05]、运行命令 [M-02] 与 provider 参数注释 [H-04]。
3. **第三阶段（数据校准）**：全仓统一章节数（12 章）、案例数（5 个）、对比 Agent 数量（6 个）与 Discussions 响应帖数（8 帖）[H-06, M-03]。
