# FAQ：常见问题速查

> 汇总各章 FAQ + 全局高频问题，一页速查。找不到答案？去[官方 Discussions](https://github.com/deepseek-ai/deepseek-harness/discussions)提问。

## 入门

**Q：dsh 是模型吗？**
不是。dsh 是运行时/框架，模型通过 `llm` 插件接入（官方适配 DeepSeek V4 系，可接 OpenAI 兼容模型）。

**Q：dsh 和 Claude Code 什么区别？**
Claude Code 是"整车"（开箱即用、封闭），dsh 是"乐高底座"（可定制、开源）。见[第 1 章对比](./01-intro.md)。

**Q：没写过 TypeScript 能玩吗？**
使用完全不需要；写插件需要基础 TS，白皮书给完整代码。

**Q：要花钱吗？**
dsh 本身免费开源；对话需要 DeepSeek API key（按量付费，Flash 很便宜，缓存命中 98% 折扣）。

## 安装与运行

**Q：`npx` 很慢？**
首次下载包体大（40+ 插件模块）。`npm i -g @deepseek-ai/dsh` 后更快。

**Q：浏览器打不开 3080？**
端口被占：`netstat -ano | findstr 3080` → kill PID。

**Q：`dsh --profile tui` 报错？**
tui profile 需插件创建（官方未内置），`dsh plugin --profile tui add <pkg>`。

**Q：首次 `npx` 等了 8 分钟没动静？**
正常——首装要下载 500+ 依赖包（Windows 上尤其慢，[#176](https://github.com/deepseek-ai/deepseek-harness/discussions/176)）。用 `npm i -g @deepseek-ai/dsh` 全局安装，之后免 npx 下载。

**Q：启动报 `--expose-internals is required for HMR service`？**
macOS arm64 / NixOS / 部分 Linux 上 cordis HMR loader 探测不到 Node 内部模块所致（[#113](https://github.com/deepseek-ai/deepseek-harness/discussions/113) [#269](https://github.com/deepseek-ai/deepseek-harness/discussions/269) [#690](https://github.com/deepseek-ai/deepseek-harness/discussions/690)）。临时方案：用 `node --expose-internals <bin> web` 启动；等官方修复。

**Q：端口 3080 报 EACCES，但没进程占用？**
Windows 上 3080 可能落在 Hyper-V/WSL2/Docker Desktop 的保留端口区间内（[#589](https://github.com/deepseek-ai/deepseek-harness/discussions/589)）。`netstat -ano | findstr 3080` 无结果时，先查 `netsh interface ipv4 show excludedportrange protocol=tcp`，或直接 `dsh web --port 13080` 换个端口。

## 模型与性能

**Q：推理档位怎么选？**
> ⚠️ 档位支持因适配器而异：`deepseek-official` 适配器能力表为 `off`/`high`/`max`（`low` 官方 API 实际支持但适配器未暴露）；opencode-go/pi-ai 网关支持 `low`。降档前先确认当前 provider 支持（报 `does not support reasoning effort` = 适配器缺口，映射到最近可用档位即可）。

`low`（简单/批量/工具轮）/ `high`（日常）/ `max`（复杂）。工具链 90% 时间在思考——降档最快提速。

**Q：为什么我的任务慢？**
先看是不是思考档位高 + 是否冷启动。长任务建议 `low` + 会话延续（缓存命中）。

**Q：缓存命中率怎么提升？**
保持会话延续、prompt 前缀稳定、批量同会话。实测可到 97%（见[第 5 章](./05-cases.md)）；社区实测长跑可达 99.7%（[#560](https://github.com/deepseek-ai/deepseek-harness/discussions/560)）。

**Q：第三方模型/自定义网关没有"推理强度"选项？**
rc.6 的 llm-pi-ai 只暴露 `thinkingFormat`/`supportsReasoningEffort`，且手写 provider 的 reasoningEfforts 需在 settings.yaml 手动声明（[#122](https://github.com/deepseek-ai/deepseek-harness/discussions/122) [#302](https://github.com/deepseek-ai/deepseek-harness/discussions/302) [#736](https://github.com/deepseek-ai/deepseek-harness/discussions/736)）。声明后报 `400 unknown variant developer` 是网关不认 developer role——需配 `compat.supportsDeveloperRole: false`（[#280](https://github.com/deepseek-ai/deepseek-harness/discussions/280) [#614](https://github.com/deepseek-ai/deepseek-harness/discussions/614) [#636](https://github.com/deepseek-ai/deepseek-harness/discussions/636)）。社区有自动探测网关方言的插件（[#559](https://github.com/deepseek-ai/deepseek-harness/discussions/559)）。

**Q：所有工具调用都报 `Error: unknown tool ""`？**
rc.6 流式解析 bug：SSE 分块覆盖赋值把工具名/ID 抹成空串（[#725](https://github.com/deepseek-ai/deepseek-harness/discussions/725) 根因 + 修复；[#161](https://github.com/deepseek-ai/deepseek-harness/discussions/161) 同族）。**两类触发根因**：
1. **覆盖赋值**：`translate.ts` 对 `block.name`/`block.callId` 逐分块覆盖而非累加，后续分块带空 `function.name` 时把已解析的工具名抹成空串（帖内主修复：改为 `(block.name ?? '') + ...` 累加）；
2. **null 隐式转字符串**：部分模型（如 hy3、longcat-2.0）在流式 delta 中给 `id`/`name` 填 `null`——`null !== undefined` 恒真，原判断会把 `null` 隐式转成字符串拼接，产出破坏性工具名（如 `"Glob" + null → "Globnull"`）。更彻底的修复是**严格类型校验**：`typeof call.id === 'string'` / `typeof call.function?.name === 'string'` 才累加（#725 评论区补充方案）。

因官方当前关闭 Issue/PR 提交（#725 评论区确认），**需自行修改** `packages/llm/llm-deepseek/src/translate.ts`（对应函数逐分块累加 + 严格类型校验）后 `pnpm run build` 再重启 dsh。官方修复前亦可降级/等版本；模型会反复重试，注意及时中止。

**Q：超长会话打不开，报 `Maximum call stack size exceeded`？**
超长回复（20 万+ token）的 `sourceEventSeqs` 数组被展开成函数参数，超出 V8 参数上限（[#317](https://github.com/deepseek-ai/deepseek-harness/discussions/317) [#370](https://github.com/deepseek-ai/deepseek-harness/discussions/370) [#508](https://github.com/deepseek-ai/deepseek-harness/discussions/508)）。会话文件本身没坏；属 rc 已知缺陷，等修复或找社区补丁。

## 插件开发

**Q：插件装不上（404）？**
rc.1 依赖断裂——确认用 `^0.1.0-rc.6` 线（第 3 章坑 #1）。

**Q：写第一个插件最容易踩哪些坑？（社区六坑）**
来源：官方讨论区 [#380](https://github.com/deepseek-ai/deepseek-harness/discussions/380)「写第一个 dsh 插件踩的六个坑」（作者 codeAnqiang-ma 授权收录，dsh `0.1.0-rc.6` 本机复核，致谢 @codeAnqiang-ma）。忠实提炼：
1. **`@deepseek-ai/*` 能否 import 取决于插件装在哪**：dev `link` 进 profile 时，Node 沿软链接真实路径解析，走不到兜底目录 `~/.dsh/profiles/node_modules`（只有 registry 安装才能撞上）→ 报 `ERR_MODULE_NOT_FOUND`。解法：插件不 import 任何 `@deepseek-ai/*`，全从 `ctx` 上拿；要用 schemastery 写 config schema 就走 peer dependency（registry 形态下通）。
2. **`inject` 只能是字符串数组**：写成 `{ required: [...], optional: [...] }` 会把 `required`/`optional` 当成两个服务名，启动卡在 `pending (waiting for services: required, optional)`。官方包全是数组写法（`["skills"]`、`["systemPrompt"]`、`["agents","tools","skills"]`）。
3. **想成为一层 profile 必须声明 `dsh.bundle`**：`package.json` 加 `"dsh": { "bundle": { "patch": "./cordis.patch.yml" } }`，否则 `dsh plugin add` 装完只是普通依赖、插件毫无动静（警告夹在 pnpm 输出里易漏）。改包名要同步 patch 里的 `name`，否则报 `plugin(s) failed to load`。
4. **prompt section 压缩之后还在（好消息）**：`ctx.systemPrompt.section()` 注册的内容在上下文压缩后依然在——每步从注册表重新组装，不用监听会话事件反复注入、不用写去重守卫。`order` 有约定分段（`-100` harness identity / `0` persona / `100-199` 工具指导），同一 order 按插件加载顺序排（不稳定，自己挑不撞的数）。
5. **Web 面不用改 preset，但 persona 是例外**：skill 注册表与 prompt section 都是「全局层 + scope 链」合并读，全局层注册的每个 agent 都拿得到；但 preset 自挂的 `persona`（`deployment:persona`）按 scope 层同名遮蔽全局，改 profile patch 里的 persona 对 Web 默认会话无效，得改 preset。插件 section 名字带自己前缀就不会被遮。
6. **发 npm 的两个坑**：registry 指国内镜像（只读）时 `npm login`/`npm publish` 都要显式 `--registry=https://registry.npmjs.org`；`npm publish` 只认 `--otp`（没有 `--auth-type` 选项），2FA 只绑 passkey/Touch ID 时拿不出 OTP，得用 TOTP 验证码或恢复码。

> 作者仓库：[dsh-superpowers](https://github.com/codeAnqiang-ma/dsh-superpowers)（Superpowers 方法论插件）。rc 迭代快，若条目失效欢迎指正。

**Q：`agent/request` 的 `next()` 要 await 吗？**
**必须**。不 await 会丢 provider/model 报错（第 4 章坑）。

**Q：怎么写插件最快？**
克隆[插件模板](../examples/plugin-template/)，改纯函数逻辑，挂载即用。想验证 waterfall 行为但没 API key？社区有零成本方案：仓库自带 mock llm + headless + 审计 dump（[#462](https://github.com/deepseek-ai/deepseek-harness/discussions/462)）。

**Q：Code 模式下 run_code/bash 一直报 `missing required property "description"`？**
rc.6 工具参数坑：run_code 与 bash 的 description 字段同名且标 required，模型常把内层 bash.description 当已传，外层缺字段 → 死循环重试（[#558](https://github.com/deepseek-ai/deepseek-harness/discussions/558) [#581](https://github.com/deepseek-ai/deepseek-harness/discussions/581) [#689](https://github.com/deepseek-ai/deepseek-harness/discussions/689)）。遇到时手动补外层 description 或换标准模式。

**Q：分叉（fork）会话里 edit 总报 "edit requires reading ... first"？**
rc.6 bug：fork 新建 session 不继承父会话的"已读文件"观察状态，历史里明明读过、策略却认为没读（[#275](https://github.com/deepseek-ai/deepseek-harness/discussions/275) [#450](https://github.com/deepseek-ai/deepseek-harness/discussions/450)）。重读一次文件即可绕过。

**Q：装完某个插件后 dsh 启动报 `Invalid schema for function ...`？**
插件 schema 写坏或 agent 改坏了 `cordis.patch.yml`，整个 dsh 起不来（[#297](https://github.com/deepseek-ai/deepseek-harness/discussions/297) [#447](https://github.com/deepseek-ai/deepseek-harness/discussions/447) [#708](https://github.com/deepseek-ai/deepseek-harness/discussions/708)）。恢复：删/修 `~/.dsh/profiles/web/cordis.patch.yml` 里对应行，或备份还原。别让 agent 自己装插件改配置前先备份。

**Q：工具调用报 `Cannot read properties of undefined (reading 'prepare')`？**
`@deepseek-ai/dsh-tools` 在进程里存在两份（全局 + profile），模块级 Symbol 分裂导致调度器找不到（[#572](https://github.com/deepseek-ai/deepseek-harness/discussions/572) [#783](https://github.com/deepseek-ai/deepseek-harness/discussions/783)）。清理 profile 里重复的 dsh-tools 依赖即可。

## 安全与生产

**Q：dsh 安全吗？**
工具执行有沙箱 + 审批层。医疗/法律等高风险输出需人工审核。但别掉以轻心：社区审计发现沙箱有真实逃逸面——`node:vm` 不是安全边界（workflow/动态插件可逃逸，[#243](https://github.com/deepseek-ai/deepseek-harness/discussions/243) [#451](https://github.com/deepseek-ai/deepseek-harness/discussions/451) [#774](https://github.com/deepseek-ai/deepseek-harness/discussions/774)）、`workspace-write` 下可递归删除整个工作区（[#149](https://github.com/deepseek-ai/deepseek-harness/discussions/149)）、模型可能经 approval 回环自批准 full access（[#250](https://github.com/deepseek-ai/deepseek-harness/discussions/250)）、localhost Web 可被 iframe 点击劫持（[#381](https://github.com/deepseek-ai/deepseek-harness/discussions/381)）。完整第三方审计见 [#454](https://github.com/deepseek-ai/deepseek-harness/discussions/454)。

**Q：能进生产吗？**
rc 阶段有破坏性变更；核心依赖等 `0.1.0` 正式版，生态玩法现在可入。生产调度侧注意：headless 没有 UI 处理审批请求，行为未定义（[#291](https://github.com/deepseek-ai/deepseek-harness/discussions/291)）；子代理可无上限派生拖死服务（[#131](https://github.com/deepseek-ai/deepseek-harness/discussions/131)）；大任务曾报 heap OOM（[#754](https://github.com/deepseek-ai/deepseek-harness/discussions/754)）。

**Q：为什么禁止 `--host 0.0.0.0`？能绕过吗？**
官方为安全主动拒绝——暴露到网络等于把 RCE/凭据/上下文泄露给不可信网络（[#76](https://github.com/deepseek-ai/deepseek-harness/discussions/76) [#130](https://github.com/deepseek-ai/deepseek-harness/discussions/130)）。绕过的代价很高（改配置/反向代理），远程认证完善前**不建议**。真要远程：SSH 隧道 + 改 Host/Origin 可跑通但步骤繁琐（[#242](https://github.com/deepseek-ai/deepseek-harness/discussions/242)）。

**Q：长任务会崩吗？**
建议全局安装（绕 npx）+ 降推理档 + 观察内存（实测 50 步任务内存显著上涨）。Windows 上 Temp 目录被清理可能让沙箱永久崩溃不自愈（[#758](https://github.com/deepseek-ai/deepseek-harness/discussions/758)）；强制 kill 后重启，正在写的会话可能残留未闭合 turn（[#466](https://github.com/deepseek-ai/deepseek-harness/discussions/466)）。

## Windows 兼容

**Q：选工作区时中文路径被截断（`开`/`一`/`需` 等字后面全丢）？**
rc.6 著名 bug：Windows 原生目录选择器 readUtf16 只查 UTF-16 低字节，遇到低字节为 0x00 的汉字（开 U+5F00、一 U+4E00、需 U+9700 等）就提前截断（[#107](https://github.com/deepseek-ai/deepseek-harness/discussions/107) [#151](https://github.com/deepseek-ai/deepseek-harness/discussions/151) [#563](https://github.com/deepseek-ai/deepseek-harness/discussions/563)）。17+ 帖复现（[#244](https://github.com/deepseek-ai/deepseek-harness/discussions/244) [#580](https://github.com/deepseek-ai/deepseek-harness/discussions/580) 等），社区有 cherry-pick 修复。临时方案：工作区路径避开 U+XX00 字符。

**Q：目录选择框报 `win32 folder dialog worker exited before reporting a result`？**
koffi/native picker 系列崩溃（[#30](https://github.com/deepseek-ai/deepseek-harness/discussions/30) [#154](https://github.com/deepseek-ai/deepseek-harness/discussions/154) [#236](https://github.com/deepseek-ai/deepseek-harness/discussions/236)）。koffi 3.1.3/3.1.4 预编译损坏可锁 3.1.2（[#293](https://github.com/deepseek-ai/deepseek-harness/discussions/293)）；另有 STA CoUninitialize 段错误根因（[#768](https://github.com/deepseek-ai/deepseek-harness/discussions/768)）。

**Q：浏览器打开 127.0.0.1:3080，但 API 全报 403？**
Host/Origin 信任校验问题：用 `http://localhost:3080` 访问通常正常（[#153](https://github.com/deepseek-ai/deepseek-harness/discussions/153) [#313](https://github.com/deepseek-ai/deepseek-harness/discussions/313) [#764](https://github.com/deepseek-ai/deepseek-harness/discussions/764)）。注意服务端打印的地址可能不可用，改 localhost 试试。

**Q：局域网/手机访问报 `crypto.randomUUID is not a function`？**
明文 HTTP 非 loopback 不是安全上下文，`crypto.randomUUID` 不可用，所有 RPC 失败（[#221](https://github.com/deepseek-ai/deepseek-harness/discussions/221) [#367](https://github.com/deepseek-ai/deepseek-harness/discussions/367) [#514](https://github.com/deepseek-ai/deepseek-harness/discussions/514) [#755](https://github.com/deepseek-ai/deepseek-harness/discussions/755)）。rc.6 未带仓库已修的 shim；远程访问别用明文 IP。

**Q：Windows 下调用 pwsh/工具报 `missing required property "command"` 或假死？**
pwsh 调用失败家族（[#121](https://github.com/deepseek-ai/deepseek-harness/discussions/121) [#225](https://github.com/deepseek-ai/deepseek-harness/discussions/225)），最严重时整个 dsh 假死（[#663](https://github.com/deepseek-ai/deepseek-harness/discussions/663)）。涉及沙箱与 PowerShell 组合的已知问题，Windows 用户先降级为 bash（若可用）或等修复。

## 生态

**Q：官方收外部 PR 吗？**
当前明确"暂不接受"（CONTRIBUTING）。走 Discussion 提案 + 社区渠道（见第 7 章）。社区多次呼吁稳定版开放 Issues/PR（[#341](https://github.com/deepseek-ai/deepseek-harness/discussions/341) [#775](https://github.com/deepseek-ai/deepseek-harness/discussions/775)）。

**Q：怎么推广我的插件？**
加 `dsh-plugin` topic + npm 发布 + 官方 Discussion Show-and-tell + awesome 列表（[#215](https://github.com/deepseek-ai/deepseek-harness/discussions/215) 中英双语精选列表）。社区还有一键安装器 DSH Plugin Marketplace（[#442](https://github.com/deepseek-ai/deepseek-harness/discussions/442)）与聚合仓库（[#688](https://github.com/deepseek-ai/deepseek-harness/discussions/688)）。

**Q：想要 CLI / TUI？**
官方暂无，社区已做：TUI 插件（[#391](https://github.com/deepseek-ai/deepseek-harness/discussions/391)）、CLI（[#405](https://github.com/deepseek-ai/deepseek-harness/discussions/405)）、Pi 系 CLI（[#132](https://github.com/deepseek-ai/deepseek-harness/discussions/132)）。headless 续跑（打印 session-id + `--resume`）是社区高频诉求（[#167](https://github.com/deepseek-ai/deepseek-harness/discussions/167)）。

**Q：想要桌面版 / 免装 Node？**
社区有大量打包：mac DMG + Windows exe 安装包（[#414](https://github.com/deepseek-ai/deepseek-harness/discussions/414)）、Windows 一键包（[#419](https://github.com/deepseek-ai/deepseek-harness/discussions/419)）、桌面壳（[#767](https://github.com/deepseek-ai/deepseek-harness/discussions/767) 汇总对比）。均为非官方社区维护。

**Q：想要 memory / 视觉能力？**
官方未内置，社区方案成体系：memory（[#192](https://github.com/deepseek-ai/deepseek-harness/discussions/192) [#484](https://github.com/deepseek-ai/deepseek-harness/discussions/484) [#525](https://github.com/deepseek-ai/deepseek-harness/discussions/525)）、视觉桥（[#456](https://github.com/deepseek-ai/deepseek-harness/discussions/456) [#495](https://github.com/deepseek-ai/deepseek-harness/discussions/495) [#733](https://github.com/deepseek-ai/deepseek-harness/discussions/733)）。从其他工具迁移也有桥接插件（[#272](https://github.com/deepseek-ai/deepseek-harness/discussions/272) [#531](https://github.com/deepseek-ai/deepseek-harness/discussions/531)）。

**Q：企微小助手加不上？**
官方企微渠道被腾讯风控/加爆（[#25](https://github.com/deepseek-ai/deepseek-harness/discussions/25) [#270](https://github.com/deepseek-ai/deepseek-harness/discussions/270) [#591](https://github.com/deepseek-ai/deepseek-harness/discussions/591)），等官方修复；社区自发建了微信群/QQ 群（[#705](https://github.com/deepseek-ai/deepseek-harness/discussions/705) [#730](https://github.com/deepseek-ai/deepseek-harness/discussions/730)）。

---

**更多**：术语表见[附录 A](./appendix-glossary.md) · 命令速查见[一页卡](./cheatsheet.md)
