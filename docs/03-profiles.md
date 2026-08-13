# 第 3 章：profile 与插件系统

> 本章目标：理解 dsh 的可定制骨架——profile 怎么组织、插件怎么挂载、host/client 双半是什么。**这是从"用户"变成"开发者"的分水岭。**

## 3.1 profile：一个可启动的配置栈

dsh 用 **profile** 表示"一种可启动的形态"。官方内置两个，其余用插件创建：

| profile | 用途 | 命令 |
|---|---|---|
| `web` | Web UI（对话 + 侧边栏 + 工具） | `dsh web` |
| `headless` | 一次性 CLI 任务 | `dsh --profile headless "任务"` |
| `tui`（需插件） | 终端 UI | `dsh --profile tui`（未内置，需安装插件） |

一个 profile 目录长这样（`~/.dsh/profiles/<name>/`）：

```
profiles/web/
├── package.json        # 插件依赖 + dsh.profile 清单（bundles 顺序）
├── cordis.patch.yml    # 你的补丁层：挂载/覆盖插件的声明
├── cordis.yml          # （生成的）合成配置
├── pnpm-workspace.yaml
└── node_modules/
```

**加载顺序**（官方文档原文）：内置 bundle（`dsh-base` → `dsh-web-app`）→ profile 的 `cordis.patch.yml` → 用户级 `~/.dsh/cordis.patch.yml` → `--patch` 覆盖层。

## 3.2 挂载一个插件：两处改动

以挂载社区插件 `dsh-better-sidebar` 为例（真实操作）：

**① `package.json` 加依赖**（`link:` 指向本地源码，或用 npm 包名）：

```json
{
  "dependencies": {
    "dsh-better-sidebar": "link:C:\\path\\to\\DSH-better-sidebar"
  }
}
```

**② `cordis.patch.yml` 加挂载行**：

```yaml
- insert:
    - id: better-sidebar
      name: dsh-better-sidebar
```

**③ 安装并重启**：

```bash
cd ~/.dsh/profiles/web && pnpm install
dsh web   # 重启后生效
```

> 💡 插件默认是**按会话隔离**的（`better-sidebar` 的布局/标签按会话持久化）——挂载是 profile 级，但状态是会话级。

## 3.3 host 半与 client 半：一个包，两副面孔

插件可以同时携带两个运行半：

| 半边 | 运行位置 | 职责 | 示例 |
|---|---|---|---|
| **host 半** | Node 进程 | 工具、服务、事件、文件系统、进程 | `apply(ctx)` 注册工具/服务 |
| **client 半** | 浏览器（web profile） | UI、交互、DOM | `package.json` 的 `dsh.client` 声明 + `src/client/` |

`package.json` 里如何声明 client 半：

```json
{
  "dsh": {
    "client": {
      "inject": ["@deepseek-ai/dsh-client-runtime", "@deepseek-ai/dsh-client-locale"],
      "platform": "web"
    }
  },
  "exports": {
    ".": { "types": "./lib/types/index.d.ts", "default": "./lib/index.js" },
    "./client": { "types": "./lib/types/client/index.d.ts", "default": "./lib/client.js" }
  }
}
```

- host 半：`exports["."]` → `apply(ctx)`（cordis 插件主体）
- client 半：`exports["./client"]` → 浏览器侧的 `apply(ctx)`
- `inject`：声明需要的服务（cordis 依赖注入）

## 3.4 扩展点：改行为优先找钩子，别 fork 核心

官方原则（CONTRIBUTING/AGENTS.md 明示）：**"Plugins, not loop changes: new behavior goes on documented extension points"**。新手最常见的错误是改核心 loop——正确做法是用扩展点。

已确认的常用扩展点（后续章节逐一实战）：

| 扩展点 | 位置 | 用途 |
|---|---|---|
| `agent/request` waterfall | `agent-loop` | **每次模型请求前改配置**（provider/model/reasoningEffort/tools）——tool-turbo 用这个 |
| `agent/request-error` | `agent-loop` | 请求失败时干预（官方 compaction 插件用这个做上下文溢出恢复） |
| `conversationEvents.register` | client runtime | 订阅/注入对话事件（tool/call、turn/start 等） |
| `ctx.slots.inject` | client ui-slots | 在界面槽位注入 UI（如 turnTail 显示产物文件行） |
| `settings` 服务 | dsh-settings | 注册用户可配置的命名空间（设置页自动渲染） |
| `ctx.provide` / `ctx.get` | cordis | 跨插件提供服务 |

## 3.5 常见坑（真实踩过）

| 坑 | 现象 | 解决 |
|---|---|---|
| **rc.1 依赖断裂** | `pnpm install` 报 `@deepseek-ai/dsh-type-meta@0.0.1-rc.1` 404 | 官方 rc.1 时代多个包从未发布；升级到 `^0.1.0-rc.6` 线 |
| 插件缺 `main` | `dsh: No "exports" main defined` | host 插件 `package.json` 要暴露 `.` 入口（`"main": "src/index.ts"` 可被 tsx 直接加载） |
| 事件 handler 忘了 `await next()` | 请求丢失 provider/model 报错 | `agent/request` 的 `next()` 返回 **Promise**，必须 await 后 spread |
| 类型报 `'agent/request' is not assignable to keyof Events` | npm 类型未 re-export 官方类型增强 | 用宽松签名（`ctx.on as unknown as ...`）在边界转换 |
| client 包产物依赖 `window.__ModuleLoader__` | jsdom 无法直接跑 client 测试 | 组件级测试需 dsh web 运行时（官方 CI 跑） |

---

**下一章**：[第 4 章：插件开发实战](./04-plugin-dev.md)（规划中）—— 从零写第一个 host 插件。
