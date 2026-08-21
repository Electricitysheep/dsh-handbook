# 官方讨论区内容挖掘报告（deepseek-ai/deepseek-harness）

> 挖掘时间：2026-08-14（dsh 0.1.0-rc.8 时代）
> 数据来源：`gh api graphql` 分页抓取官方 Discussions 全部 **780 帖**（Announcements 1 / General 424 / Ideas 165 / Q&A 103 / Show and tell 84 / Polls 3），逐帖通读标题 + 正文前 500 字。
> 目的：把社区真实使用经验（踩坑/可复现方案/高频问题/生态实践）融入 dsh-handbook 白皮书。所有帖号均经 gh 验证存在。
>
> **摘要速览**：发布首日社区火力集中在三类事——① Windows 兼容性灾难（中文路径截断、目录选择器崩溃、403/随机 UUID 系列），② 第三方模型接入（思考强度、developer role、工具名丢失），③ 生态补位（CLI/TUI、桌面端、memory、视觉桥，官方未做社区全做）。白皮书已有章节覆盖安装/插件/生态骨架，但以下领域是**内容缺口**：Windows 中文路径家族 bug、第三方网关 compat 方言、`unknown tool ""` 流式 bug、历史加载失败（stack overflow）、子代理模型继承、安全审计报告、社区插件生态全景。

---

## 一、总体发现（Top 规律）

1. **官方 Issues 关闭、暂不收 PR**（[#341](https://github.com/deepseek-ai/deepseek-harness/discussions/341) [#371](https://github.com/deepseek-ai/deepseek-harness/discussions/371) [#775](https://github.com/deepseek-ai/deepseek-harness/discussions/775) 反复呼吁开放）：所有 bug 都以 Discussion 形式提交，社区已形成"报告-复现-根因-修复分支"的成熟模板（大量帖自带 cherry-pick 修复），白皮书第 7 章可引用这一贡献模式。
2. **Windows 是第一大痛点**：约 60+ 帖与 Windows 相关。最高频的是**原生目录选择器截断中文路径**（同一根因 readUtf16 只查低字节 0x00，15+ 帖独立复现：#107 #151 #210 #244 #295 #396 #428 #488 #563 #580 #617 #643 #644 #701 #727 #761 #800），其次是目录选择器 worker 崩溃（koffi 相关，#30 #154 #236 #293 #449 #768）。
3. **"官方没做，社区全做"**：官方无 CLI/TUI/桌面端/memory/视觉，社区两周内涌现：TUI（#391 #132 #405 #386 #415 #416）、桌面壳（#182 #227 #239 #276 #279 #358 #407 #414 #419 #434 #446 #529 #537 #683 #689 #767 #769 #789）、memory（#192 #484 #525 #516 #544 #795 #797）、视觉桥（#384 #395 #456 #482 #495 #733 #357 #561）。
4. **安全审计异常活跃**：第三方安全研究者对 plugin 模型/沙箱/vm 做了系统性审计（#243 #250 #278 #381 #451 #454 #774 #778），发现了可复现的 vm 逃逸、approval 回环、clickjacking 等真实问题——这是白皮书第 12 章"已知不足"的富矿。

---

## 二、按主题分类挖掘

### 2.1 安装 / 环境 / 配置

| 帖号 | 核心内容摘要 | 白皮书融入建议 |
|---|---|---|
| [#49](https://github.com/deepseek-ai/deepseek-harness/discussions/49) | ArchLinux 上 npx 安装失败（node v26.7.0），给出完整 log | 第 2 章「安装」加 Linux 发行版注意项 |
| [#55](https://github.com/deepseek-ai/deepseek-harness/discussions/55) | `pnpm add -g @deepseek-ai/dsh` 后启动找不到 `cordis-plugin-timer` | 第 3 章坑位（全局安装的依赖解析问题） |
| [#86](https://github.com/deepseek-ai/deepseek-harness/discussions/86) | 源码跑 `pnpm run build` 失败——配置里写死了 npm 指令 | 第 3 章/贡献指南 |
| [#100](https://github.com/deepseek-ai/deepseek-harness/discussions/100) | `node:zlib` 无 `createZstdDecompress`：Node 版本过低（需 ≥22.19） | 第 2 章「环境要求」加 Node 版本红线 |
| [#113](https://github.com/deepseek-ai/deepseek-harness/discussions/113) | macOS arm64 上 npx 启动崩溃，`--expose-internals is required for HMR service`；用 `node --expose-internals` 可启动 | **内容缺口**：macOS 启动坑，FAQ 候选 |
| [#139](https://github.com/deepseek-ai/deepseek-harness/discussions/139) | 全局 `core.hooksPath`（Codex 等设置）导致 pnpm install/lefthook 失败 | 第 7 章贡献指南（与 Codex 共存的坑） |
| [#141](https://github.com/deepseek-ai/deepseek-harness/discussions/141) | Windows 源码编译 rolldown 缺 binding：`pnpm i @rolldown/binding-win32-x64-msvc` 解决 | 第 3 章 Windows 源码开发坑 |
| [#176](https://github.com/deepseek-ai/deepseek-harness/discussions/176) | 首次 `npx dsh web` 在 Windows 上 8+ 分钟零反馈（npm 下载 500+ 包） | 第 2 章 FAQ「npx 很慢」补充细节 |
| [#177](https://github.com/deepseek-ai/deepseek-harness/discussions/177) | Ubuntu 安装失败：`Failed to load native module: pty.node` | **内容缺口**：Linux 原生模块缺失类问题 |
| [#193](https://github.com/deepseek-ai/deepseek-harness/discussions/193) | macOS npx 运行失败（HMR expose-internals 同 #113） | 同上 |
| [#204](https://github.com/deepseek-ai/deepseek-harness/discussions/204) | macOS pnpm 全局安装后 loader 解析不到 ~88 个插件包 | 第 3 章全局安装坑 |
| [#223](https://github.com/deepseek-ai/deepseek-harness/discussions/223) | mise+aube 严格解析器报 "mutually recursive peers"：cordis 反向 peer 依赖成环 | 第 3 章依赖图坑（高级） |
| [#252](https://github.com/deepseek-ai/deepseek-harness/discussions/252) | 建议 README 补 Windows 全局安装说明（`npm i -g`、新开终端、原生依赖放行） | **白皮书已有**（第 2 章），可互相印证 |
| [#269](https://github.com/deepseek-ai/deepseek-harness/discussions/269) | 必须 `--expose-internals` 才能启动（同 #113 家族） | 同上 |
| [#273](https://github.com/deepseek-ai/deepseek-harness/discussions/273) | 发布包漏 `dsh-app-boot` 依赖 → 手动补装 `cordis-plugin-group` 绕过 | 第 3 章「rc.1 依赖断裂」同族案例 |
| [#293](https://github.com/deepseek-ai/deepseek-harness/discussions/293) | **koffi 3.1.3/3.1.4 win32-x64 预编译损坏**，建议锁 koffi@3.1.2 | **内容缺口**：Windows 安装失败新根因 |
| [#311](https://github.com/deepseek-ai/deepseek-harness/discussions/311) | `AbortSignal.timeout is not a function`：Node 版本过低 | 第 2 章环境要求 |
| [#369](https://github.com/deepseek-ai/deepseek-harness/discussions/369) | `pnpm dlx @deepseek-ai/dsh web` 404（@deepseek-ai/dsh-pty 未发布/0.0.1-rc.2） | 第 2 章安装方式对比 |
| [#412](https://github.com/deepseek-ai/deepseek-harness/discussions/412) | macOS volta 管理下 pnpm install 失败（@pnpm/exe 身份验证） | 贡献指南 |
| [#556](https://github.com/deepseek-ai/deepseek-harness/discussions/556) | Windows 首次 pnpm install 时 lefthook postinstall 报 yaml UTF-8（自愈型 bug） | 贡献指南 |
| [#568](https://github.com/deepseek-ai/deepseek-harness/discussions/568) | `node-domexception@1.0.0` deprecated 警告是否可忽略 | FAQ「安装警告」 |
| [#574](https://github.com/deepseek-ai/deepseek-harness/discussions/574) | stripTypeScriptTypes ExperimentalWarning（无害） | FAQ |
| [#605](https://github.com/deepseek-ai/deepseek-harness/discussions/605) | Linux x64 缺 node-pty `pty.node` 预编译，插件树启动失败 | **内容缺口**：Linux pty 缺失 |
| [#623](https://github.com/deepseek-ai/deepseek-harness/discussions/623) | 源码 build 失败：tsdown 需 unrun（可选 peerDep 未装） | 贡献指南 |
| [#648](https://github.com/deepseek-ai/deepseek-harness/discussions/648) | 首次连接失败被误报为 "reconnecting"，重试无上限 | 第 6 章踩坑 |
| [#649](https://github.com/deepseek-ai/deepseek-harness/discussions/649) | **提议 `dsh doctor` 一键环境诊断**（汇总 #605 #623 #650 #748 #752 同类问题） | **内容缺口**：环境诊断工具需求 |
| [#650](https://github.com/deepseek-ai/deepseek-harness/discussions/650) | Linux GCC<10 无法编译 node-pty（C++20 要求） | **内容缺口**：Linux 编译工具链要求 |
| [#679](https://github.com/deepseek-ai/deepseek-harness/discussions/679) | Windows 上 pnpm 未识别命令（未安装） | FAQ「基础环境」 |
| [#690](https://github.com/deepseek-ai/deepseek-harness/discussions/690) | NixOS 上 HMR 报 `--expose-internals is required`（node-addon 探测失败） | 同上家族 |
| [#700](https://github.com/deepseek-ai/deepseek-harness/discussions/700) | Ubuntu 缺 g++/make 导致安装失败 | FAQ「Linux 安装」 |
| [#748](https://github.com/deepseek-ai/deepseek-harness/discussions/748) | `install-lefthook failed`：Node 版本过高（v24.15 不行），volta pin node@22.19.0 解决 | 贡献指南/第 2 章 |
| [#752](https://github.com/deepseek-ai/deepseek-harness/discussions/752) | `node-addon-require-builtin` 与 Node 24.18.1 不兼容，静默回退掩盖根因 | 同 #690 家族 |

### 2.2 Windows 兼容性（最大痛点，60+ 帖）

| 帖号 | 核心内容摘要 | 白皮书融入建议 |
|---|---|---|
| [#30](https://github.com/deepseek-ai/deepseek-harness/discussions/30) | 目录选择器报 `win32 folder dialog worker exited before reporting a result` | 第 3 章 Windows 坑 #6 扩展 |
| [#37](https://github.com/deepseek-ai/deepseek-harness/discussions/37) | 目录选择对话框在 Firefox 后台弹出（Brave 正常） | 第 12 章跨平台短板 |
| [#38](https://github.com/deepseek-ai/deepseek-harness/discussions/38) | 无法打开文件夹：koffi 包路径缺失 | 同 #30 家族 |
| [#47](https://github.com/deepseek-ai/deepseek-harness/discussions/47) | **工作区不支持中文路径名** | **内容缺口**：中文路径限制说明 |
| [#53](https://github.com/deepseek-ai/deepseek-harness/discussions/53) | Windows 快速模式默认调 Linux 命令：`terminal inspection is unsupported on platform win32` | 第 3/12 章 Windows 工具执行差异 |
| [#65](https://github.com/deepseek-ai/deepseek-harness/discussions/65) | **工作区选磁盘根目录 → 空标题工作区 + webui 异常**（basename 空串） | **内容缺口**：根目录工作区限制 |
| [#71](https://github.com/deepseek-ai/deepseek-harness/discussions/71) | 工作目录存在名为 `.env` 的文件夹 → 启动报 EISDIR | FAQ/第 2 章坑 |
| [#92](https://github.com/deepseek-ai/deepseek-harness/discussions/92) | 目录选择对话框未前置（每次复现，Edge） | 同 #37 家族 |
| [#107](https://github.com/deepseek-ai/deepseek-harness/discussions/107) | **中文路径截断**：readUtf16 单字节判 0，`开`=U+5F00 被截 | **最高频家族根因帖** |
| [#116](https://github.com/deepseek-ai/deepseek-harness/discussions/116) | 写文件 EISDIR：原子写（link）在 Windows 失败 | 第 3 章 Windows 文件系统坑 |
| [#121](https://github.com/deepseek-ai/deepseek-harness/discussions/121) | `Pwsh Error: invalid arguments: missing required property "command"` 循环耗 token | **内容缺口**：pwsh 调用失败家族 |
| [#127](https://github.com/deepseek-ai/deepseek-harness/discussions/127) | 新会话头几次工具调用连续报错（Windows） | 第 6 章踩坑 |
| [#128](https://github.com/deepseek-ai/deepseek-harness/discussions/128) | WSL 里拉目录报 `/api/host.listDirectory` HTTP 403 | **内容缺口**：WSL 下 403 家族 |
| [#143](https://github.com/deepseek-ai/deepseek-harness/discussions/143) | 整盘（D:\）作工作区：空标题 + `session.create` EPERM | 同 #65 家族 |
| [#151](https://github.com/deepseek-ai/deepseek-harness/discussions/151) | 中文路径截断细节：所有 U+XX00 字符（一 U+4E00 等） | 同 #107 家族 |
| [#154](https://github.com/deepseek-ai/deepseek-harness/discussions/154) | picker worker 崩溃根因：ESM loader 把 Windows 绝对路径当 URL（`e:` 协议） | 同 #30 家族（根因版） |
| [#160](https://github.com/deepseek-ai/deepseek-harness/discussions/160) | WSL/Ubuntu 下工作区只能选 /root 内目录 | **内容缺口**：WSL 工作区限制 |
| [#197](https://github.com/deepseek-ai/deepseek-harness/discussions/197) | **koffi 原生崩溃**：npm 装不上/选择器崩/服务静默挂（0xC0000005），含修复思路 | **内容缺口**：koffi 崩溃完整分析 |
| [#210](https://github.com/deepseek-ai/deepseek-harness/discussions/210) | 路径截断复现（耀 U+8000） | 同 #107 家族 |
| [#225](https://github.com/deepseek-ai/deepseek-harness/discussions/225) | PowerShell 相关调用全部 `unknown_tool` | 同 #121 家族 |
| [#236](https://github.com/deepseek-ai/deepseek-harness/discussions/236) | picker worker 确认文件夹后崩溃（win32 folder dialog worker exited） | 同 #30 家族 |
| [#244](https://github.com/deepseek-ai/deepseek-harness/discussions/244) | 含"需求"等汉字路径截断 + **附修复补丁** | 同 #107 家族（附 patch） |
| [#249](https://github.com/deepseek-ai/deepseek-harness/discussions/249) | **大小写不同的 Session ID 在 JSONL 后端路径冲突**（Windows 大小写不敏感） | **内容缺口**：存储层 Windows 问题 |
| [#256](https://github.com/deepseek-ai/deepseek-harness/discussions/256) | 从 Codex 桌面环境启动选工作区受阻（picker 不可见/主目录不可读/端口占用） | 第 12 章 |
| [#259](https://github.com/deepseek-ai/deepseek-harness/discussions/259) | picker 对话框不置前根因（IFileOpenDialog 后台） | 同 #37 家族 |
| [#268](https://github.com/deepseek-ai/deepseek-harness/discussions/268) | **Windows taskkill 当前目录劫持**：workspace 放 taskkill.exe 可劫持宿主清理 | 第 8 章安全（高级） |
| [#292](https://github.com/deepseek-ai/deepseek-harness/discussions/292) | Windows 无法选择含中文路径的工作区 | 同 #107 家族 |
| [#293](https://github.com/deepseek-ai/deepseek-harness/discussions/293) | koffi 3.1.3/3.1.4 损坏 → 锁 3.1.2 | 同 #197 家族 |
| [#295](https://github.com/deepseek-ai/deepseek-harness/discussions/295) | 中文路径截断复现 + 修复代码片段 | 同 #107 家族 |
| [#296](https://github.com/deepseek-ai/deepseek-harness/discussions/296) | 运行报 `rename is not defined`（Windows 10） | 第 6 章踩坑 |
| [#298](https://github.com/deepseek-ai/deepseek-harness/discussions/298) | WSL2+systemd-nspawn 里 picker 静默失败（zenity 退出码 1 被当取消） | **内容缺口**：Linux/WSL picker 差异 |
| [#324](https://github.com/deepseek-ai/deepseek-harness/discussions/324) | 选中路径但工作区未选中（Windows 11） | 同 #30 家族 |
| [#345](https://github.com/deepseek-ai/deepseek-harness/discussions/345) | 真实用户连串反馈：路径不能含特殊符号/空格/多语种（"ai学习"/"ai 写作"失败） | 第 2/12 章（与 #47 呼应） |
| [#396](https://github.com/deepseek-ai/deepseek-harness/discussions/396) | 截断复现（含「开」字） | 同 #107 家族 |
| [#401](https://github.com/deepseek-ai/deepseek-harness/discussions/401) | **Windows 工作区连接后外部新增子目录无法写入**（capability SID 不继承） | **内容缺口**（白皮书第 12 章已有回应，可深化） |
| [#409](https://github.com/deepseek-ai/deepseek-harness/discussions/409) | PowerShell 调用不成功 + 弹框；插件无便捷安装处 | 同 #121 家族 |
| [#423](https://github.com/deepseek-ai/deepseek-harness/discussions/423) | 外部创建/移入子目录永远无法写入（ACE 永不补授），附验证 | 同 #401 家族 |
| [#425](https://github.com/deepseek-ai/deepseek-harness/discussions/425) | **edit/write 覆盖已有文件 ReplaceFileW EIO 高频失败**（瞬时文件锁，无重试） | **内容缺口**：Windows 覆盖写失败 |
| [#428](https://github.com/deepseek-ai/deepseek-harness/discussions/428) | VS Code 内嵌 web UI 的截断复现 | 同 #107 家族 |
| [#449](https://github.com/deepseek-ai/deepseek-harness/discussions/449) | picker 失败（Windows 10，Chrome/Edge 均现） | 同 #30 家族 |
| [#458](https://github.com/deepseek-ai/deepseek-harness/discussions/458) | writeFileAtomic 缺父目录 fsync（POSIX 崩溃持久性） | 第 6/8 章（深度） |
| [#463](https://github.com/deepseek-ai/deepseek-harness/discussions/463) | **Python tempfile.mkdtemp 显式安全描述符 → 沙箱内自锁，pytest tmp_path 失效** | **内容缺口**：Windows 沙箱 + Python 冲突 |
| [#488](https://github.com/deepseek-ai/deepseek-harness/discussions/488) | 截断复现（"05agent开发"→"05agent"） | 同 #107 家族 |
| [#527](https://github.com/deepseek-ai/deepseek-harness/discussions/527) | Windows "New workspace" 无反应：native dialog 替代了 in-browser picker | 同 #30 家族（交互层） |
| [#542](https://github.com/deepseek-ai/deepseek-harness/discussions/542) | resolveWorkspacePath 混用正反斜杠（C:\a/b） | 第 3 章 Windows 坑 |
| [#563](https://github.com/deepseek-ai/deepseek-harness/discussions/563) | 截断根因 + 修复（koffi + readUtf16） | 同 #107 家族（根因最全版） |
| [#580](https://github.com/deepseek-ai/deepseek-harness/discussions/580) | 截断修复（附可 cherry-pick） | 同 #107 家族 |
| [#589](https://github.com/deepseek-ai/deepseek-harness/discussions/589) | **默认端口 3080 落在 Hyper-V 保留区间 → EACCES**（3070-3169 被保留），换 13080 解决 | **内容缺口**：端口占用新根因 |
| [#592](https://github.com/deepseek-ai/deepseek-harness/discussions/592) | 无法读取带空格的工作区路径 | 同 #345 家族 |
| [#617](https://github.com/deepseek-ai/deepseek-harness/discussions/617) | 截断复现（"整理APP需求"→"整理APP"） | 同 #107 家族 |
| [#643](https://github.com/deepseek-ai/deepseek-harness/discussions/643) | 截断复现 + 修复建议 | 同 #107 家族 |
| [#644](https://github.com/deepseek-ai/deepseek-harness/discussions/644) | 截断复现（可直接粘贴 issue） | 同 #107 家族 |
| [#663](https://github.com/deepseek-ai/deepseek-harness/discussions/663) | **Windows 下调用 pwsh 导致 DSH 假死**（页面超时、terminate 不回收） | 同 #121 家族（最严重版） |
| [#674](https://github.com/deepseek-ai/deepseek-harness/discussions/674) | 崩溃后 `.tmp` 明文会话文件残留不清理（隐私） | 第 8 章安全 |
| [#701](https://github.com/deepseek-ai/deepseek-harness/discussions/701) | 截断复现（一 U+4E00） | 同 #107 家族 |
| [#717](https://github.com/deepseek-ai/deepseek-harness/discussions/717) | Windows 子进程：无优雅终止阶梯/孙进程输出截断/spill 权限不生效/shellPath 指向 /bin/bash | **内容缺口**：Windows 子进程系统性问题清单 |
| [#727](https://github.com/deepseek-ai/deepseek-harness/discussions/727) | 截断复现（项目一测试→项目） | 同 #107 家族 |
| [#742](https://github.com/deepseek-ai/deepseek-harness/discussions/742) | vcpkg 写入被沙箱拦，cmake 挂死不报错（难排查） | 第 8 章沙箱排查技巧 |
| [#746](https://github.com/deepseek-ai/deepseek-harness/discussions/746) | `terminal_open` Windows 不支持（createProcessInspector 只实现 linux/darwin）；失败命令显示绿色完成 | **内容缺口**：持久终端 Windows 限制 |
| [#747](https://github.com/deepseek-ai/deepseek-harness/discussions/747) | 工作区文件夹改名后卡死 | 第 6 章踩坑 |
| [#750](https://github.com/deepseek-ai/deepseek-harness/discussions/750) | 内测声明确认保存失败（safe-delete trash 报错） | 第 2 章首次启动坑 |
| [#755](https://github.com/deepseek-ai/deepseek-harness/discussions/755) | **局域网 HTTP 访问所有 RPC 失败：crypto.randomUUID 非安全上下文不可用** | **内容缺口**：LAN 访问限制（含成因） |
| [#758](https://github.com/deepseek-ai/deepseek-harness/discussions/758) | **Windows 沙箱临时目录清理后永久崩溃不自愈（P0）+ 4 个相关问题** | **内容缺口**：Windows 沙箱稳定性 |
| [#761](https://github.com/deepseek-ai/deepseek-harness/discussions/761) | 截断复现（去重的单一装置数据→去重的单） | 同 #107 家族 |
| [#768](https://github.com/deepseek-ai/deepseek-harness/discussions/768) | **koffi 崩溃根因：STA 线程 CoUninitialize 段错误**（MTA 不崩；省略 CoUninitialize 修复） | 同 #197 家族（根因版） |
| [#770](https://github.com/deepseek-ai/deepseek-harness/discussions/770) | arm Ubuntu + Firefox 无法选择工作区 | 第 12 章跨平台 |
| [#800](https://github.com/deepseek-ai/deepseek-harness/discussions/800) | 截断复现（07 最終產出→07） | 同 #107 家族 |

### 2.3 插件开发

| 帖号 | 核心内容摘要 | 白皮书融入建议 |
|---|---|---|
| [#129](https://github.com/deepseek-ai/deepseek-harness/discussions/129) | Code Mode 无参工具调用被拒（binding arguments must be lossless JSON） | 第 4 章 Code Mode 坑 |
| [#173](https://github.com/deepseek-ai/deepseek-harness/discussions/173) | produced-file 打开动作可拦截（含补丁分支） | 第 4 章扩展点案例 |
| [#186](https://github.com/deepseek-ai/deepseek-harness/discussions/186) | "动态插件"与组合文件两套系统并存，用户困惑 | 第 3 章创造模式说明 |
| [#272](https://github.com/deepseek-ai/deepseek-harness/discussions/272) | **桥接插件**：Claude Code/Codex/OpenCode/Pi 配置+技能迁入 dsh | 第 7 章生态（迁移专题） |
| [#285](https://github.com/deepseek-ai/deepseek-harness/discussions/285) | 创造模式 preset 插件定位：探路工具，验证后沉淀到组合文件 | 第 3 章创造模式 |
| [#297](https://github.com/deepseek-ai/deepseek-harness/discussions/297) | **插件 schema 写坏 cordis.patch.yml → 整个 dsh 崩溃**（Invalid schema for function） | **内容缺口**：插件安装事故恢复 |
| [#380](https://github.com/deepseek-ai/deepseek-harness/discussions/380) | **写第一个 dsh 插件踩的六个坑**（@deepseek-ai 可 import 与否、扁平兜底目录、PluginNotFound 等，本机复核） | **与白皮书第 3/4 章结论互相印证**（README 已引用此帖） |
| [#382](https://github.com/deepseek-ai/deepseek-harness/discussions/382) | 动态插件重启后不持久化（无法保存为常驻插件） | 第 3 章动态插件限制 |
| [#385](https://github.com/deepseek-ai/deepseek-harness/discussions/385) | 建议发布教程加社区组合包实例（visionDS） | 第 7 章/附录 |
| [#410](https://github.com/deepseek-ai/deepseek-harness/discussions/410) | **`@deepseek-ai/dsh-tools@0.0.1-rc.1` 无法安装：peer `dsh-type-meta` 未发布** | 第 4 章依赖坑 |
| [#432](https://github.com/deepseek-ai/deepseek-harness/discussions/432) | dsh-doctor：patch 失败静默启动（id 覆盖/未知 id） | 第 3 章 patch 层坑 |
| [#447](https://github.com/deepseek-ai/deepseek-harness/discussions/447) | `Invalid schema for function 'cmd'`：插件 schema 错误拖垮 agent | 第 4 章 schema 校验 |
| [#462](https://github.com/deepseek-ai/deepseek-harness/discussions/462) | **插件运行时验证方法论：mock llm + headless + 审计 dump，零成本无 key 验证 waterfall** | **已沉淀**：第 4 章契约测试 + 第 8 章 8.7 节无 Key 运行时验证 |
| [#502](https://github.com/deepseek-ai/deepseek-harness/discussions/502) | 第三方 settings namespaces 被硬编码白名单挡住（plugin-configuration 不显示） | 第 4 章 settings 扩展点 |
| [#558](https://github.com/deepseek-ai/deepseek-harness/discussions/558) | **code 模式 run_code/bash 同名 required description 导致死循环** | **内容缺口**：Code Mode 工具参数坑 |
| [#572](https://github.com/deepseek-ai/deepseek-harness/discussions/572) | 进程内多份 `@deepseek-ai/dsh-tools` → Symbol key 不匹配，调度器静默 undefined（crash） | 第 4 章依赖复制坑 |
| [#581](https://github.com/deepseek-ai/deepseek-harness/discussions/581) | ToolArgsError 不带工具名 → 死循环（同 #558，附修复） | 同 #558 |
| [#582](https://github.com/deepseek-ai/deepseek-harness/discussions/582) | **Claude hook matcher 大小写敏感：Bash 选不中 bash，安全 hook 静默失效** | **内容缺口**：hooks 迁移坑 |
| [#583](https://github.com/deepseek-ai/deepseek-harness/discussions/583) | `defaultTimeoutMs: 0` 使全部 hook fail-open（应加载时失败） | 同 #582 家族 |
| [#584](https://github.com/deepseek-ai/deepseek-harness/discussions/584) | scrubbedParentEnv 子串误伤 KEYBOARD/MONKEY 等环境变量 | 第 4 章子进程环境 |
| [#618](https://github.com/deepseek-ai/deepseek-harness/discussions/618) | MCP list_changed 重同步撞 namespace 抢占 → 工具集清空 | 第 9 章 MCP 坑 |
| [#631](https://github.com/deepseek-ai/deepseek-harness/discussions/631) | host-apiproxy 重复 Cordis 依赖键（Bun 严格解析器报错） | 贡献指南 |
| [#656](https://github.com/deepseek-ai/deepseek-harness/discussions/656) | `dsh plugin add github:` 只加依赖不 append 到 profile bundles | 第 3 章插件安装坑 |
| [#689](https://github.com/deepseek-ai/deepseek-harness/discussions/689) | run_code 内所有 tools.* 被 missing description 拒绝（同 #558 家族） | 同 #558 |
| [#708](https://github.com/deepseek-ai/deepseek-harness/discussions/708) | 让 dsh 装插件，插件把自己装死（重启后无法启动） | 同 #297 家族 |
| [#711](https://github.com/deepseek-ai/deepseek-harness/discussions/711) | 工具 description 含 `{{...}}` 破坏 code-mode prompt 组装 | 第 4 章工具描述坑 |
| [#715](https://github.com/deepseek-ai/deepseek-harness/discussions/715) | 所有带参工具调用生成 `{"input": ""}` 参数名丢失 | **内容缺口**：参数丢失 bug |
| [#777](https://github.com/deepseek-ai/deepseek-harness/discussions/777) | 插件缺 Manifest 设计与 i18n 支持 | 第 7 章生态建议 |
| [#780](https://github.com/deepseek-ai/deepseek-harness/discussions/780) | llm-pi-ai 暴露 compat 开关（branch ready） | 第 4 章/8 章 |
| [#781](https://github.com/deepseek-ai/deepseek-harness/discussions/781) | 提议 ctx.lsp seam 增加 diagnostics/formatDocument/completion | 第 4 章扩展点展望 |
| [#783](https://github.com/deepseek-ai/deepseek-harness/discussions/783) | profile 内 pnpm install 后 `Cannot read properties of undefined (reading 'prepare')`（dsh-tools 双份 Symbol 分裂） | 同 #572 家族 |

### 2.4 模型 / API 接入（第三方模型是第二痛点）

| 帖号 | 核心内容摘要 | 白皮书融入建议 |
|---|---|---|
| [#80](https://github.com/deepseek-ai/deepseek-harness/discussions/80) | Flash 模型 `<think>` 块显示异常 | 第 5 章 UI 坑 |
| [#97](https://github.com/deepseek-ai/deepseek-harness/discussions/97) | 对话中吐出重复字符（v4 flash） | 第 6 章踩坑 |
| [#112](https://github.com/deepseek-ai/deepseek-harness/discussions/112) | 接入第三方视觉模型仍说"无法识别图片" | 第 8 章多模态接入 |
| [#117](https://github.com/deepseek-ai/deepseek-harness/discussions/117) | **第三方 API 下子代理报 `no API key for provider route "deepseek-official"`** | **内容缺口**：子代理模型路由继承 |
| [#122](https://github.com/deepseek-ai/deepseek-harness/discussions/122) | 第三方模型无法选择推理强度 | 第 8 章模型配置 |
| [#135](https://github.com/deepseek-ai/deepseek-harness/discussions/135) | 创建自定义模型报"已有提供方使用了这个 ID" | 第 8 章配置坑 |
| [#161](https://github.com/deepseek-ai/deepseek-harness/discussions/161) | **工具调用丢失：continuation deltas 传 null → id/name 覆盖为空 → UNKNOWN_TOOL** | **内容缺口**：unknown tool 家族根因之一 |
| [#175](https://github.com/deepseek-ai/deepseek-harness/discussions/175) | 模型一直连不上（DeepSeek API request failed） | FAQ「连接失败」 |
| [#196](https://github.com/deepseek-ai/deepseek-harness/discussions/196) | 自定义 API 也想配思考强度 + @选文件 | 第 8 章 |
| [#199](https://github.com/deepseek-ai/deepseek-harness/discussions/199) | vLLM 自部署把 thinking 流成 delta.reasoning → 适配器丢弃 | 第 8 章自部署模型坑 |
| [#208](https://github.com/deepseek-ai/deepseek-harness/discussions/208) | 提议 Codex OAuth 作为主 LLM provider | 第 7 章生态 |
| [#231](https://github.com/deepseek-ai/deepseek-harness/discussions/231) | 多轮会话丢 reasoning：400 "reasoning_text must be passed back" | 第 6/8 章 |
| [#245](https://github.com/deepseek-ai/deepseek-harness/discussions/245) | 选多模态模型仍提示"模型不支持图片" | 同 #112 家族 |
| [#265](https://github.com/deepseek-ai/deepseek-harness/discussions/265) | **同一 key 下 harness TPS 140 vs opencode 80**（性能正反馈） | 第 6 章/benchmark 补充 |
| [#280](https://github.com/deepseek-ai/deepseek-harness/discussions/280) | llm-pi-ai 应支持 compat.supportsDeveloperRole（火山 Coding Plan 只支持 system role） | **内容缺口**：developer role 家族 |
| [#302](https://github.com/deepseek-ai/deepseek-harness/discussions/302) | 自定义 provider 无 reasoningEffort 选项 | 同 #122 家族 |
| [#320](https://github.com/deepseek-ai/deepseek-harness/discussions/320) | **预设系统提示词全英文 → 中文模型被强制英文思考，建议 i18n** | **内容缺口**：中文思考优化建议 |
| [#321](https://github.com/deepseek-ai/deepseek-harness/discussions/321) | 支持"主模型+辅助视觉模型"配置（识图不切模型） | 第 8 章多模态 |
| [#356](https://github.com/deepseek-ai/deepseek-harness/discussions/356) | 自定义 pi-ai provider 模型默认 text-only，无 UI 可改 | 同 #112 家族 |
| [#372](https://github.com/deepseek-ai/deepseek-harness/discussions/372) | LLM 中文输出用半角逗号 ","（不用"，"） | 第 6 章观察（趣味） |
| [#373](https://github.com/deepseek-ai/deepseek-harness/discussions/373) | LLM stream EOF 无终结被当作成功回复 | 第 6 章踩坑 |
| [#388](https://github.com/deepseek-ai/deepseek-harness/discussions/388) | 兼容网关 `data: [DONE]` 后无空行 → STREAM_CLOSED 丢回复 | 第 8 章网关兼容 |
| [#408](https://github.com/deepseek-ai/deepseek-harness/discussions/408) | **web_search 固定请求官方端点，baseURL 覆盖无效 → 自配网关认证必失败** | **内容缺口**：web_search 配置坑 |
| [#422](https://github.com/deepseek-ai/deepseek-harness/discussions/422) | 多子任务汇总时 HTTP 400（192k cached tokens） | 第 9 章子代理坑 |
| [#436](https://github.com/deepseek-ai/deepseek-harness/discussions/436) | 孤立 UTF-16 代理码元 → 会话永久 HTTP 400（无法恢复） | 第 6 章踩坑 |
| [#444](https://github.com/deepseek-ai/deepseek-harness/discussions/444) | pi-ai qwen token plan catalog 过期（qwen3.8-max-preview） | 第 8 章模型目录 |
| [#455](https://github.com/deepseek-ai/deepseek-harness/discussions/455) | **子代理继承"创建时默认模型"而非"会话当前模型"**（#117 根因版） | 同 #117 家族（根因） |
| [#472](https://github.com/deepseek-ai/deepseek-harness/discussions/472) | llm-pi-ai compat schema 丢弃大部分 OpenAICompletionsCompat 字段（手写 provider 不可用） | 同 #280 家族 |
| [#473](https://github.com/deepseek-ai/deepseek-harness/discussions/473) | 同 #472 中文版（火山方舟/Kimi 具体案例） | 同 #280 家族 |
| [#474](https://github.com/deepseek-ai/deepseek-harness/discussions/474) | 文本模型禁图根因：inputModalities 硬编码 ["text"] | 同 #112 家族（根因） |
| [#495](https://github.com/deepseek-ai/deepseek-harness/discussions/495) | **dsh-vision-router：图片轮次路由到视觉模型，纯文字轮反向回 DeepSeek** | 第 7 章生态插件案例 |
| [#530](https://github.com/deepseek-ai/deepseek-harness/discussions/530) | WebSocket error 被分类为 PI_AI_ERROR 绕过重试 | 第 6 章重试坑 |
| [#545](https://github.com/deepseek-ai/deepseek-harness/discussions/545) | 工具调用文本化（偶发） | 第 6 章 |
| [#551](https://github.com/deepseek-ai/deepseek-harness/discussions/551) | llm-pi-ai 需暴露 supportsDeveloperRole（reasoning 模型在拒 developer role 网关必失败） | 同 #280 家族 |
| [#559](https://github.com/deepseek-ai/deepseek-harness/discussions/559) | **第三方 OpenAI 兼容网关方言自动测定 + 修复（dsh-gateway-presets 插件 + 增强 fork）** | **内容缺口**：网关方言系统性问题 + 社区解法 |
| [#560](https://github.com/deepseek-ai/deepseek-harness/discussions/560) | 一晚 10e token，缓存命中 99.7%（正反馈） | 第 5/6 章缓存专题 |
| [#564](https://github.com/deepseek-ai/deepseek-harness/discussions/564) | 同 #559（思考强度自动测定 + 方言修复） | 同 #559 |
| [#566](https://github.com/deepseek-ai/deepseek-harness/discussions/566) | GLM-5.2 接入后中文经常乱码 | 第 8 章第三方模型坑 |
| [#567](https://github.com/deepseek-ai/deepseek-harness/discussions/567) | web_search 对非官方 Anthropic 兼容代理 key 报 401 且无诊断 | 同 #408 家族 |
| [#599](https://github.com/deepseek-ai/deepseek-harness/discussions/599) | 会话 ID 不发送为 metadata.user_id → 网关无法按会话归属用量 | 第 8 章网关计费 |
| [#611](https://github.com/deepseek-ai/deepseek-harness/discussions/611) | 怎么接入其他大模型（高频入门问题） | 第 8 章（已有，补充） |
| [#614](https://github.com/deepseek-ai/deepseek-harness/discussions/614) | `supportsDeveloperRole: false` 正确格式疑问 | 同 #280 家族 |
| [#615](https://github.com/deepseek-ai/deepseek-harness/discussions/615) | 所有工具调用 `unknown tool ""`（Windows+pwsh） | 同 #161 家族 |
| [#636](https://github.com/deepseek-ai/deepseek-harness/discussions/636) | 配置 reasoningEfforts 后报 400 unknown variant developer | 同 #280 家族 |
| [#691](https://github.com/deepseek-ai/deepseek-harness/discussions/691) | 选 opencode-go 渠道扣费却走官方 API | 第 8 章路由坑 |
| [#693](https://github.com/deepseek-ai/deepseek-harness/discussions/693) | 聊着聊着吐英文（与 #320 同源） | 同 #320 |
| [#694](https://github.com/deepseek-ai/deepseek-harness/discussions/694) | tool 调用 `unknown tool ""`（code 模式） | 同 #161 家族 |
| [#707](https://github.com/deepseek-ai/deepseek-harness/discussions/707) | MCP 需要 node20、dsh 需要 node22，版本冲突怎么办 | 第 9 章 MCP 环境 |
| [#722](https://github.com/deepseek-ai/deepseek-harness/discussions/722) | 其他模型没有推理等级 | 同 #122 家族 |
| [#725](https://github.com/deepseek-ai/deepseek-harness/discussions/725) | **unknown tool "" 根因：SSE 流式解析覆盖赋值而非累加**（附修复验证） | 同 #161 家族（根因版） |
| [#736](https://github.com/deepseek-ai/deepseek-harness/discussions/736) | 自定义模型支持思考强度配置？ | 同 #122 家族 |
| [#739](https://github.com/deepseek-ai/deepseek-harness/discussions/739) | 思考模式下工具调用 400：reasoning_content 未回传 | 同 #231 家族 |
| [#740](https://github.com/deepseek-ai/deepseek-harness/discussions/740) | `llm.discoverModels` 始终失败（registerDiscovery 无调用点） | 第 8 章模型发现坑 |
| [#741](https://github.com/deepseek-ai/deepseek-harness/discussions/741) | 安装完成即 `Error: unknown tool` | 同 #161 家族 |
| [#762](https://github.com/deepseek-ai/deepseek-harness/discussions/762) | 自动路由分发功能 + harness 禁多模态看图 | 第 8 章 |
| [#763](https://github.com/deepseek-ai/deepseek-harness/discussions/763) | **会话内切换模型后 reasoning 永久丢失，思考全混入正文** | **内容缺口**：切换模型副作用 |
| [#784](https://github.com/deepseek-ai/deepseek-harness/discussions/784) | 自定义多模态模型回答完切不回文本模型 | 同 #763 家族 |
| [#779](https://github.com/deepseek-ai/deepseek-harness/discussions/779) | 联网搜索能否兼容其他模型（写死 DeepSeek） | 同 #408 家族 |

### 2.5 性能 / 稳定性

| 帖号 | 核心内容摘要 | 白皮书融入建议 |
|---|---|---|
| [#62](https://github.com/deepseek-ai/deepseek-harness/discussions/62) | 项目感觉杂：skill 未按需加载、sandbox 一言难尽、缓存命中率不高 | 第 6 章对照（与 pi 对比） |
| [#115](https://github.com/deepseek-ai/deepseek-harness/discussions/115) | 新版主页 CPU 100% | 第 6 章性能坑 |
| [#131](https://github.com/deepseek-ai/deepseek-harness/discussions/131) | **子代理无上限派生嵌套 56 个拖死 web 服务**（2.2GB 内存，单核满载 20 分钟） | **内容缺口**：子代理资源失控 |
| [#211](https://github.com/deepseek-ai/deepseek-harness/discussions/211) | 上下文到一定长度浏览器卡死 | 第 6 章 |
| [#238](https://github.com/deepseek-ai/deepseek-harness/discussions/238) | **TokenMeter 每个会话事件重建完整快照 → 二次方级性能退化**（32K 事件 3.5 倍） | **内容缺口**：前端性能根因分析 |
| [#304](https://github.com/deepseek-ai/deepseek-harness/discussions/304) | goal 模式页面太卡，切换会话无反应 | 第 6 章 |
| [#317](https://github.com/deepseek-ai/deepseek-harness/discussions/317) | **超长回合（50 分钟/23.9 万 chunk）→ Web 卡死 + 历史加载失败（Maximum call stack）** | **内容缺口**：超长会话历史加载失败家族根因 |
| [#359](https://github.com/deepseek-ai/deepseek-harness/discussions/359) | 长任务对话后页面卡死（建议虚拟滚动） | 同 #317 家族 |
| [#370](https://github.com/deepseek-ai/deepseek-harness/discussions/370) | 20 万 token 会话历史加载失败（paginate 展开 14.5 万参数） | 同 #317 家族 |
| [#376](https://github.com/deepseek-ai/deepseek-harness/discussions/376) | 存储空间用尽时 agent 卡在转圈 | 第 6 章 |
| [#452](https://github.com/deepseek-ai/deepseek-harness/discussions/452) | 时间一长就卡顿 | 同 #238 家族 |
| [#470](https://github.com/deepseek-ai/deepseek-harness/discussions/470) | 隧道/低带宽下历史加载失败（50 条消息 900KB 无 gzip + 30s 超时） | 同 #317 家族（网络侧） |
| [#477](https://github.com/deepseek-ai/deepseek-harness/discussions/477) | **高并发下用户输入延迟数分钟**（被排队在繁忙 turn 后，无"排队中"提示） | **内容缺口**：并发输入延迟 |
| [#479](https://github.com/deepseek-ai/deepseek-harness/discussions/479) | 高负载下新用户请求完全不显示（gap-repair 吃掉 user/message） | 同 #477 家族 |
| [#483](https://github.com/deepseek-ai/deepseek-harness/discussions/483) | 强制 kill 后重启，write-behind 批处理丢失未刷新尾部 | 同 #477 家族 |
| [#494](https://github.com/deepseek-ai/deepseek-harness/discussions/494) | 会话统计条截断且省略号切在数字中间 | 第 5 章 UI 小坑 |
| [#501](https://github.com/deepseek-ai/deepseek-harness/discussions/501) | 长会话历史加载失败（Maximum call stack，同 #317） | 同 #317 家族 |
| [#508](https://github.com/deepseek-ai/deepseek-harness/discussions/508) | 133,679 个 sourceEventSeqs 超 V8 参数上限 | 同 #317 家族（根因） |
| [#534](https://github.com/deepseek-ai/deepseek-harness/discussions/534) | 20 万输出 tok 会话历史加载失败 | 同 #317 家族 |
| [#548](https://github.com/deepseek-ai/deepseek-harness/discussions/548) | 历史加载失败且刷新无法重载 | 同 #317 家族 |
| [#560](https://github.com/deepseek-ai/deepseek-harness/discussions/560) | 缓存命中 99.7%（正面数据） | 第 5 章缓存专题 |
| [#624](https://github.com/deepseek-ai/deepseek-harness/discussions/624) | 长会话 DOM 全内存导致 10s 级延迟，建议 IndexedDB offloading | 同 #238 家族 |
| [#671](https://github.com/deepseek-ai/deepseek-harness/discussions/671) | **WebSocket 下行无背压 → 慢客户端上 bufferedAmount 无限增长（内存泄漏）** | **内容缺口**：WS 内存泄漏 |
| [#676](https://github.com/deepseek-ai/deepseek-harness/discussions/676) | subagent catalog 条目从不回收 → 内存线性增长 | 同 #238 家族 |
| [#677](https://github.com/deepseek-ai/deepseek-harness/discussions/677) | PartialAccumulator 稀疏块压缩 → 流式内容中途 remount（闪烁/卡顿） | 同 #238 家族 |
| [#682](https://github.com/deepseek-ai/deepseek-harness/discussions/682) | 无限尝试工具调用失败不停 → 浏览器卡顿 | 第 6 章 |
| [#724](https://github.com/deepseek-ai/deepseek-harness/discussions/724) | 两个会话跑一晚 Chrome 内存占用过高 | 同 #238 家族 |
| [#729](https://github.com/deepseek-ai/deepseek-harness/discussions/729) | 处理数据任务想着想着进死循环 | 第 6 章 |
| [#754](https://github.com/deepseek-ai/deepseek-harness/discussions/754) | **大型任务 Javascript heap out of memory**（139 并行子代理，跑到 90+ 崩） | 同 #131 家族 |
| [#660](https://github.com/deepseek-ai/deepseek-harness/discussions/660) | wakeDriver() dispose 期同步抛错 → agent 永久卡 running | 第 6 章 |
| [#661](https://github.com/deepseek-ai/deepseek-harness/discussions/661) | 流式失败重试后，失败 chunk 成孤儿日志数据（幻影内容/重复计费） | 第 6 章 |

### 2.6 安全（社区自发性安全审计，含金量极高）

| 帖号 | 核心内容摘要 | 白皮书融入建议 |
|---|---|---|
| [#76](https://github.com/deepseek-ai/deepseek-harness/discussions/76) | `--host 0.0.0.0` 被官方故意拒绝（防止远程 RCE 暴露） | 第 8 章安全设计 |
| [#130](https://github.com/deepseek-ai/deepseek-harness/discussions/130) | **安全建议：远程认证完善前勿绕过 loopback 限制**（完整攻击链：key 泄露/上下文泄露/配置篡改/SSRF） | **内容缺口**：安全边界科普（第 8 章） |
| [#138](https://github.com/deepseek-ai/deepseek-harness/discussions/138) | danger-full-access 会话 pwsh 仍广告 escalation 选项（噪音） | 第 8 章 |
| [#149](https://github.com/deepseek-ai/deepseek-harness/discussions/149) | **workspace-write 下可递归删除整个工作区零确认** | **内容缺口**：权限边界真实风险（第 8 章） |
| [#159](https://github.com/deepseek-ai/deepseek-harness/discussions/159) | **fs-sandbox post-check pathname race 绕过 workspace-write 文件边界**（confused deputy） | **内容缺口**：沙箱 race 细节 |
| [#226](https://github.com/deepseek-ai/deepseek-harness/discussions/226) | settings 密钥脱敏缺口（union/intersect/transform 内 role('secret') fail-open） | 第 8 章安全 |
| [#243](https://github.com/deepseek-ai/deepseek-harness/discussions/243) | **workflow 工具 vm 逃逸**（宿主域闭包注入，一行表达式逃出） | **内容缺口**：vm 非安全边界（第 9/12 章） |
| [#250](https://github.com/deepseek-ai/deepseek-harness/discussions/250) | **Web approval 回环通道：模型自批准 danger-full-access**（真实复现） | **内容缺口**：approval 回环（第 8 章） |
| [#268](https://github.com/deepseek-ai/deepseek-harness/discussions/268) | taskkill 当前目录劫持（同 2.2） | 第 8 章 |
| [#278](https://github.com/deepseek-ai/deepseek-harness/discussions/278) | **/tmp workspace 可被受限 child rebind 拓宽 workspace-write 授权** | 同 #159 家族 |
| [#381](https://github.com/deepseek-ai/deepseek-harness/discussions/381) | **localhost Web 可被跨站 iframe 点击劫持**（诱导授权 Full access） | **内容缺口**：clickjacking（第 8 章） |
| [#397](https://github.com/deepseek-ai/deepseek-harness/discussions/397) | CLI 0.0.0.0 检查可被 cordis.patch.yml 绕过 + 特权方法仍钉死 loopback | 同 #76 家族 |
| [#451](https://github.com/deepseek-ai/deepseek-harness/discussions/451) | **vm 沙箱逃逸 ×2 + 本地 /api RPC 无鉴权（CVSS 8.8）** | **内容缺口**：系统性安全清单（第 12 章） |
| [#454](https://github.com/deepseek-ai/deepseek-harness/discussions/454) | **第三方安全审计完整报告**（13 个可复现 demo + 证据附录） | **内容缺口**：引用第三方审计（第 12 章） |
| [#460](https://github.com/deepseek-ai/deepseek-harness/discussions/460) | hooks timeout: 0 静默禁用 hook（fail-open） | 第 8 章 |
| [#461](https://github.com/deepseek-ai/deepseek-harness/discussions/461) | **Full Access 模式误删整个家目录**（真实事故，沙盒保护之重要） | **内容缺口**：真实事故案例（第 8 章警告） |
| [#466](https://github.com/deepseek-ai/deepseek-harness/discussions/466) | 沙箱内 agent 可 taskkill 杀宿主（WRITE RESTRICTED 不限进程），turn 永久"运行中" | 同 #451 家族 |
| [#468](https://github.com/deepseek-ai/deepseek-harness/discussions/468) | danger-full-access 下重试带 sandbox_permissions 被拒（误读为权限失效） | 第 8 章权限语义 |
| [#492](https://github.com/deepseek-ai/deepseek-harness/discussions/492) | **提议评测隔离模式**：当前只限写不限读，workspace 外内容可被读到 | **内容缺口**：评测隔离（第 10 章） |
| [#523](https://github.com/deepseek-ai/deepseek-harness/discussions/523) | **Web minimal preset 在 Windows 上允许 workspace 外写入**（无审批） | **内容缺口**：权限预设不一致 |
| [#587](https://github.com/deepseek-ai/deepseek-harness/discussions/587) | **第三方插件 boot 期有全配置树写权限**，`dsh plugin add` 无签名/来源校验 | **内容缺口**：插件信任边界（第 7/8 章） |
| [#674](https://github.com/deepseek-ai/deepseek-harness/discussions/674) | 崩溃后 .tmp 明文会话残留（同 2.2） | 第 8 章 |
| [#774](https://github.com/deepseek-ai/deepseek-harness/discussions/774) | 工作流预设依赖使默认会话暴露 vm 逃逸面 | 同 #243 家族 |
| [#778](https://github.com/deepseek-ai/deepseek-harness/discussions/778) | node:vm 逃逸详细分析（agent() 等函数注入宿主域） | 同 #243 家族 |
| [#792](https://github.com/deepseek-ai/deepseek-harness/discussions/792) | 建议打开 security.md 规范漏洞报告渠道 | 第 7 章参与路径 |

### 2.7 生态（社区补位 + Show and tell）

| 帖号 | 核心内容摘要 | 白皮书融入建议 |
|---|---|---|
| [#14](https://github.com/deepseek-ai/deepseek-harness/discussions/14) | 求 memory 能力（迁移 codex/claude memory 的方案） | 第 7 章 memory 需求 |
| [#45](https://github.com/deepseek-ai/deepseek-harness/discussions/45) | 求 TUI（Linux 是 AI 主战场） | 第 7 章 CLI/TUI 需求 |
| [#67](https://github.com/deepseek-ai/deepseek-harness/discussions/67) | 社区手搓 CLI 中（17 评论） | 同 #45 家族 |
| [#90](https://github.com/deepseek-ai/deepseek-harness/discussions/90) | 支持 SSH 远程连接项目 | 第 7/11 章 |
| [#95](https://github.com/deepseek-ai/deepseek-harness/discussions/95) | 与 pi/opencode/claudecode/codex 性能对比求测 | 第 1 章/benchmark |
| [#118](https://github.com/deepseek-ai/deepseek-harness/discussions/118) | "夯还是拉"（23 评论，用户口碑讨论） | 第 1 章用户视角 |
| [#123](https://github.com/deepseek-ai/deepseek-harness/discussions/123) | 观望者问：缓存命中/占用/三方模型/多模态 | 第 1 章 |
| [#132](https://github.com/deepseek-ai/deepseek-harness/discussions/132) | **Phi CLI（用 Pi 造的 dsh 兄弟 CLI）** | 第 7 章生态列表 |
| [#136](https://github.com/deepseek-ai/deepseek-harness/discussions/136) | Android/Termux 无法运行（npx 安装失败） | 第 12 章平台限制 |
| [#162](https://github.com/deepseek-ai/deepseek-harness/discussions/162) | **desktop-app（bundesk 打包，rc.5）** | 第 7 章桌面端列表 |
| [#165](https://github.com/deepseek-ai/deepseek-harness/discussions/165) | **dsh-browser：Chrome 侧边栏扩展让 DSH 操作浏览器**（免视觉能力） | 第 7 章插件案例 |
| [#167](https://github.com/deepseek-ai/deepseek-harness/discussions/167) | **headless 打印 session-id + 支持 --resume/--continue**（CI 多阶段） | **内容缺口**：headless 续跑能力（第 2 章） |
| [#172](https://github.com/deepseek-ai/deepseek-harness/discussions/172) | 求独立客户端+CLI+VSCode 插件（26 评论高热度） | 第 7 章需求热度 |
| [#174](https://github.com/deepseek-ai/deepseek-harness/discussions/174) | dsh-tool-policy：统一工具策略缝（含三方/MCP） | 第 7 章 |
| [#182](https://github.com/deepseek-ai/deepseek-harness/discussions/182) | **dsh-launcher：Windows WebView2 桌面启动器**（开机自启） | 第 7 章桌面端列表 |
| [#188](https://github.com/deepseek-ai/deepseek-harness/discussions/188) | 求国内仓库镜像（gitee） | 第 7 章国内生态 |
| [#192](https://github.com/deepseek-ai/deepseek-harness/discussions/192) | **dsh-memory 设计提案**（Service Definition/Provider/Consumer 三角色） | 第 7 章 memory 插件 |
| [#215](https://github.com/deepseek-ai/deepseek-harness/discussions/215) | **Awesome DSH Plugin 精选列表**（中英双语） | 第 7 章资源列表 |
| [#218](https://github.com/deepseek-ai/deepseek-harness/discussions/218) | 官方会做内置 Memory 吗？（Memorix/Engram 挂载方案） | 同 #14 家族 |
| [#227](https://github.com/deepseek-ai/deepseek-harness/discussions/227) | Electron 打包 web（社区桌面） | 第 7 章桌面端列表 |
| [#229](https://github.com/deepseek-ai/deepseek-harness/discussions/229) | Tailscale Serve 远程访问适配（手机用） | 第 7/12 章远程方案 |
| [#239](https://github.com/deepseek-ai/deepseek-harness/discussions/239) | **DeepSeek Harness Desktop（macOS 原生壳）** | 第 7 章桌面端列表 |
| [#242](https://github.com/deepseek-ai/deepseek-harness/discussions/242) | **Tailscale+nginx 绕 loopback 远程访问全流程**（4 步骗过 dsh） | 第 12 章远程访问实战 |
| [#248](https://github.com/deepseek-ai/deepseek-harness/discussions/248) | Android ROM 禁 link() 原子发布失败 → rename fallback 提案 | 第 12 章 |
| [#263](https://github.com/deepseek-ai/deepseek-harness/discussions/263) | **QwenAudio 语音对话插件**（全双工 + barge in + 唤醒词） | 第 7 章插件案例 |
| [#272](https://github.com/deepseek-ai/deepseek-harness/discussions/272) | 桥接插件家族（同 2.3） | 第 7 章迁移专题 |
| [#276](https://github.com/deepseek-ai/deepseek-harness/discussions/276) | **BitFun 三个集成实验**（Tauri GUI/MCP bridge/Rust runtime） | 第 7 章集成案例 |
| [#279](https://github.com/deepseek-ai/deepseek-harness/discussions/279) | Electron macOS 桌面（steven-kid） | 第 7 章桌面端列表 |
| [#282](https://github.com/deepseek-ai/deepseek-harness/discussions/282) | **本白皮书（dsh-handbook）自己的 Show and tell** | 第 7 章（自引用） |
| [#303](https://github.com/deepseek-ai/deepseek-harness/discussions/303) | 单独出 CLI（低配置 VPS 用） | 同 #45 家族 |
| [#308](https://github.com/deepseek-ai/deepseek-harness/discussions/308) | **claude_to_dsh：Claude Code 历史同步进 dsh**（100MB→3.9MB） | 第 7 章迁移案例 |
| [#310](https://github.com/deepseek-ai/deepseek-harness/discussions/310) | 求插件收集网站/仓库 | 同 #215 家族 |
| [#315](https://github.com/deepseek-ai/deepseek-harness/discussions/315) | dsh-archive-manager：删除归档对话 | 第 7 章插件案例 |
| [#318](https://github.com/deepseek-ai/deepseek-harness/discussions/318) | **dsh-plugin-cost-tracker：token 费用实时追踪** | 第 7 章插件案例 |
| [#319](https://github.com/deepseek-ai/deepseek-harness/discussions/319) | PlainDeck MCP：Git 做撤销键的幻灯片 | 第 7/9 章 MCP 案例 |
| [#326](https://github.com/deepseek-ai/deepseek-harness/discussions/326) | "Everything is a Plugin" 用户侧成本（配置复杂度） | 第 1 章辩证视角 |
| [#327](https://github.com/deepseek-ai/deepseek-harness/discussions/327) | 本白皮书 3 Agent 实测对比帖 | benchmark |
| [#341](https://github.com/deepseek-ai/deepseek-harness/discussions/341) | 开放 Issues/PR（8 评论） | 第 7 章参与路径 |
| [#343](https://github.com/deepseek-ai/deepseek-harness/discussions/343) | **dsh-superpowers：Superpowers 14 个开发 Skill 带入 dsh** | 第 7 章插件案例 |
| [#344](https://github.com/deepseek-ai/deepseek-harness/discussions/344) | 模型收不到当前时间（web_search 参数停在训练年份，已修复分支） | 第 8 章上下文注入 |
| [#350](https://github.com/deepseek-ai/deepseek-harness/discussions/350) | **DSH Cowork：doc_read/doc_write（xlsx/pdf/docx/pptx/ipynb）** | 第 7 章插件案例 |
| [#354](https://github.com/deepseek-ai/deepseek-harness/discussions/354) | Windows 一键启动 bat 脚本 | 第 2 章便捷启动 |
| [#357](https://github.com/deepseek-ai/deepseek-harness/discussions/357) | 文本模型 + 视觉工具时可放行图片上传 | 同 #321 家族 |
| [#358](https://github.com/deepseek-ai/deepseek-harness/discussions/358) | Electron 桌面客户端提案（commit 就绪等合入） | 第 7 章桌面端 |
| [#361](https://github.com/deepseek-ai/deepseek-harness/discussions/361) | **插件生态发展预测**（前三个月活跃→水化/弃用/无治理；官方自产配套） | 第 11 章生态展望 |
| [#363](https://github.com/deepseek-ai/deepseek-harness/discussions/363) | 移动端支持投票 | 第 12 章 |
| [#364](https://github.com/deepseek-ai/deepseek-harness/discussions/364) | 真需要 CLI（3 评论） | 同 #45 家族 |
| [#384](https://github.com/deepseek-ai/deepseek-harness/discussions/384) | **visionDS：多提供商视觉/OCR skill 安装包** | 第 7 章插件案例（README 已引用） |
| [#386](https://github.com/deepseek-ai/deepseek-harness/discussions/386) | 从 git 历史恢复带 CLI/TUI 的旧版（CatchCatOoO fork） | 第 7 章 CLI 历史 |
| [#391](https://github.com/deepseek-ai/deepseek-harness/discussions/391) | **deepseek-harness-tui：Ink 终端原生 TUI 插件**（~800 行 UI） | 第 7 章 CLI/TUI 案例 |
| [#392](https://github.com/deepseek-ai/deepseek-harness/discussions/392) | 建议把社区 TUI 纳入官方 examples（README 已回应） | 第 7 章 |
| [#394](https://github.com/deepseek-ai/deepseek-harness/discussions/394) | **dsh-portable-launcher：Windows 免装 Node 一键启动** | 第 2/7 章 |
| [#400](https://github.com/deepseek-ai/deepseek-harness/discussions/400) | cordis 抽象评价：可组合扩展远超 pi | 第 1 章架构评价 |
| [#402](https://github.com/deepseek-ai/deepseek-harness/discussions/402) | 为什么不能 create issue | 第 7 章 |
| [#405](https://github.com/deepseek-ai/deepseek-harness/discussions/405) | 轻量 CLI 扩展（Tomsawyerhu） | 同 #45 家族 |
| [#411](https://github.com/deepseek-ai/deepseek-harness/discussions/411) | **dsh-tool-git：结构化安全 Git 工具**（8 个工具） | 第 7 章插件案例 |
| [#414](https://github.com/deepseek-ai/deepseek-harness/discussions/414) | **免装 Node 安装包：mac DMG / Windows exe**（非官方） | 第 2/7 章 |
| [#415](https://github.com/deepseek-ai/deepseek-harness/discussions/415) | 模仿 pi 实现 tui 模式 | 同 #45 家族 |
| [#416](https://github.com/deepseek-ai/deepseek-harness/discussions/416) | DeepCode CLI（007M7，只支持 ds 模型） | 同 #45 家族 |
| [#419](https://github.com/deepseek-ai/deepseek-harness/discussions/419) | **Windows 桌面一键包**（解压即用，238MB） | 第 2/7 章 |
| [#421](https://github.com/deepseek-ai/deepseek-harness/discussions/421) | 求审查模式（类似 Codex/CC 双模型审查） | 第 8/11 章 |
| [#424](https://github.com/deepseek-ai/deepseek-harness/discussions/424) | dsh-superpowers 一条命令装上（同 #343） | 第 7 章 |
| [#431](https://github.com/deepseek-ai/deepseek-harness/discussions/431) | LLM Provider Fallback Router（生产容灾） | 第 11 章 |
| [#434](https://github.com/deepseek-ai/deepseek-harness/discussions/434) | 桌面应用壳（HaoyueQin，常驻后台） | 第 7 章桌面端列表 |
| [#435](https://github.com/deepseek-ai/deepseek-harness/discussions/435) | **dsh-milestone：会话圆点时间轴导航** | 第 7 章 UI 插件 |
| [#442](https://github.com/deepseek-ai/deepseek-harness/discussions/442) | **DSH Plugin Marketplace：dsh-plugin topic 一键安装器**（450+ 插件） | **内容缺口**：插件市场（第 7 章） |
| [#446](https://github.com/deepseek-ai/deepseek-harness/discussions/446) | deepseek-desktop（免费模型） | 第 7 章桌面端列表 |
| [#448](https://github.com/deepseek-ai/deepseek-harness/discussions/448) | **ds-balance-card：多平台余额/Coding Plan 额度卡片** | 第 7 章插件案例 |
| [#454](https://github.com/deepseek-ai/deepseek-harness/discussions/454) | 第三方安全审计（同 2.6） | 第 12 章 |
| [#456](https://github.com/deepseek-ai/deepseek-harness/discussions/456) | **dsh-tool-describe-image：阿里云百炼视觉，粘贴即识别** | 第 7 章视觉插件案例 |
| [#462](https://github.com/deepseek-ai/deepseek-harness/discussions/462) | 插件运行时验证方法论（同 2.3） | 第 4 章 |
| [#475](https://github.com/deepseek-ai/deepseek-harness/discussions/475) | **PTC 模式真实 PR 体验**：轨迹好用，但 PTC 对模型能力要求更高 | **内容缺口**：PTC/Code Mode 使用建议（第 8 章） |
| [#476](https://github.com/deepseek-ai/deepseek-harness/discussions/476) | 子代理会话未正常结束显示绿色（状态混淆） | 第 9 章 UI 坑 |
| [#478](https://github.com/deepseek-ai/deepseek-harness/discussions/478) | 强制 kill 后孤儿子代理显示绿色（同 #476） | 第 9 章 |
| [#480](https://github.com/deepseek-ai/deepseek-harness/discussions/480) | **pi2dsh：把 Pi 包迁移成 DSH bundle**（fails closed） | 第 7 章迁移专题 |
| [#484](https://github.com/deepseek-ai/deepseek-harness/discussions/484) | 长期记忆插件（MemGPT core memory 风格） | 第 7 章 memory 案例 |
| [#487](https://github.com/deepseek-ai/deepseek-harness/discussions/487) | Android hard link 禁用会话 materialize EACCES（patch 已附） | 第 12 章 |
| [#491](https://github.com/deepseek-ai/deepseek-harness/discussions/491) | **dsh-remote-sandbox：E2B 远程沙箱套件** | 第 7/11 章 |
| [#493](https://github.com/deepseek-ai/deepseek-harness/discussions/493) | dsh-turn-index：turn 索引侧栏 | 第 7 章 UI 插件 |
| [#497](https://github.com/deepseek-ai/deepseek-harness/discussions/497) | **IronLaw 安全插件家族**（完成闸门 + 记忆） | 第 7 章插件案例 |
| [#498](https://github.com/deepseek-ai/deepseek-harness/discussions/498) | **dsh-tool-underseal：哈希密封授权**（替代聊天文本授权） | 第 8 章安全插件 |
| [#503](https://github.com/deepseek-ai/deepseek-harness/discussions/503) | **headless 流式输出 + 结构化事件流（stream-json）**（平台调度方诉求） | **内容缺口**：headless 平台化（第 2 章） |
| [#504](https://github.com/deepseek-ai/deepseek-harness/discussions/504) | ChatGPT 订阅登录 Codex（社区 fork 实现） | 第 7 章 |
| [#505](https://github.com/deepseek-ai/deepseek-harness/discussions/505) | **dsh-codex-provider：OpenAI 设备码 OAuth 插件** | 第 7 章插件案例 |
| [#509](https://github.com/deepseek-ai/deepseek-harness/discussions/509) | **deepseek娘桌宠插件**（16 方向追视） | 第 7 章趣味案例 |
| [#510](https://github.com/deepseek-ai/deepseek-harness/discussions/510) | 桌面 GUI 客户端 feature request（Tauri/Electron） | 同 #172 家族 |
| [#516](https://github.com/deepseek-ai/deepseek-harness/discussions/516) | mindspace session memory（可编辑会话隔离记忆） | 第 7 章 memory |
| [#518](https://github.com/deepseek-ai/deepseek-harness/discussions/518) | **dsh-codex：ChatGPT OAuth + Codex search + 图片输入** | 第 7 章插件案例 |
| [#520](https://github.com/deepseek-ai/deepseek-harness/discussions/520) | 建议 Harness 出 Plus/Pro 订阅（4 评论） | 第 11 章商业展望 |
| [#521](https://github.com/deepseek-ai/deepseek-harness/discussions/521) | dsh-web-attention-badge：角标/标签页/favicon 三处提醒 | 第 7 章 UI 插件 |
| [#525](https://github.com/deepseek-ai/deepseek-harness/discussions/525) | dsh-memory（hermes-agent 移植，MEMORY.md/USER.md） | 第 7 章 memory |
| [#526](https://github.com/deepseek-ai/deepseek-harness/discussions/526) | **dsh-eval-regression：确定性 golden-output 评测插件** | 第 7 章评测工具 |
| [#528](https://github.com/deepseek-ai/deepseek-harness/discussions/528) | **dsh-email：邮件 6 工具 + 审批门** | 第 7 章插件案例 |
| [#529](https://github.com/deepseek-ai/deepseek-harness/discussions/529) | **DeepSeek Desktop：Windows x64 社区安装包** | 第 7 章桌面端列表 |
| [#531](https://github.com/deepseek-ai/deepseek-harness/discussions/531) | **dsh-session-import：Claude/Codex/Reasonix/ZCode 历史导入** | 第 7 章迁移案例 |
| [#533](https://github.com/deepseek-ai/deepseek-harness/discussions/533) | 官方必须出交互式 CLI/TUI（同 #45 家族） | 第 7 章 |
| [#537](https://github.com/deepseek-ai/deepseek-harness/discussions/537) | DSH 桌面版（sleep2agi） | 第 7 章桌面端列表 |
| [#544](https://github.com/deepseek-ai/deepseek-harness/discussions/544) | **dsh-agent-messaging：跨会话 agent 互聊**（多会话并行协作） | 第 7 章插件案例 |
| [#552](https://github.com/deepseek-ai/deepseek-harness/discussions/552) | **dsh-rag-kb：本地 RAG 知识库（Ollama）** | 第 7 章插件案例 |
| [#559](https://github.com/deepseek-ai/deepseek-harness/discussions/559) | 网关方言插件（同 2.4） | 第 8 章 |
| [#565](https://github.com/deepseek-ai/deepseek-harness/discussions/565) | dsh-openclaw-acp：OpenClaw/WeChat 跑 Harness | 第 7 章集成案例 |
| [#569](https://github.com/deepseek-ai/deepseek-harness/discussions/569) | **社区被 AI 低质量评论淹没**，建议 Discussion 公约 | **内容缺口**：社区治理（第 7 章） |
| [#576](https://github.com/deepseek-ai/deepseek-harness/discussions/576) | Windows 桌面快捷方式（14 评论，普通用户痛点） | 第 2 章便捷启动 |
| [#579](https://github.com/deepseek-ai/deepseek-harness/discussions/579) | dsh-exa-mcp：Exa 搜索 MCP | 第 7/9 章 MCP 案例 |
| [#587](https://github.com/deepseek-ai/deepseek-harness/discussions/587) | 插件信任边界（同 2.6） | 第 7 章 |
| [#591](https://github.com/deepseek-ai/deepseek-harness/discussions/591) | 企微助手加不了（8 评论） | 第 7 章官方渠道 |
| [#598](https://github.com/deepseek-ai/deepseek-harness/discussions/598) | **Docker 部署 deepseek-harness** | 第 2 章部署方式 |
| [#600](https://github.com/deepseek-ai/deepseek-harness/discussions/600) | dsh web 不处理 SIGHUP → 关终端即退出（无法后台常驻） | 第 2 章后台运行 |
| [#601](https://github.com/deepseek-ai/deepseek-harness/discussions/601) | "他居然是 web 的不是桌面端"（12 评论） | 第 1 章预期管理 |
| [#607](https://github.com/deepseek-ai/deepseek-harness/discussions/607) | 有人封装桌面应用吗 | 同 #172 家族 |
| [#629](https://github.com/deepseek-ai/deepseek-harness/discussions/629) | **CJK 输入法在 Web 对话框失效**（透明文字+高亮层，组合候选不可见） | **内容缺口**：中文输入法兼容（第 5 章） |
| [#630](https://github.com/deepseek-ai/deepseek-harness/discussions/630) | dsh-k12-lesson-builder：K12 英语课件（PPTX+DOCX 同步） | 第 7 章行业案例 |
| [#632](https://github.com/deepseek-ai/deepseek-harness/discussions/632) | **dsh-academic-research：学术研究插件**（文献/证据矩阵/引用核查） | 第 7 章行业案例 |
| [#638](https://github.com/deepseek-ai/deepseek-harness/discussions/638) | 选择 WSL 工作空间 | 第 12 章 |
| [#641](https://github.com/deepseek-ai/deepseek-harness/discussions/641) | CLI 和 web 分离模式建议 | 第 11 章 |
| [#649](https://github.com/deepseek-ai/deepseek-harness/discussions/649) | dsh doctor 提议（同 2.1） | 第 2 章 |
| [#655](https://github.com/deepseek-ai/deepseek-harness/discussions/655) | **5 个社区项目**：SpecFlow/GitFlow/Guardian/Code Intel/VS Code 客户端 | 第 7 章 |
| [#659](https://github.com/deepseek-ai/deepseek-harness/discussions/659) | @ 选择文件/目录作为上下文（同 2.8） | 第 5 章 |
| [#665](https://github.com/deepseek-ai/deepseek-harness/discussions/665) | WEBUI 移动端适配（手机看鲸鱼娘进度） | 第 12 章 |
| [#670](https://github.com/deepseek-ai/deepseek-harness/discussions/670) | 微信交流群（22 评论） | 第 7 章社区渠道 |
| [#681](https://github.com/deepseek-ai/deepseek-harness/discussions/681) | dsh-builtin-toggles：内置插件可视化开关 | 第 7 章 UI 插件 |
| [#683](https://github.com/deepseek-ai/deepseek-harness/discussions/683) | Tauri 桌面端打包（Mac 无签名问题） | 第 7 章桌面端 |
| [#685](https://github.com/deepseek-ai/deepseek-harness/discussions/685) | 文件管理插件（预览/拖拽/打开资源管理器） | 第 7 章 |
| [#687](https://github.com/deepseek-ai/deepseek-harness/discussions/687) | skill 不支持中文名 | 第 3 章 |
| [#688](https://github.com/deepseek-ai/deepseek-harness/discussions/688) | Oh My DSH 插件聚合仓库 | 第 7 章资源列表 |
| [#692](https://github.com/deepseek-ai/deepseek-harness/discussions/692) | dsh-cost-meter：会话/每日费用+余额 | 第 7 章插件案例 |
| [#697](https://github.com/deepseek-ai/deepseek-harness/discussions/697) | 插件排行榜 | 第 7 章 |
| [#698](https://github.com/deepseek-ai/deepseek-harness/discussions/698) | **workspace rules bridge**：.cursorrules/GEMINI.md/copilot-instructions 复用 | 第 7 章迁移案例 |
| [#703](https://github.com/deepseek-ai/deepseek-harness/discussions/703) | 子 agent 支持 cwd 参数（其他 workspace 完整启动） | 第 9 章 |
| [#704](https://github.com/deepseek-ai/deepseek-harness/discussions/704) | token/墙钟预算功能 | 第 11 章 |
| [#706](https://github.com/deepseek-ai/deepseek-harness/discussions/706) | 允许绑定内网 IP（多设备协同） | 同 #351 家族 |
| [#714](https://github.com/deepseek-ai/deepseek-harness/discussions/714) | **dsh-plugin-hello（最小模板）+ dsh-plugin-browser（Playwright 浏览器插件）** | 第 7 章插件案例 |
| [#723](https://github.com/deepseek-ai/deepseek-harness/discussions/723) | 官方插件商店（防插件投毒） | 第 7 章生态展望 |
| [#732](https://github.com/deepseek-ai/deepseek-harness/discussions/732) | **Outpost SKILL：拆穿方案幻觉** | 第 7 章 skill 案例 |
| [#733](https://github.com/deepseek-ai/deepseek-harness/discussions/733) | **dsh-image-bridge 补丁**：图片改写为本地路径文本 | 同 #112 家族 |
| [#738](https://github.com/deepseek-ai/deepseek-harness/discussions/738) | **dsh-doctor-windows：一键诊断 Windows 环境** | 第 2/7 章 |
| [#759](https://github.com/deepseek-ai/deepseek-harness/discussions/759) | pi2dsh 黑盒验证（39/50 挂载，32/50 工作） | 第 7 章迁移 |
| [#765](https://github.com/deepseek-ai/deepseek-harness/discussions/765) | 桌面端适配 mac Intel | 第 7 章 |
| [#767](https://github.com/deepseek-ai/deepseek-harness/discussions/767) | 桌面应用需求分析（社区方案对比） | 第 7 章桌面端全景 |
| [#769](https://github.com/deepseek-ai/deepseek-harness/discussions/769) | **Harness Desktop：Windows 客户端（SHA256 校验）** | 第 7 章桌面端列表 |
| [#775](https://github.com/deepseek-ai/deepseek-harness/discussions/775) | 稳定版是否开放 Issues/PR（同 #341） | 第 7 章 |
| [#782](https://github.com/deepseek-ai/deepseek-harness/discussions/782) | 官方尽快提供 SSH 能力 | 第 11 章 |
| [#785](https://github.com/deepseek-ai/deepseek-harness/discussions/785) | 交流群（19 评论） | 第 7 章 |
| [#789](https://github.com/deepseek-ai/deepseek-harness/discussions/789) | Electron 桌面壳（官方 npm 自动升级） | 第 7 章桌面端 |
| [#794](https://github.com/deepseek-ai/deepseek-harness/discussions/794) | SSH 能力（类似 zcode） | 第 11 章 |
| [#797](https://github.com/deepseek-ai/deepseek-harness/discussions/797) | **primordial-soup：撞击式记忆适配层** | 第 7 章 memory 前沿 |
| [#798](https://github.com/deepseek-ai/deepseek-harness/discussions/798) | 文件预览功能（三入口+四类预览） | 第 5 章 UI 需求 |

### 2.8 功能需求（Web UI / 交互 / 会话管理）

| 帖号 | 核心内容摘要 | 白皮书融入建议 |
|---|---|---|
| [#29](https://github.com/deepseek-ai/deepseek-harness/discussions/29) | 对话中无法切换使用模式（只能新开对话） | 第 5 章 UI 限制 |
| [#40](https://github.com/deepseek-ai/deepseek-harness/discussions/40) | 会话归档后无法查看/恢复 | 第 5 章 |
| [#42](https://github.com/deepseek-ai/deepseek-harness/discussions/42) | 粘贴文本优化 | 第 5 章 |
| [#63](https://github.com/deepseek-ai/deepseek-harness/discussions/63) | 会话置顶功能 | 第 5 章 |
| [#84](https://github.com/deepseek-ai/deepseek-harness/discussions/84) | 支持 VSCode 插件模式 | 第 7/11 章 |
| [#106](https://github.com/deepseek-ai/deepseek-harness/discussions/106) | 获取可用模型不可全部反选 | 第 8 章模型管理 |
| [#109](https://github.com/deepseek-ai/deepseek-harness/discussions/109) | Ralph 失败接续（failure successor） | 第 9 章工作流 |
| [#124](https://github.com/deepseek-ai/deepseek-harness/discussions/124) | userQuestions 中文文案优化（"上一题/下一题"答题感） | 第 5 章中文化 |
| [#126](https://github.com/deepseek-ai/deepseek-harness/discussions/126) | TUI + Vim/Neovim 集成 | 同 #45 家族 |
| [#134](https://github.com/deepseek-ai/deepseek-harness/discussions/134) | 设置界面内容太少 | 第 5 章 |
| [#146](https://github.com/deepseek-ai/deepseek-harness/discussions/146) | **@ 选择文件功能** | **内容缺口**：@ 文件引用（第 5 章） |
| [#147](https://github.com/deepseek-ai/deepseek-harness/discussions/147) | dsh 终端模式脑洞 | 第 11 章 |
| [#156](https://github.com/deepseek-ai/deepseek-harness/discussions/156) | 轨迹页面选择后无法滚动 | 第 5 章 UI bug |
| [#157](https://github.com/deepseek-ai/deepseek-harness/discussions/157) | WebUI 加文档查看入口 | 第 5 章 |
| [#158](https://github.com/deepseek-ai/deepseek-harness/discussions/158) | workflow 展开后无法收起 | 第 9 章 UI bug |
| [#166](https://github.com/deepseek-ai/deepseek-harness/discussions/166) | 模型选择加搜索栏 | 第 8 章模型管理 |
| [#170](https://github.com/deepseek-ai/deepseek-harness/discussions/170) | 失败对话内容无法编辑 | 第 5 章 |
| [#184](https://github.com/deepseek-ai/deepseek-harness/discussions/184) | 剪切 bug（win10 edge） | 第 5 章 |
| [#195](https://github.com/deepseek-ai/deepseek-harness/discussions/195) | 拖拽 zip/md/代码进对话 | 同 #146 家族 |
| [#200](https://github.com/deepseek-ai/deepseek-harness/discussions/200) | **OpenCode 式回退功能**（工作区修改同步回退） | **内容缺口**：回退/分支（第 5/10 章） |
| [#203](https://github.com/deepseek-ai/deepseek-harness/discussions/203) | Codex 式注释（框选针对性问答） | 第 5 章 |
| [#206](https://github.com/deepseek-ai/deepseek-harness/discussions/206) | 消息修改分支回退 + 任务重试 | 同 #200 家族 |
| [#212](https://github.com/deepseek-ai/deepseek-harness/discussions/212) | **中止后队列内容无法处理**（#465 确认是 bug） | **内容缺口**：队列行为（第 5 章） |
| [#216](https://github.com/deepseek-ai/deepseek-harness/discussions/216) | 后端退出前端无提醒 | 第 5 章 |
| [#228](https://github.com/deepseek-ai/deepseek-harness/discussions/228) | show in finder | 第 5 章 |
| [#233](https://github.com/deepseek-ai/deepseek-harness/discussions/233) | 运行后鼠标只能在限定范围活动 | 第 6 章（环境） |
| [#234](https://github.com/deepseek-ai/deepseek-harness/discussions/234) | 必须支持 @filename 引用 | 同 #146 家族 |
| [#237](https://github.com/deepseek-ai/deepseek-harness/discussions/237) | 移动端响应式布局缺失（技术分析） | 第 12 章 |
| [#254](https://github.com/deepseek-ai/deepseek-harness/discussions/254) | 任务完成后不打勾 | 第 5 章 UI bug |
| [#261](https://github.com/deepseek-ai/deepseek-harness/discussions/261) | @ 只能指定子智能体不能指定文件 | 同 #146 家族 |
| [#264](https://github.com/deepseek-ai/deepseek-harness/discussions/264) | 提问卡着不给选 | 第 6 章 |
| [#266](https://github.com/deepseek-ai/deepseek-harness/discussions/266) | 三端协同 agent | 第 11 章 |
| [#284](https://github.com/deepseek-ai/deepseek-harness/discussions/284) | goal 模式：子 agent 未核验完主 agent 提前 complete | 第 9 章 |
| [#286](https://github.com/deepseek-ai/deepseek-harness/discussions/286) | per-session hook 配置发现 | 第 8 章 |
| [#287](https://github.com/deepseek-ai/deepseek-harness/discussions/287) | headless↔web 能力对齐矩阵 | 第 2 章 |
| [#288](https://github.com/deepseek-ai/deepseek-harness/discussions/288) | seam 稳定性标注（早期采用者） | 第 12 章 |
| [#289](https://github.com/deepseek-ai/deepseek-harness/discussions/289) | 进程级 hooks 配置跨 session 共享 | 第 8 章 |
| [#290](https://github.com/deepseek-ai/deepseek-harness/discussions/290) | Think 按钮无冻结效果 | 第 5 章 UI |
| [#291](https://github.com/deepseek-ai/deepseek-harness/discussions/291) | headless 遇到审批工具行为未定义 | **内容缺口**：headless 审批边界（第 2 章） |
| [#299](https://github.com/deepseek-ai/deepseek-harness/discussions/299) | 工作区根目录无效 + 多目录协同 + 无记忆 | 第 5/12 章 |
| [#300](https://github.com/deepseek-ai/deepseek-harness/discussions/300) | 多语言切换未完全适配 | 第 5 章 |
| [#301](https://github.com/deepseek-ai/deepseek-harness/discussions/301) | 完成回复后整体折叠思考/执行过程 | 第 5 章 UI |
| [#306](https://github.com/deepseek-ai/deepseek-harness/discussions/306) | **项目级插件根**：技能/工具随项目加载 | 第 3 章扩展点 |
| [#309](https://github.com/deepseek-ai/deepseek-harness/discussions/309) | CLI 和 VSCode 插件 | 第 7 章 |
| [#312](https://github.com/deepseek-ai/deepseek-harness/discussions/312) | selectModel 传输失败 → 模型选择器永久锁定 | 第 5 章 UI bug |
| [#332](https://github.com/deepseek-ai/deepseek-harness/discussions/332) | 搜索用旧代模型比较 | 第 6 章 |
| [#336](https://github.com/deepseek-ai/deepseek-harness/discussions/336) | **edit/write 结果不给模型 diff**（只回一行确认） | **内容缺口**：模型可见性设计（第 8 章） |
| [#337](https://github.com/deepseek-ai/deepseek-harness/discussions/337) | 文本文件拖拽附件（.md/.txt 等） | 同 #146 家族 |
| [#339](https://github.com/deepseek-ai/deepseek-harness/discussions/339) | 无法识别 /claude/skill 下软链接 skill | 第 3 章 |
| [#342](https://github.com/deepseek-ai/deepseek-harness/discussions/342) | iPhone 原生 app | 第 11 章 |
| [#347](https://github.com/deepseek-ai/deepseek-harness/discussions/347) | 模型选择加搜索（同 #166） | 第 8 章 |
| [#349](https://github.com/deepseek-ai/deepseek-harness/discussions/349) | **消息回撤功能**（Esc 双击等三种场景） | 同 #200 家族 |
| [#351](https://github.com/deepseek-ai/deepseek-harness/discussions/351) | **dsh web 远程访问/控制端点**（token 认证） | **内容缺口**：远程访问方案（第 12 章） |
| [#360](https://github.com/deepseek-ai/deepseek-harness/discussions/360) | @ 引用文件（同 OpenCode） | 同 #146 家族 |
| [#366](https://github.com/deepseek-ai/deepseek-harness/discussions/366) | 自动切换 flash/pro（Claude 式） | 第 6 章 |
| [#368](https://github.com/deepseek-ai/deepseek-harness/discussions/368) | 复制文件只支持图片格式 | 同 #146 家族 |
| [#378](https://github.com/deepseek-ai/deepseek-harness/discussions/378) | harness 进程中断 → 任务 list 消失 | 第 5 章 |
| [#383](https://github.com/deepseek-ai/deepseek-harness/discussions/383) | **跨对话引用：先挂 session-query 工具，不做 GUI 基座** | 第 9 章 |
| [#390](https://github.com/deepseek-ai/deepseek-harness/discussions/390) | VSCode 插件需求 + peerDeps 太重 | 第 7 章 |
| [#398](https://github.com/deepseek-ai/deepseek-harness/discussions/398) | 会话统计条截断 "…" | 第 5 章 |
| [#403](https://github.com/deepseek-ai/deepseek-harness/discussions/403) | **agent-presets.roots 用户配置被 composeProfile 覆盖**（自定义 preset 根永远不生效） | 第 3 章配置坑 |
| [#418](https://github.com/deepseek-ai/deepseek-harness/discussions/418) | Quote & reply 按钮 | 第 5 章 |
| [#426](https://github.com/deepseek-ai/deepseek-harness/discussions/426) | 小米平板+外接键盘 question cards 不显示 | 第 5 章 |
| [#429](https://github.com/deepseek-ai/deepseek-harness/discussions/429) | 模型配置关闭后污染会话搜索 | 第 5 章 UI bug |
| [#430](https://github.com/deepseek-ai/deepseek-harness/discussions/430) | 无法创建"无工作区"对话 | 第 5 章 |
| [#435](https://github.com/deepseek-ai/deepseek-harness/discussions/435) | dsh-milestone 圆点时间轴（同 2.7） | 第 7 章 |
| [#440](https://github.com/deepseek-ai/deepseek-harness/discussions/440) | Markdown 宽表格截断 | 第 5 章 |
| [#453](https://github.com/deepseek-ai/deepseek-harness/discussions/453) | 并发 sandbox 审批误定向（点 Allow 中止一个调用） | 第 8 章审批 |
| [#464](https://github.com/deepseek-ai/deepseek-harness/discussions/464) | 可读文件只有 PNG/JPG/WebP/GIF | 同 #146 家族 |
| [#465](https://github.com/deepseek-ai/deepseek-harness/discussions/465) | **中止后已 claim 队列消息不重新排队**（#212 根因版） | 同 #212 家族 |
| [#467](https://github.com/deepseek-ai/deepseek-harness/discussions/467) | 会话上下文撤销/重做（dsh-undo PoC） | 同 #200 家族 |
| [#489](https://github.com/deepseek-ai/deepseek-harness/discussions/489) | 消息编辑失败提示脱离消息本体 | 第 5 章 |
| [#494](https://github.com/deepseek-ai/deepseek-harness/discussions/494) | 统计条截断（同 #398） | 第 5 章 |
| [#499](https://github.com/deepseek-ai/deepseek-harness/discussions/499) | 移植 codex 桌宠 | 第 7 章趣味 |
| [#500](https://github.com/deepseek-ai/deepseek-harness/discussions/500) | 一次任务消耗金额是否预期（poll） | 第 6 章成本 |
| [#506](https://github.com/deepseek-ai/deepseek-harness/discussions/506) | agent/turn-starting 与 turn-aborting hooks 提案 | 第 4 章扩展点 |
| [#507](https://github.com/deepseek-ai/deepseek-harness/discussions/507) | 会话列表嵌套文件夹 | 第 5 章 |
| [#512](https://github.com/deepseek-ai/deepseek-harness/discussions/512) | userQuestions 支持 diff 预览 | 第 4 章人机交互 |
| [#513](https://github.com/deepseek-ai/deepseek-harness/discussions/513) | 不存在目录的工作区报 ENOENT 无提示 | 第 5 章 |
| [#515](https://github.com/deepseek-ai/deepseek-harness/discussions/515) | dsh-dev-actions：可复用命令转侧边栏动作 | 第 7 章 |
| [#519](https://github.com/deepseek-ai/deepseek-harness/discussions/519) | 嵌套仓库 AGENTS.md 不注入 | 第 8 章 |
| [#524](https://github.com/deepseek-ai/deepseek-harness/discussions/524) | ToolSearch 分阶段激活提案 | 第 4 章 |
| [#535](https://github.com/deepseek-ai/deepseek-harness/discussions/535) | npx web 报错（3 评论） | 第 2 章 |
| [#538](https://github.com/deepseek-ai/deepseek-harness/discussions/538) | **SSH 端口转发远程访问时无法添加工作区**（picker 弹在服务端桌面） | 同 #351 家族 |
| [#540](https://github.com/deepseek-ai/deepseek-harness/discussions/540) | 粘贴长文本卡顿 | 第 5 章 |
| [#541](https://github.com/deepseek-ai/deepseek-harness/discussions/541) | "Open file" 在宿主机打开且静默失败 | 第 5 章 |
| [#543](https://github.com/deepseek-ai/deepseek-harness/discussions/543) | transport error 隐藏宿主错误详情 | 第 6 章排障 |
| [#546](https://github.com/deepseek-ai/deepseek-harness/discussions/546) | 子代理回复需手动 steer 才注入；默认开 Codex/CC presets | 第 9 章 |
| [#549](https://github.com/deepseek-ai/deepseek-harness/discussions/549) | 多项目切换优化 | 第 5 章 |
| [#550](https://github.com/deepseek-ai/deepseek-harness/discussions/550) | 拖拽非图片文件报错 | 同 #146 家族 |
| [#553](https://github.com/deepseek-ai/deepseek-harness/discussions/553) | （空/占位帖，跳过） | — |
| [#557](https://github.com/deepseek-ai/deepseek-harness/discussions/557) | 自定义模型搜索+全选/反选 | 同 #106 家族 |
| [#562](https://github.com/deepseek-ai/deepseek-harness/discussions/562) | **真实高强度协作反馈工作单**（web search 不可用/子分身重复通知/…） | 第 6 章综合 |
| [#586](https://github.com/deepseek-ai/deepseek-harness/discussions/586) | 子代理确认项不提醒（卡一晚） | 第 9 章 |
| [#590](https://github.com/deepseek-ai/deepseek-harness/discussions/590) | 等子代理时主会话应显示等待中 | 第 9 章 |
| [#593](https://github.com/deepseek-ai/deepseek-harness/discussions/593) | ACP 扩展：steer 活跃 turn | 第 9 章 |
| [#594](https://github.com/deepseek-ai/deepseek-harness/discussions/594) | ACP 流式文本 delta | 第 9 章 |
| [#595](https://github.com/deepseek-ai/deepseek-harness/discussions/595) | 添加工作目录弹窗需激活到最前 | 同 #37 家族 |
| [#596](https://github.com/deepseek-ai/deepseek-harness/discussions/596) | 用量统计仪表盘 | 第 11 章 |
| [#597](https://github.com/deepseek-ai/deepseek-harness/discussions/597) | ACP 支持 session-scoped MCP | 第 9 章 |
| [#604](https://github.com/deepseek-ai/deepseek-harness/discussions/604) | 多会话 UI 插件渲染器扩展点 | 第 4 章 |
| [#608](https://github.com/deepseek-ai/deepseek-harness/discussions/608) | 后台任务详情页（输出+终止按钮） | 第 5 章 |
| [#610](https://github.com/deepseek-ai/deepseek-harness/discussions/610) | Mermaid 流程图渲染 | 第 5 章 |
| [#616](https://github.com/deepseek-ai/deepseek-harness/discussions/616) | 自定义模型 Token 框触发浏览器密码保存 | 第 5 章 |
| [#619](https://github.com/deepseek-ai/deepseek-harness/discussions/619) | 首次启动界面像卡死（需 API key + 工作区两步） | 第 2 章 |
| [#620](https://github.com/deepseek-ai/deepseek-harness/discussions/620) | 动态插件 undefine 后无法恢复 | 第 3 章 |
| [#622](https://github.com/deepseek-ai/deepseek-harness/discussions/622) | 任务追踪不更新 | 第 5 章 |
| [#626](https://github.com/deepseek-ai/deepseek-harness/discussions/626) | 工作区右键菜单 | 第 5 章 |
| [#627](https://github.com/deepseek-ai/deepseek-harness/discussions/627) | macOS Safari Keychain 密码自动填充干扰 | 第 5 章 |
| [#633](https://github.com/deepseek-ai/deepseek-harness/discussions/633) | 文件管理系统（Codex 式预览） | 同 #685 家族 |
| [#634](https://github.com/deepseek-ai/deepseek-harness/discussions/634) | APIKEY 由启动环境提供时只读无法改 | 第 8 章 |
| [#640](https://github.com/deepseek-ai/deepseek-harness/discussions/640) | SSH 重连历史加载失败 | 同 #317 家族 |
| [#646](https://github.com/deepseek-ai/deepseek-harness/discussions/646) | **重连静默丢 pending approval**（resync 清空 + replay 竞态） | 第 8 章 |
| [#651](https://github.com/deepseek-ai/deepseek-harness/discussions/651) | 源码启动怎么加别人插件 | 第 3 章 |
| [#652](https://github.com/deepseek-ai/deepseek-harness/discussions/652) | SSH 隧道执行失败 + 改端口方法 | 同 #351 家族 |
| [#653](https://github.com/deepseek-ai/deepseek-harness/discussions/653) | 反代访问 403 | 同 #153 家族 |
| [#654](https://github.com/deepseek-ai/deepseek-harness/discussions/654) | HTTPS 访问 127.0.0.1 /api 403（localhost 正常，:443 默认端口比较） | 同 #153 家族 |
| [#657](https://github.com/deepseek-ai/deepseek-harness/discussions/657) | edit 总被拦（requires reading first）→ 反复 read+edit | 同 #275 家族 |
| [#667](https://github.com/deepseek-ai/deepseek-harness/discussions/667) | 方向键↑不显示上一条消息 | 第 5 章 |
| [#668](https://github.com/deepseek-ai/deepseek-harness/discussions/668) | 自动重试只有 2 次（公司内网） | 第 6 章 |
| [#672](https://github.com/deepseek-ai/deepseek-harness/discussions/672) | settings-file 外部编辑被静默覆盖 | 第 6 章 |
| [#678](https://github.com/deepseek-ai/deepseek-harness/discussions/678) | 支持 Office 全家桶文件类型 | 第 5 章 |
| [#684](https://github.com/deepseek-ai/deepseek-harness/discussions/684) | 后台子代理汇报迟到 → 最终答复后一串确认回合 | 第 9 章 |
| [#686](https://github.com/deepseek-ai/deepseek-harness/discussions/686) | 自定义模型没有多模态选项 | 同 #112 家族 |
| [#695](https://github.com/deepseek-ai/deepseek-harness/discussions/695) | 配置 API 失败 | 第 8 章 |
| [#696](https://github.com/deepseek-ai/deepseek-harness/discussions/696) | RTL 混合文本渲染错乱 | 第 5 章 |
| [#699](https://github.com/deepseek-ai/deepseek-harness/discussions/699) | 预设选择器文案面向产品用户重写 | 第 5 章 |
| [#702](https://github.com/deepseek-ai/deepseek-harness/discussions/702) | 添加工作区缺即时反馈（macOS picker 延迟） | 第 5 章 |
| [#709](https://github.com/deepseek-ai/deepseek-harness/discussions/709) | 消息预览插件 | 第 7 章 |
| [#713](https://github.com/deepseek-ai/deepseek-harness/discussions/713) | 多选菜单点一个就下一步 | 第 5 章 |
| [#716](https://github.com/deepseek-ai/deepseek-harness/discussions/716) | missing required property "command"（macOS） | 同 #121 家族 |
| [#726](https://github.com/deepseek-ai/deepseek-harness/discussions/726) | 可删除对话 + 多文件夹工作区 + @路径 | 第 5 章 |
| [#728](https://github.com/deepseek-ai/deepseek-harness/discussions/728) | subagent 返回消息出现在主对话框排队队列 | 第 9 章 |
| [#731](https://github.com/deepseek-ai/deepseek-harness/discussions/731) | 插件自动续跑重复显示反馈按钮 | 第 5 章 |
| [#735](https://github.com/deepseek-ai/deepseek-harness/discussions/735) | 单轮 token 消耗显示 | 第 5 章 |
| [#737](https://github.com/deepseek-ai/deepseek-harness/discussions/737) | 内测声明弹窗无法关闭 | 第 2 章 |
| [#744](https://github.com/deepseek-ai/deepseek-harness/discussions/744) | 修改代码后显示 diff | 同 #336 家族 |
| [#756](https://github.com/deepseek-ai/deepseek-harness/discussions/756) | 模型设置页加载提供方目录 403 | 同 #153 家族 |
| [#757](https://github.com/deepseek-ai/deepseek-harness/discussions/757) | 后台任务详情+快捷结束 | 同 #608 家族 |
| [#760](https://github.com/deepseek-ai/deepseek-harness/discussions/760) | 模型选择全选/反选 toggle | 同 #106 家族 |
| [#766](https://github.com/deepseek-ai/deepseek-harness/discussions/766) | 对话锚点导航 | 同 #435 家族 |
| [#772](https://github.com/deepseek-ai/deepseek-harness/discussions/772) | 界面全英文没中文 | 第 5 章 |
| [#773](https://github.com/deepseek-ai/deepseek-harness/discussions/773) | 输入队列拖拽排序 | 第 5 章 |
| [#776](https://github.com/deepseek-ai/deepseek-harness/discussions/776) | plan-mode 快速开关丢关闭通知 | 第 8 章 |
| [#786](https://github.com/deepseek-ai/deepseek-harness/discussions/786) | user 对话加编辑按钮 | 第 5 章 |
| [#787](https://github.com/deepseek-ai/deepseek-harness/discussions/787) | 请求阻塞 | 第 6 章 |
| [#788](https://github.com/deepseek-ai/deepseek-harness/discussions/788) | Composer 发送键可配置（Ctrl+Enter） | 第 5 章 |
| [#790](https://github.com/deepseek-ai/deepseek-harness/discussions/790) | **重连后 ask_user_question 提问框丢失**（agent 永久等待） | 同 #646 家族 |
| [#791](https://github.com/deepseek-ai/deepseek-harness/discussions/791) | python 依赖装虚拟环境超时 | 第 6 章 |
| [#793](https://github.com/deepseek-ai/deepseek-harness/discussions/793) | dsh web 后自动打开浏览器 | 第 2 章 |
| [#796](https://github.com/deepseek-ai/deepseek-harness/discussions/796) | 工具调用组级折叠 | 第 5 章 |
| [#799](https://github.com/deepseek-ai/deepseek-harness/discussions/799) | 设置面板 Esc 关闭整个面板 | 第 5 章 |

---

## 三、白皮书内容缺口清单（尚未覆盖，建议补入）

> 按优先级排序。**缺口 = 白皮书现有章节未系统覆盖、但社区高频/高价值的内容**。

### 🔴 P0（最高频真实问题，FAQ/速查必入）

1. **Windows 中文路径截断家族**（#107 #151 #210 #244 #295 #396 #428 #488 #563 #580 #617 #643 #644 #701 #727 #761 #800 等 17+ 帖，同一根因 readUtf16 低字节 0x00）：白皮书第 3 章提到"端口占用"等坑，但未覆盖此 rc.8 未修复的顶级 bug。→ 建议：第 2 章（工作区选择注意事项）+ FAQ + 第 12 章。
2. **`unknown tool ""` 流式 bug**（#161 #615 #694 #725 #741）：SSE 分块覆盖赋值导致工具名丢失，rc.8 未修复，工具链全部失效。→ 建议：第 6 章踩坑 + FAQ（现象/规避/等修复）。
3. **第三方模型接入的 compat 方言**（#280 #302 #472 #473 #551 #614 #636 #559 #564 #780）：developer role、reasoningEfforts 字段、网关方言——白皮书第 8 章有第三方接入但未覆盖这些坑。→ 建议：第 8 章加"自定义网关兼容矩阵"小节 + FAQ。
4. **历史加载失败 Maximum call stack size exceeded**（#317 #370 #501 #508 #534 #548 #640）：超长回合（20 万 token+）导致 sourceEventSeqs 展开超 V8 参数上限。→ 建议：第 6 章 + FAQ（怎么避免/恢复）。
5. **子代理模型路由继承**（#117 #455）：子代理继承"创建时默认模型"而非"会话当前模型"，第三方 provider 下必报 no API key。→ 建议：第 9 章子代理坑 + FAQ。

### 🟠 P1（安全/架构高价值，第 8/12 章必入）

6. **社区安全审计系列**（#243 #250 #278 #381 #451 #454 #774 #778）：vm 逃逸、approval 回环自批准、clickjacking、/tmp rebind、第三方审计报告（13 复现）。→ 建议：第 12 章新增"社区安全审计发现"小节（白皮书目前仅泛提沙箱）。
7. **权限边界真实风险**（#149 递归删工作区零确认、#461 误删家目录、#523 minimal preset 越权、#587 插件 boot 期全配置写权限）：→ 建议：第 8 章安全小节加真实事故案例。
8. **workflow/动态插件的 vm 非安全边界**（#243 #451 #774 #778）：→ 建议：第 9 章 workflow 节加安全边界警告。

### 🟡 P2（生态全景，第 7 章扩写）

9. **CLI/TUI 社区实现全景**（#391 TUI 插件、#132 Phi、#405 轻量 CLI、#386 恢复 CLI、#415 #416、#167 headless resume 需求、#503 headless 流式）：→ 建议：第 7 章加"社区 CLI/TUI"小节 + 第 11 章展望引用。
10. **桌面端社区实现全景**（#182 #227 #239 #276 #279 #358 #407 #414 #419 #434 #446 #529 #537 #683 #689 #767 #769 #789 等 18+）：→ 建议：第 7 章加"社区桌面端"表格。
11. **memory 社区实现全景**（#192 #484 #525 #516 #544 #795 #797 + #14 #218 需求）：→ 建议：第 7 章加"memory 方案对比"。
12. **视觉桥社区实现全景**（#384 #395 #456 #482 #495 #733 + #112 #245 #321 #356 #357 #474 #561 #588 #625 需求）：→ 建议：第 7 章加"视觉能力方案"（描述桥 vs 路由桥 vs sidecar）。
13. **迁移桥**（#272 #308 #480 #531 #698 #759）：Claude/Codex/OpenCode/Pi/ZCode 配置/会话迁移。→ 建议：第 7 章"从其他工具迁移"小节。
14. **插件市场/发现**（#215 #310 #442 #688）：→ 建议：第 7 章资源列表扩写。
15. **安全审计驱动生态**（#569 社区治理、#723 官方插件商店防投毒、#792 security.md）：→ 建议：第 7 章参与路径。

### 🟢 P3（体验/性能细节，按 ROI）

16. **LAN/远程访问系列**（#76 #130 #153 #242 #313 #322 #351 #367 #397 #437 #514 #538 #652 #653 #654 #706 #755 #764）：403/随机 UUID/反代/隧道——白皮书第 12 章已提跨平台短板，但 403 家族根因（Host/Origin 校验）未讲。→ 建议：第 2 章排障 + FAQ。
17. **性能根因分析**（#131 子代理 56 个拖死、#238 TokenMeter 二次方、#671 WS 无背压、#676 catalog 内存、#754 heap OOM）：→ 建议：第 6 章"资源控制建议"。
18. **CJK/中文本地化**（#320 预设英文思考、#629 输入法、#687 中文 skill、#693 吐英文、#124 文案）：→ 建议：第 5 章中文化小节。
19. **@文件引用/拖拽附件**（#146 #195 #202 #234 #261 #337 #360 #368 #464 #540 #550 #659 #685）：高频 UX 需求，白皮书未提。→ 建议：第 5 章"已知 UX 缺口"。
20. **headless 平台化**（#167 #291 #503）：session-id/resume/流式/审批边界。→ 建议：第 2 章 headless 小节扩写。
21. **PTC/Code Mode 使用建议**（#475 真实 PR 体验、#129 #558 #689 工具坑）：→ 建议：第 8 章 preset 说明。
22. **Windows 沙箱稳定性**（#401 #423 #463 #758 #717）：capability ACE、mkdtemp 自锁、临时目录清理崩溃。→ 建议：第 12 章 Windows 沙箱小节。

---

## 四、对白皮书的具体融入动作建议

| 白皮书位置 | 建议融入内容 | 主要帖号 |
|---|---|---|
| 第 2 章（安装/快速上手） | Node ≥22.19 红线；`--expose-internals` macOS/NixOS 家族；首次 npx 慢；全局安装 vs npx；内测声明/首次启动两步 | #100 #113 #176 #252 #269 #311 #574 #619 #690 #737 #748 #750 #793 |
| 第 3 章（profile/插件） | 全局安装依赖解析；pnpm 依赖环；插件 schema 事故；动态插件不持久化；preset roots 被覆盖；plugin add github 不 append | #55 #204 #223 #297 #382 #403 #620 #651 #656 #708 |
| 第 4 章（插件开发） | 运行时验证方法论（mock llm）；run_code description 坑；Symbol 分裂；hooks 大小写/timeout；MCP 重同步 | #129 #410 #462 #558 #572 #581 #582 #583 #584 #618 #689 #711 #715 #783 |
| 第 5 章（应用场景） | @文件引用缺失；消息回退/编辑；统计条/UI 细节；中文文案/输入法 | #146 #200 #206 #349 #398 #494 #629 #687 #693 #796 |
| 第 6 章（性能调优） | 超长会话历史加载失败；子代理资源失控；WS 背压/内存；缓存 99.7% 正面数据；TPS 对比 | #131 #238 #317 #370 #508 #534 #560 #671 #676 #724 #754 |
| 第 7 章（生态） | 社区 CLI/TUI/桌面/memory/视觉/迁移全景；插件市场；安全审计；治理建议 | #132 #215 #272 #391 #414 #442 #454 #480 #495 #531 #559 #738 #759 |
| 第 8 章（工具/上下文） | 自定义网关 compat；web_search baseURL；模型收不到时间；edit 不给 diff；子代理模型继承 | #167 #199 #280 #320 #336 #344 #408 #455 #472 #559 #599 #763 |
| 第 9 章（MCP/子代理） | 子代理确认不提醒；goal 提前 complete；汇报乱序；vm 安全边界；session-query 跨会话引用 | #284 #383 #455 #586 #590 #684 #728 |
| 第 10 章（复杂案例） | 评测隔离模式（读隔离）；大任务 heap OOM 预防 | #131 #492 #754 |
| 第 11 章（未来展望） | CLI/TUI/桌面官方化；SSH 能力；Plus/Pro；token 预算；插件商店 | #167 #303 #364 #431 #503 #520 #704 #723 #782 #794 |
| 第 12 章（已知不足） | Windows 中文路径截断；沙箱 race/approval 回环/vm 逃逸；第三方审计；移动端；Termux | #107 #159 #243 #250 #363 #381 #451 #454 #463 #589 #629 #758 #778 |
| FAQ（docs/faq.md） | 见《四、FAQ 补充清单》 | 见下 |

---

## 五、方法学与可信度说明

- **数据完整性**：GraphQL `discussions(first:100)` 分页 8 次拉全 780 帖（含 body 全文），无缺页。
- **忠实性**：每帖摘要基于正文前 500 字 + 标题；正文含图片/代码块的以 `[code block]`/`[img]` 占位，摘要不虚构。
- **帖号真实性**：全部引用帖号来自上述 API 返回，已程序化核验存在。
- **时效**：dsh 为 0.1.0-rc.8 时代（2026-08-13 发布后 48h 内），部分 bug 可能已在更新的 rc 修复；引用时请标注版本语境。
