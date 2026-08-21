# 配置参考大全（Configuration Reference）

> 面向需要深度配置 dsh 的用户：settings.yaml 全字段、profile 结构、cordis.patch.yml 语法。**rc 阶段字段可能变化，以官方 changelog 为准**；本表基于 0.1.0-rc.8 实测与官方文档。

## 1. settings.yaml（全局设置）

`~/.dsh/settings.yaml`

| 字段 | 示例 | 说明 |
|---|---|---|
| `agent-default-model.model` | `deepseek-v4-flash` | 默认模型（也可 `deepseek-v4-pro`） |
| `agent-default-model.reasoningEffort` | `high` | 思考档位：`off`（关闭思考/最快）/ `high`（默认）/ `max`（最强）。注：官方 DeepSeek 适配器仅这三档，`low` 等为 pi-ai（opencode-go）网关档位 |
| （其他命名空间） | — | 各插件的设置命名空间（如侧边栏 prefs） |

> 完整字段以官方 settings 服务 schema 为准；`dsh --dump-config` 可看当前生效的合成配置。

## 2. profile 结构

```
~/.dsh/profiles/<name>/
├── package.json          # 插件依赖 + profile 清单（dsh.profile）
├── cordis.patch.yml      # 补丁层（挂载/覆盖插件）
├── cordis.yml            # （生成的）合成配置
├── pnpm-workspace.yaml
└── node_modules/
```

### package.json 的 dsh.profile 清单

```json
{
  "dsh": {
    "profile": {
      "bundles": [
        "@deepseek-ai/dsh-base",
        "@deepseek-ai/dsh-web-app"
      ]
    }
  }
}
```

`bundles`：按顺序加载的官方/第三方插件组（web 用 dsh-web-app，headless 用 dsh-headless）。

## 3. cordis.patch.yml 语法

`cordis.patch.yml` 是**顶层 YAML 数组**的补丁条目，常用三种：

### insert（挂载插件）

```yaml
- insert:
    - id: better-sidebar      # 插件实例 id（唯一）
      name: dsh-better-sidebar # npm 包名
```

### override（覆盖插件配置）

```yaml
- override:
    - id: speed-plugin
      config:
        baseline: low         # 覆盖插件默认配置
```

### disable（禁用插件）

```yaml
- disable:
    - id: some-plugin
```

> 注意：顶层必须是数组（`- insert:` 开头），不能先写 `[]` 再写条目（YAML 语法错误）。

## 4. 常用配置场景

### 换默认模型

```yaml
agent-default-model:
  model: deepseek-v4-pro
  reasoningEffort: high
```

### 挂载一个本地开发中的插件

```json
// package.json dependencies
"my-plugin": "link:C:\\path\\to\\my-plugin"
```

```yaml
# cordis.patch.yml
- insert:
    - id: my-plugin
      name: my-plugin
```

```bash
cd ~/.dsh/profiles/web && pnpm install && dsh web
```

### 查看当前生效配置

```bash
dsh --dump-config        # 含用户层的合成树
dsh --dump-default-config  # 不含用户层/补丁
```

## 5. 常见配置问题

| 问题 | 原因 | 解法 |
|---|---|---|
| 插件没生效 | cordis.patch.yml 没挂载 / 依赖没装 | 检查 insert 行 + `pnpm install` |
| 改了 settings 没反应 | 未重启 | 重启 `dsh web` |
| 依赖 404 | rc.1 线断裂 | 用 `^0.1.0-rc.8` |
| YAML 解析失败 | 顶层混用 `[]` 和块式条目 | 统一用块式数组 |
