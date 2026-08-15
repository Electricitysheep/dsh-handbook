# 第 2 章：五分钟快速上手

> 本章目标：**跟着做，跑起来**。每一条命令都给出预期输出与常见错误解法。建议打开终端边看边做。

## TL;DR（本章核心，30 秒版）

1. **装**：`npx -y @deepseek-ai/dsh web` → http://127.0.0.1:3080
2. **两种常用模式**：web（对话 UI）/ headless（`dsh --profile headless "任务"`，CI 友好）——官方共四种运行模式（见 2.4.1 总览）
3. **推理档位**：off / low（关闭或弱思考/最快，官方 provider 用 `off`，网关用 `low`）/ high（默认）/ max（最强）——**工具链任务 90% 时间在思考，降档是最快提速**
4. **模型**：`deepseek-v4-flash`（默认，性价比）或 `deepseek-v4-pro`（旗舰）
5. **配置**：`~/.dsh/settings.yaml`（模型 + 推理档位）

<!-- [fix] 结构核验：补齐本章导航（第 2 章原缺失，与第 3-11 章结构保持一致） -->
<details><summary>本章导航</summary>
- [2.1 准备工作（30 秒检查）](#21-准备工作30-秒检查)
  - [Node 版本红线（≥22.19）](#node-版本红线2219)
- [2.2 安装（三种方式）](#22-安装三种方式)
  - [安装坑（社区真实踩过）](#安装坑社区真实踩过)
- [2.3 模式一：Web UI（`dsh web`）](#23-模式一web-uidsh-web)
- [2.4 模式二：Headless（一次性任务，适合脚本/CI）](#24-模式二headless一次性任务适合脚本ci)
  - [2.4.1 官方四种运行模式总览](#241-官方四种运行模式总览)
- [2.5 你的第一个插件：给 web 加个 Git 面板](#25-你的第一个插件给-web-加个-git-面板)
- [2.6 配置与目录速查](#26-配置与目录速查)
- [2.7 命令速查](#27-命令速查)
- [2.8 排障速查](#28-排障速查)
</details>

## 2.1 准备工作（30 秒检查）

| 需要 | 检查命令 | 通过标准 |
|---|---|---|
| **Node.js ≥ 22.19** | `node --version` | `v22.19.0` 或更高（**红线**，见下） |
| npm（随 Node 附带） | `npm --version` | 有版本号即可 |
| 网络 | 能访问 npm registry | 能装包 |
| （可选）DeepSeek API Key | https://platform.deepseek.com | 用于真实对话 |

> 没有 API Key 也能启动 dsh（界面能开），但对话需要 Key。本白皮书示例假设已配置。

### Node 版本红线（≥22.19）

社区实测发现 **Node < 22.19 会触发两个致命缺失**：

| 缺失 API | 报错示例 | 触发帖号 |
|---|---|---|
| `node:zlib` 无 `createZstdDecompress` | `TypeError: zlib.createZstdDecompress is not a function` | [#100](https://github.com/deepseek-ai/deepseek-harness/discussions/100) |
| `AbortSignal.timeout` 未实现 | `AbortSignal.timeout is not a function` | [#311](https://github.com/deepseek-ai/deepseek-harness/discussions/311) |

**Workaround**：用 nvm/volta/fnm 切换到 `22.19.0+`。Node 24 早期版本（如 v24.15）也可能触发 `install-lefthook failed`——若遇此错，pin 到 `22.19.0` 最稳 ([#748](https://github.com/deepseek-ai/deepseek-harness/discussions/748))。

## 2.2 安装（三种方式）

**方式一：直接运行（推荐新手）**

```bash
npx -y @deepseek-ai/dsh --version
```

首次运行会下载 dsh（包体较大，含 40+ 插件模块，约 1-3 分钟）。看到版本号即成功：

<!-- [style] 输出/目录类代码块统一补 text 语言标签 -->
```text
0.1.0-rc.6
```

**方式二：全局安装（推荐频繁使用）**

```bash
npm install -g @deepseek-ai/dsh
dsh --version
```

**方式三：免装 Node 的安装包（新手可选）**

不想装 Node？社区作者 codeAnqiang-ma（[#380](https://github.com/deepseek-ai/deepseek-harness/discussions/380) 插件踩坑帖作者，已授权收录）提供了**免装 Node 的安装包**——mac DMG / Windows exe，底层官方 dsh 原样打包、自带 Node 运行时，零前置依赖：

> [dsh-installers](https://github.com/codeAnqiang-ma/dsh-installers)（非官方，随官方 rc 版本发布对应安装包，含 SHA256 校验）

适合「不想折腾 Node 环境、双击即用」的尝鲜用户；需要插件开发/频繁升级的话仍建议方式一或二。

### 安装坑（社区真实踩过）

| 坑 | 现象 | 解决 | 帖号 |
|---|---|---|---|
| **首次 npx 极慢（Windows）** | `npx dsh web` 首次在 Windows 上 8+ 分钟零反馈，npm 需下载 500+ 包 | 耐心等待；改用 `npm i -g @deepseek-ai/dsh` 后秒启 | [#176](https://github.com/deepseek-ai/deepseek-harness/discussions/176) |
| **pnpm dlx 404** | `pnpm dlx @deepseek-ai/dsh web` 报 `@deepseek-ai/dsh-pty@0.0.1-rc.2` 未发布 | 用 `npx` 或 `npm i -g` 替代 `pnpm dlx` | [#369](https://github.com/deepseek-ai/deepseek-harness/discussions/369) |
| **pnpm 全局装后找不到插件** | `pnpm add -g @deepseek-ai/dsh` 后启动报 `Cannot find package 'cordis-plugin-timer'` | pnpm 全局安装的依赖解析策略与 npm 不同；建议用 `npm i -g` 或 npx | [#55](https://github.com/deepseek-ai/deepseek-harness/discussions/55) |
| **WSL2 上 npx 装不上** | 在 WSL2（Ubuntu 等发行版）里 `npx -y @deepseek-ai/dsh` 安装失败 | 先确认 npm 代理配置；仍不行就**改用源码安装**（社区实测可行） | [#118](https://github.com/deepseek-ai/deepseek-harness/discussions/118) |

> **WSL2 安装注意**：社区在 [#118](https://github.com/deepseek-ai/deepseek-harness/discussions/118) 反映 WSL2 上 `npx` 安装可能失败（Windows 原生侧正常，见该帖"win 上都装好开始玩了"的对照）。排查顺序：① 确认 npm 代理/registry 配置；② 若 `npx` 仍装不上，**先试源码安装**（clone 官方仓库后 `pnpm install`，社区实测可行）。详见该帖评论区。
>
> 全局安装方式对比：**`npm i -g`** 最稳（社区验证最多）；**`npx`** 适合尝鲜；**`pnpm dlx`** 暂不建议（rc 阶段 pty 包未发布到 pnpm 可见 registry）。

## 2.3 模式一：Web UI（`dsh web`）

### 启动

```bash
dsh web
```

预期输出：

```text
dsh web: http://127.0.0.1:3080
```

浏览器打开 http://127.0.0.1:3080。

### 界面认识（对照截图）

![dsh Web UI 对话](./assets/demo-web-chat.png)

| 区域 | 内容 |
|---|---|
| 左栏 | 会话列表 / 工作区切换 / 新建会话 |
| 中栏 | 对话区：输入框、模型选择（`DeepSeek V4 Flash`）、推理等级（`High`） |
| 右侧/底部 | 插件侧边栏（默认空；安装社区插件后出现） |
| 右上 | Session log（会话日志）/ 轨迹（工具调用轨迹） |

### 第一次对话

1. 点「新建会话」
2. 输入框输入：`你好，请用一句话介绍你自己`
3. 回车发送

预期回复类似：

> 你好！我是 DeepSeek 驱动的 AI 编程助手，可以帮你写代码、调试问题、处理文件、搜索资料，以及完成各种开发和办公任务。

### 模型与推理档位

点输入框旁的「选择模型」，打开模型与推理档位选择器：

![dsh 模型选择与推理档位](./assets/demo-model-selector.png)

| 模型 | 定位 |
|---|---|
| `deepseek-v4-flash`（默认） | 性价比：快、便宜，日常够用 |
| `deepseek-v4-pro` | 旗舰：更强，更贵更慢 |

**推理等级**（思考模式三档，2026-08-13 起支持）：

| 档位 | 速度 | 质量 | 建议场景 |
|---|---|---|---|
| `low` | 最快 | 够用 | 简单/确定性任务、批量、工具链廉价轮次 |
| `high`（默认） | 中等 | 好 | 日常 Agent 任务 |
| `max` | 最慢 | 最强 | 复杂推理、长链规划 |

<!-- [fix] 技术准确性核验：上表档位为本白皮书实测环境（pi-ai / opencode-go 网关）所支持。DeepSeek 官方适配器（默认 provider=deepseek-official，llm-deepseek 插件）只接受 `off`（关闭思考，最快）/ `high` / `max` 三档，`low` 会抛 `UNSUPPORTED_REASONING_EFFORT`。在 settings.yaml 里对默认 provider 请使用 `off` / `high` / `max` -->

> 💡 **性能关键认知**：模型在**每次工具调用前都会重新思考**。实测一个"创建文件"任务，思考占 ~90% 墙钟时间；50 步工具链任务思考累计可达数分钟到十几分钟。**调低推理档位是性价比最高的提速手段**（见第 6 章 + 示例提速插件）。

## 2.4 模式二：Headless（一次性任务，适合脚本/CI）

```bash
dsh --profile headless "你好，请用一句话介绍你自己"
```

预期输出（打印结果后进程退出）：

```text
你好！我是 DeepSeek 驱动的 AI 编程助手，可以帮你写代码、调试问题、处理文件、搜索资料，以及完成各种开发和办公任务。
```

**Headless 的核心价值**：
- **自动化**：可进 CI、服务器、cron
- **脚本友好**：非零退出码 = 失败；输出可管道处理
- **会话隔离**：每次调用一个新鲜会话（`--resume` 可恢复，见 `dsh --profile headless --help`）

**实战**：写个脚本每天跑一次"生成日报"：

```bash
dsh --profile headless "读取工作区今天的 git log，生成一份中文日报摘要" > daily-report.md
echo "exit=$?"
```

### 2.4.1 官方四种运行模式总览

> 来源：官方站点 https://deepseek.com/harness/ 与官方仓库 `docs/`（2026-08 快照）。前两节（web / headless）是白皮书实测详讲的；后两种模式官方已公布但白皮书暂未逐项实测。

| 模式 | 一句话 | 用途 | 白皮书覆盖 |
|---|---|---|---|
| **Standard mode**（标准） | 完整工具集 + 浏览器界面 | 日常对话/开发（`dsh web`） | ✅ 2.3 节实测 |
| **Minimal mode**（极简） | 仅 `bash` + `str_replace_editor` 两个工具 | 基准测试、最小攻击面 | ⚠️ 未实测，见官方 docs |
| **Code mode**（代码） | 模型写 TypeScript，在单次程序内编排多轮工具调用 | 长链路自动化、确定性执行 | ⚠️ 未实测，见官方 docs |
| **Creator mode**（创造） | 运行时自检 + 内存内测试 Cordis 插件 + 组合新模式 | 插件开发、快速原型 | ⚠️ 未实测，见官方 docs |

> 对新手：日常用 **Standard（web）**、脚本用 **Headless** 即可；Code/Creator 模式属于进阶能力，等官方文档稳定后再深挖。官方文档站（VitePress）：https://deepseek-harness.github.io/deepseek-harness/

## 2.5 你的第一个插件：给 web 加个 Git 面板

dsh 的侧边栏默认是空的——安装社区插件 `dsh-better-sidebar` 体验"一切皆插件"（详细原理见第 3 章，这里先跑通）：

```bash
# 1. 找到你的 web profile
#    Windows: %USERPROFILE%\.dsh\profiles\web
#    macOS/Linux: ~/.dsh/profiles/web

# 2. 在 package.json 的 dependencies 加一行（link: 指向插件源码）
#    "dsh-better-sidebar": "link:C:\\path\\to\\DSH-better-sidebar"

# 3. 在 cordis.patch.yml 加挂载行
#    - insert:
#        - id: better-sidebar
#          name: dsh-better-sidebar

# 4. 安装并重启
cd ~/.dsh/profiles/web && pnpm install
#    （Windows cmd 下 `~` 不展开，请用：cd %USERPROFILE%\.dsh\profiles\web）
dsh web
```

重启后，右侧出现文件管理 / 终端 / **Git 面板** / 浏览器等标签：

![dsh Git 面板（better-sidebar 插件）](./assets/demo-git-panel.png)

> 图中「拉取远端 / 拉取合并 / 推送」按钮是社区 PR 实现的（见第 5 章案例）——**这就是"插件生态"的运转方式**。

## 2.6 配置与目录速查

首次运行后生成的目录：

```text
~/.dsh/
├── settings.yaml          # 全局设置（模型、推理档位）
├── profiles/              # profile 目录
│   └── web/
│       ├── package.json      # 插件依赖 + 清单
│       └── cordis.patch.yml  # 补丁层（挂载插件）
├── sessions/              # 会话数据
└── storages/              # 持久化存储
```

`settings.yaml` 示例：

```yaml
agent-default-model:
  model: deepseek-v4-flash
  reasoningEffort: high
```

## 2.7 命令速查

| 命令 | 用途 |
|---|---|
| `dsh web` | 启动 Web UI（=`dsh --profile web`） |
| `dsh --profile headless "任务"` | 一次性任务，打印结果退出 |
| `dsh plugin --profile <name> add <pkg>` | 给 profile 安装插件 |
| `dsh --dump-config` | 打印合成配置树 |
| `dsh --profile tui` | TUI 模式（需先安装 tui 插件，官方未内置） |
| `dsh --version` | 版本 |

## 2.8 排障速查

| 现象 | 原因与解法 |
|---|---|
| `dsh: profile "tui" does not exist` | tui profile 需插件创建（`dsh plugin --profile tui add <pkg>`） |
| `npx` 极慢 | 首次下载包体大；`npm i -g` 后更快 |
| 浏览器打不开 3080 | 端口被占：`netstat -ano \| findstr 3080` → kill PID |
| 模型无响应 | 检查 `~/.dsh/settings.yaml` 模型配置 + API Key |
| 插件装不上（404） | **rc.1 依赖断裂**：确认依赖用 `^0.1.0-rc.6` 线（第 3 章常见坑 #1） |
| 升级后行为变了 | rc 阶段破坏性变更正常，看官方 changelog |

---

**下一章**：[第 3 章：profile 与插件系统](./03-profiles.md) —— 理解可定制骨架。

---

> **源码方式启动慢的根因（#1424 社区实测确认）**：`pnpm dsh web` 每次启动用 tsx/esbuild **现场转译整个 TS 源码图**（非全量构建），叠加机械盘/大文件数时冷启动可达数分钟。**实测计时**：tsx 热缓存 ~40s / 冷缓存 ~5min / 编译产物 `lib/bin.js` 版 ~12s（页面响应 5ms）。解决：① 启动命令改用 `node apps\cli\lib\bin.js web`（走编译产物）② 或先 `pnpm build` 全量构建一次 ③ 或直接用 `npx @deepseek-ai/dsh web`（发布版）。
## 动手练习（10 分钟内完成）

1. **安装**：`npx -y @deepseek-ai/dsh --version` 确认版本
2. **Web 对话**：启动 `dsh web`，新会话发"你好"，观察回复与界面布局
3. **Headless**：`dsh --profile headless "1+1 等于几"`，确认打印结果后退出
4. **推理档位实验**：把 settings.yaml 的 `reasoningEffort` 改为 `off`（官方 provider）或 `low`（第三方网关），重新跑一个简单任务，感受速度差异
5. **排障演练**：模拟"端口被占"（先起一个占用 3080 的服务），用 `netstat` 排查

> 全部通过后，进 [第 3 章](./03-profiles.md) 理解"为什么能这样改"。
