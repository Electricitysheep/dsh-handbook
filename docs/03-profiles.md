# 第 3 章：profile 与插件系统

> 本章目标：理解 dsh 的可定制骨架——profile 怎么组织、插件怎么挂载、host/client 双半是什么。**这是从"用户"变成"开发者"的分水岭。**

## TL;DR（本章核心，30 秒版）

1. **profile = 一种可启动形态**：`~/.dsh/profiles/<name>/` 目录，由 `package.json`（插件清单）+ `cordis.patch.yml`（补丁层）组成
2. **挂载插件只需两步**：`package.json` 加依赖 + `cordis.patch.yml` 加挂载行，然后 `pnpm install` 重启
3. **host 半跑在 Node，client 半跑在浏览器**：一个 npm 包通过 `exports["."]` 和 `exports["./client"]` 同时携带两副面孔
4. **改行为找扩展点，别 fork 核心**：`agent/request` waterfall、`conversationEvents`、`ctx.slots.inject`、`settings` 服务是四大常用钩子
5. **rc 阶段三大坑**：依赖版本用 `^0.1.0-rc.6` 线、`next()` 必须 await、client 测试需要 dsh 运行时

<details><summary>本章导航</summary>
- [3.1 profile：一个可启动的配置栈](#31-profile一个可启动的配置栈)
- [3.2 挂载一个插件：两处改动](#32-挂载一个插件两处改动)
- [3.3 host 半与 client 半：一个包，两副面孔](#33-host-半与-client-半一个包两副面孔)
- [3.4 扩展点：改行为优先找钩子，别 fork 核心](#34-扩展点改行为优先找钩子别-fork-核心)
- [3.5 常见坑（真实踩过）](#35-常见坑真实踩过)
</details>

## 3.1 profile：一个可启动的配置栈

dsh 用 **profile** 表示"一种可启动的形态"。官方内置两个，其余用插件创建：

| profile | 用途 | 命令 |
|---|---|---|
| `web` | Web UI（对话 + 侧边栏 + 工具） | `dsh web` |
| `headless` | 一次性 CLI 任务 | `dsh --profile headless "任务"` |
| `tui`（需插件） | 终端 UI | `dsh --profile tui`（未内置，需安装插件） |

一个 profile 目录长这样（`~/.dsh/profiles/<name>/`）：

<!-- [style] 目录树代码块统一补 text 语言标签 -->
```text
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
| `agent/request` waterfall | `agent-loop` | **每次模型请求前改配置**（provider/model/reasoningEffort/tools）——提速插件示例用这个 |
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

## 动手练习（检验你是否真懂了）

1. **理解题**：不看原文，画出 `profiles/web/` 目录下的文件结构，并说出每个文件的作用
   > 自查：参考本章 3.1 节"profile 目录长这样"
2. **理解题**：解释"host 半"和"client 半"分别跑在哪里、各负责什么。一个插件可以只有 host 半吗？
   > 自查：参考本章 3.3 节表格
3. **动手题**：打开你的 `~/.dsh/profiles/web/package.json`，找到 `dsh.profile.bundles` 字段，说出 bundle 的加载顺序
   > 自查：参考本章 3.1 节"加载顺序"段落
4. **动手题**：假设你要挂载一个名为 `dsh-my-widget` 的插件，写出 `package.json` 和 `cordis.patch.yml` 各需要加什么内容
   > 自查：参考本章 3.2 节的两处改动示例
5. **动手题**：在 `cordis.patch.yml` 里加一行错误的挂载（比如拼错插件名），重启 dsh web，观察报错信息并记录
   > 自查：对比本章 3.5 节"常见坑"表格
6. **思考题**：官方原则说"Plugins, not loop changes"。如果你想改 dsh 的"模型回复后自动总结"行为，应该用哪个扩展点？为什么不该直接改 agent-loop 源码？
   > 自查：参考本章 3.4 节扩展点表格 + "改行为优先找钩子"原则

## 常见疑问 FAQ

**Q1：profile 和 bundle 有什么区别？**
profile 是"一种可启动形态"（如 web、headless），bundle 是"一组预配置的插件集合"。profile 通过 `dsh.profile.bundles` 指定要加载哪些 bundle，再叠加自己的 patch。简单说：bundle 是积木包，profile 是拼好的成品。

**Q2：`cordis.patch.yml` 里的 `- insert:` 是什么意思？还有其他操作吗？**
`insert` 是"在插件链中插入一个新插件"。patch 文件基于 cordis 的配置合并机制，支持 insert（插入）、override（覆盖已有插件配置）等操作。新手只需掌握 insert 即可挂载大部分插件。

**Q3：插件状态是按 profile 隔离还是按会话隔离？**
挂载是 profile 级的（装一次，该 profile 下所有会话都能用），但**状态是会话级的**。比如 `better-sidebar` 的标签布局按会话持久化，不同会话互不干扰。

**Q4：我想写一个只有 client 半的插件（纯 UI），可以吗？**
可以。`package.json` 里声明 `dsh.client` + `exports["./client"]`，不写 `exports["."]` 即可。但注意：client 半无法直接访问文件系统或跑命令，需要通过 host 半的服务（`ctx.provide`/`ctx.get`）桥接。

**Q5：`agent/request` waterfall 和 `conversationEvents.register` 有什么区别？我该用哪个？**
`agent/request` 是"改模型请求配置"的钩子（provider/model/tools/reasoningEffort），每次请求前触发，返回新配置。`conversationEvents.register` 是"订阅/注入对话事件"的钩子（tool/call、turn/start 等），用于监听或注入事件流。想改请求参数用前者，想监听对话流用后者。

**Q6：为什么我的插件装上去没反应？怎么调试？**
三步排查：① 确认 `pnpm install` 无报错且 `node_modules` 里有你的插件；② 确认 `cordis.patch.yml` 的 id/name 拼写正确；③ 重启 `dsh web` 后看进程日志有没有插件加载信息。如果 host 半有 `console.log`，日志里应该能看到输出。

---

**下一章**：[第 4 章：插件开发实战](./04-plugin-dev.md)（规划中）—— 从零写第一个 host 插件。
