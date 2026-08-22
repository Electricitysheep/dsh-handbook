# 第 16 章 从 Claude Code、Codex 与 OpenCode 迁移

> 本章目标：**带着积累搬家，而不是从零重建**。每类资产给出「在 DSH 里会怎样」的实测结论，全部按 `0.1.0-rc.6` 源码逐项验证。

## TL;DR（本章核心，30 秒版）

1. **一半是免费的**：项目 `CLAUDE.md` 不用搬（DSH 原生就读），`SKILL.md` 格式原样兼容
2. **一半是机械的**：`.mcp.json` 可无损转换（工具名 `mcp__server__tool` 两边完全一致），hooks 有官方桥
3. **自动化**：`npx dsh-movein --from <来源>` 出搬家清单预演，`--apply` 落地；会话历史用 `dsh-chat-import`
4. **搬前先算账**：技能目录每个技能每请求约 28 token，搬你用的，不是你有的

## 16.1 资产对照表（实测）

| Claude Code 资产 | DSH 兼容性 | 实际情况 |
| --- | --- | --- |
| 项目 `CLAUDE.md` | 原生，零改动 | `instructionFileCandidates` 默认含 `CLAUDE.md`，从项目根到 cwd 自动发现 |
| 全局 `~/.claude/CLAUDE.md` | 一个符号链接 | 全局位只认 `$DSH_HOME/AGENTS.md`，链过去即可 |
| 技能（`SKILL.md`） | 格式原样兼容 | 前置元数据按开放对象解析，未知键（`allowed-tools` 等）忽略。注意 `.claude/skills` **不是** DSH 默认技能根，要落到 `~/.dsh/skills` 或 `<项目>/.dsh/skills` |
| MCP（`.mcp.json`） | 无损机械转换 | 每个服务器一行 `dsh-mcp-client` 配置（stdio 与 streamable-http），工具名两边一致，引用它们的技能不用改 |
| hooks | 官方桥，部分事件 | `dsh-hooks-claude-code` 原样跑现有配置，30 个事件映射 7 个，仅 command 型。**坑**：matcher 对 DSH 工具名大小写敏感，`Bash` 匹配不到小写的 `bash` 工具，安全 hook 会静默失效（官方讨论区 #582），修复前 matcher 写小写 |
| 权限规则 | 非原生，可桥接 | DSH 只有三档粗预设。`deny`/`ask` 可在 `tools/pre-execute` 强制执行（社区插件），`allow` 无对应物 |
| 子代理（`.claude/agents`） | 无法直接导入 | DSH 预设是 `agent.cordis.yml` 目录而非 markdown，现实路径是转成技能（前置元数据几乎一致） |
| 斜杠命令（`.claude/commands`） | 无文件等价物 | DSH 命令是代码注册的，用户可调用技能是文件级替代 |
| 会话 | 最难，别手写 | 会话文件是 v0 格式 + zstd 帧 + 严格事件校验，官方明确不承诺兼容。历史会话用 [dsh-chat-import](https://github.com/Nwflower/dsh-chat-import)（13 个来源，可反向导出） |

### Codex 与 OpenCode

| 来源 | 自动迁移 | 保留手动 |
| --- | --- | --- |
| Codex | 全局 `AGENTS.md`、自定义 prompt、`config.toml` 中的 stdio MCP | 审批与沙箱策略 |
| OpenCode | 指令、技能、命令、代理、本地或远程 MCP，支持 V1 / V2 JSONC 优先级 | 会话、权限、插件、多文件或远程指令 |

OpenCode 项目 `AGENTS.md` 由 DSH 原生读取。`{env:VAR}` 会保留为运行时环境变量引用，JSONC 解析失败会在任何写入前阻止 `--apply`。

## 16.2 自动化搬家

```sh
npx dsh-movein            # 预演，出搬家清单，不写任何文件
npx dsh-movein --apply    # 落地
npx dsh-movein --from codex
npx dsh-movein --from opencode
npx dsh-movein --from opencode --apply
npx dsh-movein --reverse  # DSH 里长出来的技能搬回 Claude Code（双栖）
```

也可装成插件让 agent 代劳。`dsh plugin --profile web add dsh-movein` 提供 Claude Code 与 OpenCode 迁移工具，Codex 迁移使用 CLI。

权限规则会输出**迁移差异报告**（几条原样生效、几条映射不了逐条列出），不静默转换。每次搬家在 `~/.dsh/movein-manifest.json` 记录来源与落点。

## 16.3 社区真实踩过的坑（启动相关）

1. **解析不到的包写进 patch 会让 dsh 启动直接失败**（plugin tree failed to load，是 fatal 不是警告）。先装包、装成功再写配置行。
2. **周边包 npm latest 标签落后于核心**（hooks 桥曾是 rc.5 而核心已 rc.6），安装按宿主 dsh 版本锁定。
3. **`dsh-hook-protocol` 是 hooks 桥的 peer 依赖**，宿主安装不带，要一起装。

## 16.4 搬前先算账

技能目录以 system-reminder 注入每个请求：固定包装 143 token，每个技能约 28 token（96 字符描述计）。129 个技能的配置每请求背约 3.8k token，缓存省钱但省不了上下文窗口。**搬你用的技能，不是你有的技能**，描述写短点。复现脚本与方法见 [dsh-movein 的 token 账单实测](https://github.com/sjh9714/dsh-movein/blob/main/docs/token-bill.md)。
