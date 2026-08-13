# 第 2 章：五分钟快速上手

> 本章目标：装起来，跑起来——用最少的命令体验 dsh 的两种模式，并理解模型与推理档位。

## 2.1 安装

**要求**：Node.js ≥ 22（推荐 24）。一条命令：

```bash
# 直接运行（npx 会自动下载）
npx -y @deepseek-ai/dsh --version

# 或全局安装
npm install -g @deepseek-ai/dsh
dsh --version
```

> ⚠️ **版本注意**：当前为 `0.1.0-rc.x`（开发预览），官方明示"将有破坏性变更"。教程示例基于 `0.1.0-rc.6` 验证。

## 2.2 模式一：Web UI（`dsh web`）

```bash
dsh web
# 输出: dsh web: http://127.0.0.1:3080
```

浏览器打开 http://127.0.0.1:3080：

- 左侧：会话列表 / 工作区
- 中间：对话区（输入框、模型选择、推理等级）
- 右侧/底部：**由插件提供**的侧边栏（默认空，安装社区插件后出现）

首次使用会引导你配置模型（DeepSeek API Key）。

**模型选择**：默认 `deepseek-v4-flash`（性价比）或 `deepseek-v4-pro`（旗舰）。两者均支持**思考模式三档**：

| 推理等级 | 速度 | 质量 | 适用 |
|---|---|---|---|
| `low` | 最快 | 够用（简单/确定性任务） | 简单问答、批量、工具链中的廉价轮次 |
| `high`（默认） | 中等 | 好 | 日常 Agent 任务 |
| `max` | 最慢 | 最强 | 复杂推理、长链规划 |

> 💡 **性能提示**：实测中，模型在**每次工具调用前都会重新思考**——一个 50 步的工具链任务，"思考时间"可能占 90% 以上墙钟时间。`low` 档对简单工具轮次几乎无损，但能显著提速（见第 6 章性能调优与社区插件 `dsh-tool-turbo`）。

## 2.3 模式二：Headless（一次性任务，适合脚本/CI）

```bash
dsh --profile headless "你好，请用一句话介绍你自己"
# 打印最终回复后退出
```

Headless 的核心价值：

- **无 GUI 的自动化**：可在 CI、服务器、cron 中使用
- **会话持久化**：每次调用是"一个新鲜会话"（`--resume` 可恢复，见 `dsh --profile headless --help`）
- **可脚本化**：退出码非零即失败，适合管道

## 2.4 配置文件在哪里

首次运行后生成：

```
~/.dsh/
├── settings.yaml          # 全局设置（含默认模型与推理档位）
├── profiles/              # profile 目录（web / headless / 自定义）
│   └── web/
│       ├── package.json      # 插件依赖 + profile 清单
│       └── cordis.patch.yml  # 你的补丁层（挂载插件）
├── sessions/              # 会话数据
└── storages/              # 持久化存储（workspace、session 索引等）
```

`settings.yaml` 示例：

```yaml
agent-default-model:
  model: deepseek-v4-flash
  reasoningEffort: high
```

## 2.5 命令速查

| 命令 | 用途 |
|---|---|
| `dsh web` | 启动 Web UI（别名 `dsh --profile web`） |
| `dsh --profile headless "任务"` | 一次性任务，打印结果后退出 |
| `dsh plugin --profile <name> add <pkg>` | 给 profile 安装插件 |
| `dsh --dump-config` | 打印当前 profile 的合成配置树 |
| `dsh --profile tui` | TUI 模式（需先安装 tui 插件，官方未内置） |

## 2.6 排障速查

| 现象 | 原因与解法 |
|---|---|
| `dsh: profile "tui" does not exist` | tui profile 需插件创建（`dsh plugin --profile tui add <pkg>`），官方未内置 |
| `npx @deepseek-ai/dsh` 极慢 | 首次下载包体较大（含 40+ 插件模块）；`npm i -g` 后更快 |
| 浏览器打不开 3080 | 检查端口占用：`netstat -ano | findstr 3080` |
| 模型无响应 | 检查 `~/.dsh/settings.yaml` 的模型配置 + API Key |
| 升级后行为变了 | rc 阶段破坏性变更正常；留意官方 changelog |

---

**下一章**：[第 3 章：profile 与插件系统](./03-profiles.md)（规划中）—— 理解 dsh 的可定制骨架。
