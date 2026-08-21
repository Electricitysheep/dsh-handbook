# dsh 插件模板（Plugin Template）

<!-- [fix] 链接健康检查：../docs/04-plugin-dev.md 从 examples/plugin-template/ 起算指向不存在的 examples/docs/，改为 ../../docs/04-plugin-dev.md -->
> 白皮书 [第 4 章](../../docs/04-plugin-dev.md) 的配套骨架——**照抄就能跑**的 host 插件。
> 模板功能：在每次模型请求前注入自定义 `reasoning_effort`（示例策略：简单工具链降档）。

## 目录结构

```
plugin-template/
├── package.json          # host 插件声明（rc.6 依赖线）
├── tsconfig.json
├── src/
│   ├── policy.ts         # 纯函数：决策逻辑（零依赖，可单测）
│   └── index.ts          # apply(ctx)：接入 agent/request waterfall
└── tests/
    ├── policy.spec.ts    # 纯函数单元测试
    └── plugin.spec.ts    # waterfall 契约测试
```

## 快速开始

```bash
# 1. 复制模板（改名为你的插件）
cp -r plugin-template my-plugin && cd my-plugin
# 2. 改 package.json 的 name 字段
# 3. 安装 + 测试
npm install && npm test
# 4. 挂载到 dsh（见下）
```

## 挂载到 dsh

```json
// ~/.dsh/profiles/web/package.json dependencies
"my-plugin": "link:C:\\path\\to\\my-plugin"
```

```yaml
# ~/.dsh/profiles/web/cordis.patch.yml
- insert:
    - id: my-plugin
      name: my-plugin
```

```bash
cd ~/.dsh/profiles/web && pnpm install && dsh web
```

## 模板逻辑说明

- `src/policy.ts`：`decidePolicy(...)` 纯函数——输入最近的工具调用，输出推理档位（可替换为你的业务逻辑）
- `src/index.ts`：`apply(ctx)` 监听 `agent/request` waterfall，注入决策结果
- **测试**：`npm test` 同时验证纯函数和插件的 waterfall 契约
- **实机验证**：需要无 API Key 跑真实 agent loop 时，见[第 8 章 8.7 节](../../docs/08-tools-context.md#87-插件运行时验证方法论零成本)

## 自定义指南

| 你想做什么 | 改哪里 |
|---|---|
| 换决策逻辑 | `src/policy.ts`（纯函数，可单测） |
| 注入别的请求字段 | `src/index.ts` 的 `return { ...seed, ... }` |
| 加设置项 | 注册 settings 命名空间（见白皮书第 3 章） |
| 加 client 半（UI） | package.json 加 `dsh.client` 声明 + `src/client/` |

## 开发纪律（来自白皮书）

1. 逻辑抽纯函数 → 单测毫秒级
2. 用官方扩展点（agent/request 等），不碰核心
3. 契约测试确认 `next()` 正确透传、上游字段不丢失
4. 自动测试 + 实机日志双证据才算完成

---

模板源码由 dsh-handbook 白皮书提供，MIT 许可。
