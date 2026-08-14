# 第 13 章：安全与沙箱模型

> 本章目标：看懂 dsh 的安全骨架——沙箱管什么、权限怎么分级、审批怎么放行——以及社区审计发现的真实边界。**这是从"能跑"到"敢上生产"的关键一章。**

## TL;DR（本章核心，30 秒版）

1. **三层防线**：沙箱（在哪执行）→ 权限预设（能做什么）→ 审批（危险动作要不要人点头）——默认不是裸执行
2. **沙箱只管文件效果**：`read-only` / `workspace-write` / `danger-full-access` 三档；网络与进程可见性不在词汇表内（所以 `taskkill` 杀宿主等案例是"词汇表外"，不是沙箱失守）
3. **权限 = 两个旋钮捆成预设**：`sandbox/mode` + `approval/policy`；默认表两张：`workspace-write`（工作区写 + ask）与 `danger-full-access`（无沙箱 + never）
4. **审批 fail-closed**：只有 `allowed-once` 放行；ask 无应答 = 拒绝（unavailable），never 一切确定性拒绝——headless 的默认姿态
5. **社区审计找到真实边界**：#159 fs-sandbox 竞态、#584 scrubbedParentEnv 误伤、#381 iframe 点击劫持、#817 审计报告（vm 逃逸 + 本地 RPC 无认证）
6. **企业基线一句话**：默认 `workspace-write`+ask、loopback 不放行、插件只装信任源、敏感目录不进 workspace

<details><summary>本章导航</summary>
- [13.1 安全设计哲学：沙箱/权限/审批三层](#131-安全设计哲学沙箱权限审批三层)
- [13.2 沙箱机制原理：fs 边界与工具沙箱](#132-沙箱机制原理fs-边界与工具沙箱)
- [13.3 权限模型：工具权限分级表](#133-权限模型工具权限分级表)
- [13.4 审批流：从请求到放行](#134-审批流从请求到放行)
- [13.5 插件安全审计清单](#135-插件安全审计清单)
- [13.6 社区已知安全案例](#136-社区已知安全案例)
- [13.7 企业安全基线](#137-企业安全基线)
</details>

## 13.1 安全设计哲学：沙箱/权限/审批三层

dsh 的安全骨架是三层各管一件事（依据官方 `docs/subsystems/*` 架构文档，已核验：`sandbox.md` / `permission-presets.md` / `approval.md`；与第 8 章 8.5 实测交叉印证）：

| 层 | 管什么 | 官方包 | 一句话 |
|---|---|---|---|
| 沙箱 | 在哪执行、能碰哪些文件 | `sandbox/sandbox`、`sandbox/sandbox-local`、`sandbox/sandbox-policy` | 隔离命令执行的文件效果 |
| 权限 | 能做什么 | `interaction/permission-presets` | 把沙箱 + 审批捆成命名预设 |
| 审批 | 危险动作要不要人确认 | `interaction/user-approval` | 最小权限的最后一道闸 |

**最小权限原则**是三层共同的设计取向：默认预设只给"工作区写 + 关键操作询问"；任何提升（切 `danger-full-access`、改审批策略）都显式发生并写入会话日志——`permission/preset` 事件是**纯日志的用户意图**，不进模型转录，便于事后回溯"谁在什么时候提了权"。

**威胁模型速记**：三层防线防的是"不可信输入驱动代理越界"——提示词投毒、恶意插件、被诱导的高权限操作（#381 iframe 劫持就是往这条链上打）；它不承诺防"信任代码自身"（插件就是可执行代码，见 13.5），也不承诺防网络/进程级攻击。

> 核心认知：**dsh 的工具执行默认有隔离与审批层，不是裸执行**；但它不是"安全操作系统"——沙箱不挡网络与进程、审批可以被模型自答（13.6）。

## 13.2 沙箱机制原理：fs 边界与工具沙箱

官方沙箱文档明确定义：**沙箱只管文件效果（filesystem effects）**，网络与进程可见性不在其词汇表内。

**三档模式**（`SandboxMode`）：

| 模式 | 允许的文件效果 | 说明 |
|---|---|---|
| `read-only` | 只读 + 必需 sink（POSIX 下如 `/dev/null`） | Windows ACL 后端无显式可写根，报 partial |
| `workspace-write` | 工作区根 + 后端承诺的临时区可写 | **默认预设**；根来自会话不可变 cwd |
| `danger-full-access` | 不设限 | 直接 spawn 原 argv，不走 `ctx.sandbox` |

**执行细节**：
- **策略按调用携带**（per-call）：`SandboxExecutionPolicy`（mode + workspaceRoot + sessionId）在每次能力调用时解析，不绑死在 provider 上——同一 provider 可同时服务 `read-only` 的 bash 与需要可写状态目录的子代理
- **工作区根规范化**：先按文件系统语义 canonicalize（`symlink/..` 解析到真实目录）再做词法归一——防符号链接绕边界
- **后端矩阵**：Linux bwrap/Landlock、macOS Seatbelt、Windows ACL restricted-token；`enforcement: full | partial`——旧 Landlock ABI 与 Windows ACL 的 Everyone/hard-link 边界是当前 partial 案例（**承诺打折扣时，消费方须按 partial 处置**）
- **fs 工具同边界**：`write`/`edit` 等文件工具同样受 workspace-write 约束，不是"文件工具直通、只有 bash 才沙箱"（#149 递归删工作区即发生在 workspace-write 下）
- **只限写不限读**：当前权限模型约束的是**写**，工作区外内容可被读到（#492 提议评测隔离模式时点出的现状）

**工具沙箱**：`bash`/`pwsh` 走 `bash-sandbox` / `pwsh-sandbox`（消费 `ctx.sandbox`）在沙箱内起子进程；Windows 上 pwsh 沙箱有 ACL 约束（第 8 章实测遇到过 temp 权限问题；#758 还报告 Windows 沙箱临时目录清理后永久崩溃）。

**同族案例**：#159 的竞态属于 TOCTOU（检查与使用之间路径被换）；#278 是另一种拓宽手法——`/tmp` 作 workspace 时，受限子进程可通过 rebind 把 workspace-write 授权范围扩宽。两者共同教训：**边界根目录要选可信位置，且不能只信任单一路径检查**。

## 13.3 权限模型：工具权限分级表

官方权限预设把**两个旋钮**——`sandbox/mode` 与 `approval/policy`——捆成命名预设，客户端展示为一个"Permissions"选择器。默认表两张：

| 预设 | sandbox/mode | approval/policy | 语义 |
|---|---|---|---|
| `workspace-write` | workspace-write | ask | 工作区内可写、操作前询问（默认） |
| `danger-full-access` | danger-full-access | never | 无沙箱、不询问 |
| `custom`（派生态） | 任意组合 | 任意 | 手动调旋钮后的"非预设"态，不可作为切换目标 |

**工具权限分级**（按危害半径排序；各工具"建议预设"为按官方文档推导，非逐工具实测——**推断，待实测**）：

| 级别 | 代表工具 | 建议预设 | 风险 | 备注 |
|---|---|---|---|---|
| 只读探查 | `read`/`grep`/`glob` | read-only 兼容 | 低 | 只读不落盘；读不限于工作区 |
| 工作区写 | `write`/`edit`/`str_replace_editor` | workspace-write | 中 | 写边界 = 工作区根 + 临时区 |
| 命令执行 | `bash`/`pwsh` | workspace-write（沙箱内） | 高 | 沙箱不挡网络与进程 |
| 全访问 | 任意（切 danger-full-access） | danger-full-access | 极高 | 关闭所有闸门 |

> 官方文档明确沙箱**只管文件**——所以"命令执行"级的高风险不能靠沙箱消除，要靠审批与信任边界（13.5 / 13.7）兜底。

**真实边界案例**（详见 13.6）：`workspace-write` 下递归删除整个工作区零确认（#149）；`danger-full-access` 误删整个家目录（#461，真实事故）；Windows 上 minimal preset 允许工作区外写入且无审批（#523）；沙箱内 agent 可 `taskkill` 杀宿主（#466，进程可见性在沙箱词汇表外）。

## 13.4 审批流：从请求到放行

官方审批文档：审批回答一个问题——"这个具体动作能不能做？"

**结果集 fail-closed**（`ApprovalOutcome`）：

| 结果 | 含义 | 对调用方的效果 |
|---|---|---|
| `allowed-once` | 一次性放行（只放行被问的这一个动作） | ✅ 继续 |
| `rejected` | 明确拒绝 | ❌ 中止 |
| `cancelled` | 请求被撤回（AbortSignal） | ❌ 中止 |
| `unavailable` | 无应答者 / 应答者异常 | ❌ 中止（默认 fail-closed） |

**策略**（`ApprovalPolicy`）：`ask`（默认，交给应答者链；链为空 → unavailable）；`never`（确定性全部 rejected，不派发任何应答者——headless/CI 的严格姿态）。

**流程**：工具调用 → `approval/request` waterfall（插件可拦截/改写）→ 应答者（Web UI 人肉应答，或 ACP 桥的一次性机器决策）→ 每次请求成对写审计事件 `approval/asked` + `approval/decided`（同一 `ApprovalRequestId`）。

**请求内容**（`ApprovalRequest`）：agent（应答者只回答自己拥有的 agent）+ toolName + callId（关联已流式展示的工具调用，参数不重复渲染）+ reason（为什么问）+ signal（AbortSignal 撤回）。

**三个已知坑**：
1. **审批回环**：#250 真实复现"模型自批准 danger-full-access"（Web approval 通道可被模型自己驱动）——**审批不是安全边界**，只是人机协作闸门
2. **并发误定向**：#453 并发沙箱审批时点 Allow 会中止另一个调用（UI 应答与 callId 错配）
3. **重连丢审批**：#646 重连静默丢 pending approval（resync 清空 + replay 竞态）；headless 下审批行为未定义（#291）

## 13.5 插件安全审计清单

插件是 dsh 的能力边界（"一切皆插件"，见第 4 章）——**装插件 = 装可执行代码**。社区审计（#817 及同族）沉淀的检查清单：

| # | 检查项 | 社区依据 | 处置 |
|---|---|---|---|
| 1 | 插件来源可信？`dsh plugin add` 无签名/来源校验 | #587 | 只装官方/知名源；装前读源码 |
| 2 | boot 期权限最小？插件 boot 期有全配置树写权限 | #587 | 警惕"装完自动改配置"的插件 |
| 3 | 不拿 vm 当安全边界？workflow/动态插件 vm 可逃逸 | #243 #451 #774 #778 | vm 只当隔离引擎，不当安全层 |
| 4 | 子进程环境 scrubbed 正确？`scrubbedParentEnv` 子串误伤合法变量 | #584 | 检查 KEYBOARD/MONKEY 等含 KEY 子串的变量是否被误 scrub（**误伤机制按标题推断**） |
| 5 | 密钥脱敏不 fail-open？settings `role('secret')` 存在脱敏缺口 | #226 | 密钥不写进提示词；校验脱敏逻辑 |
| 6 | 安全 hook 不静默失效？`timeout: 0` 会 fail-open | #460 #583 | hook 超时设正数；加载失败要报错 |
| 7 | 审计留痕？`approval/asked`/`decided` 成对可查 | 官方 approval.md | 关键操作按会话可回溯 |
| 8 | 不泄漏会话明文？崩溃后 `.tmp` 明文会话残留 | #674 | 敏感环境禁用崩溃转储 / 定期清理 |

## 13.6 社区已知安全案例

以下 4 帖全部经 `gh api graphql` 核验存在（deepseek-ai/deepseek-harness Discussions，2026-08-14）：

| 帖号 | 一句话 | 类型 | 影响 |
|---|---|---|---|
| [#159](https://github.com/deepseek-ai/deepseek-harness/discussions/159) | `fs-sandbox` post-check pathname race 可绕过 `workspace-write` 文件边界 | 沙箱竞态 | TOCTOU：检查与使用之间路径被换，可越界写 |
| [#584](https://github.com/deepseek-ai/deepseek-harness/discussions/584) | `scrubbedParentEnv` 子串误伤 KEYBOARD/MONKEY 等合法环境变量（附可 cherry-pick 修复） | 子进程环境 | 合法环境变量被 scrubbed，行为异常 |
| [#381](https://github.com/deepseek-ai/deepseek-harness/discussions/381) | 默认 localhost Web 可被跨站 iframe 点击劫持，诱导授权 `Full access` 并驱动高权限操作 | 前端点击劫持 | 恶意网页诱导用户在 dsh UI 上点出高权限 |
| [#817](https://github.com/deepseek-ai/deepseek-harness/discussions/817) | 安全审计报告：沙箱/审批边界绕过与本地 RPC 无认证（PoC 可私下提供） | 系统性审计 | 覆盖 vm 逃逸（同族 #243 #778）、本地 `/api` 无鉴权（同族 #451，CVSS 8.8）、approval 回环（#250） |

**同族高价值补充**（帖号来自仓库内 `docs/research/discussion-mining.md` §2.6，该报告称全量 780 帖程序化核验）：

| 帖号 | 一句话 | 启示 |
|---|---|---|
| #149 | workspace-write 下可递归删除整个工作区，零确认 | 工作区内容也要防"自毁" |
| #250 | Web approval 回环：模型自批准 danger-full-access | 审批不是安全边界 |
| #461 | Full Access 模式误删整个家目录（真实事故） | 高权限预设风险实锤 |
| #587 | 第三方插件 boot 期有全配置树写权限 | 插件信任 = 供应链安全 |
| #466 | 沙箱内 agent 可 taskkill 杀宿主 | 进程可见性在沙箱词汇外 |
| #674 | 崩溃后 `.tmp` 明文会话残留不清理 | 隐私风险 |

> 免责：以上为 rc.6 时代（2026-08-13 发布后 48h 内）的社区报告，部分可能已在新 rc 修复；引用时注意版本语境。

## 13.7 企业安全基线

给"要上生产 / 团队推广"的决策建议（对齐第 6 章风格）：

| 维度 | 基线 | 依据 |
|---|---|---|
| 网络暴露 | **保持 loopback**（`--host 0.0.0.0` 被官方拒绝是有意的）；远程认证完善前勿绕过 | #76 #130 #397 |
| 权限预设 | 默认 `workspace-write` + ask；`danger-full-access` 只在隔离机 / 一次性任务用 | 官方 preset 表 + #461 |
| 审批策略 | 人肉应答链路必备；headless 用 `never`（确定性拒绝）并前置 review 闸 | approval.md + #291 |
| 插件治理 | 白名单源 + 装前过 13.5 清单；禁止裸 `dsh plugin add github:` | #587 #656 |
| 工作区边界 | 敏感目录（家目录/密钥目录）不进 workspace；工作区内容定期提交版本控制 | #149 #461 |
| 审计 | 会话日志留存（approval 审计对可回溯）；防 `.tmp` 明文残留 | approval.md + #674 |
| 升级纪律 | rc 阶段每次升级重跑 13.5 清单（沙箱后端/预设表可能变） | 第 12 章 rc 版诚信 |

**决策速记**：本地个人开发 → 默认预设即可；团队共享 → `workspace-write` + ask + 插件白名单；CI/无人值守 → headless + `never` + 前置代码 review；任何场景都别为省事长期挂 `danger-full-access`。

**场景 → 推荐组合**（决策建议，按上表基线推导）：

| 场景 | 推荐组合 | 理由 |
|---|---|---|
| 本地个人开发 | 默认 `workspace-write` + ask | 开箱即用，审批不烦人 |
| 团队共享主机 | workspace-write + ask + 插件白名单 | 多用户共用，插件供应链风险放大 |
| CI / 无人值守 | headless + `never` + 前置 review 闸 | 确定性拒绝，无人挂起 |
| 隔离机 / 一次性任务 | `danger-full-access`（机器本身隔离） | 授权最大化但攻击面控制在单机 |

---

## 动手练习（检验你是否真懂了）

1. **理解题**：沙箱三档模式分别允许什么文件效果？为什么说"网络与进程不在沙箱词汇表内"？
   > 自查：参考本章 13.2 节三档表与"后端矩阵"段
2. **理解题**：为什么 headless 下的 `never` 是"最严格"而非"最宽松"？
   > 自查：参考本章 13.4 节"策略"段（deterministic rejected）
3. **动手题**：打开 `dsh web`，观察 Permissions 选择器的两个预设；切到 `danger-full-access` 再切回，看会话日志里的 `permission/preset` 事件
   > 自查：参考本章 13.3 节预设表
4. **动手题**：装一个社区插件前，按 13.5 清单逐条过一遍（来源/源码/权限/审计），结论写进笔记
   > 自查：参考本章 13.5 节清单表
5. **思考题**：为什么 #250 的"模型自批准"说明审批不是安全边界？如果审批挡不住，企业靠什么兜底？
   > 自查：参考本章 13.6 节 + 13.7 节基线表

## 常见疑问 FAQ

**Q1：沙箱能防住恶意代码吗？**
不能当安全边界用。沙箱只管文件效果；网络（如 SSRF）与进程（如 #466 taskkill）在其词汇表外。防恶意代码靠插件信任（13.5）与网络/进程级隔离（容器/VM/远程沙箱——官方文档明确这些是能力缝的 sibling 实现，不是 `ctx.sandbox` 的 provider）。

**Q2：为什么 headless 用 `never` 反而更安全？**
`never` 不是"永不询问"的宽松模式，而是**确定性拒绝**：任何审批请求直接 `rejected`，不派发应答者——无人值守时不会出现"挂着等人点 Allow"。需要放行的动作靠前置 review 或显式配置，而不是运行时询问。

**Q3：`workspace-write` 是不是就安全了？**
边界内相对安全，但 #149 显示"递归删除整个工作区"在 workspace-write 下零确认——沙箱防的是"越界"，不防"边界内自毁"。重要代码请纳入版本控制。

**Q4：第 12 章已提过 #159，这章为什么又讲？**
第 12 章是"已知不足速查表"（一句话 + 状态），本章展开机制（post-check 竞态怎么发生）、同族（#278 /tmp rebind）与缓解（不信任单一路径检查、关键目录不进 workspace）。

**Q5：这些安全帖号可信吗？不会是编的吧？**
4 个核心帖号（#159 #584 #381 #817）均经 `gh api graphql` 逐号核验存在（链接见 13.6 表格）；同族补充帖来自仓库内 `docs/research/discussion-mining.md`（全量分页抓取 780 帖并程序化核验）。

---

**下一章**：[第 14 章：成本与用量](./14-cost.md)（规划中）。
