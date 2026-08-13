# 一页速查卡（Cheatsheet）

> 打印/收藏这张卡，日常用 dsh 不用翻书。

## 安装与启动

```bash
npx -y @deepseek-ai/dsh --version      # 免安装运行
npm i -g @deepseek-ai/dsh              # 全局安装
dsh web                                # Web UI → http://127.0.0.1:3080
dsh --profile headless "任务"          # 一次性任务（脚本/CI）
```

## 配置（~/.dsh/settings.yaml）

```yaml
agent-default-model:
  model: deepseek-v4-flash     # 或 deepseek-v4-pro
  reasoningEffort: high        # low / high / max
```

## 推理档位

| 档位 | 用途 |
|---|---|
| `low` | 简单/批量/工具链廉价轮（最快） |
| `high` | 日常默认 |
| `max` | 复杂推理/长链规划 |

> 工具链任务 90% 时间在思考——降档是最快提速。

## 核心命令

| 命令 | 用途 |
|---|---|
| `dsh web` | Web UI |
| `dsh --profile headless "任务"` | 一次性任务 |
| `dsh --dump-config` | 看合成配置 |
| `dsh plugin --profile <n> add <pkg>` | 装插件 |

## 插件挂载（两步）

```yaml
# package.json 加依赖
"my-plugin": "link:C:\\path\\to\\my-plugin"
# cordis.patch.yml 加挂载
- insert:
    - id: my-plugin
      name: my-plugin
```

```bash
cd ~/.dsh/profiles/web && pnpm install && dsh web
```

## 提示词黄金法则

1. **写验收标准**：`"运行验证通过"` > `"写个脚本"`
2. **给上下文**：文件在哪、数据长啥样、读者是谁
3. **一次一个任务**：小闭环比巨型任务可靠

## 缓存省钱

- 长任务保持会话延续（别频繁新建）
- prompt 前缀稳定（别老改配置）
- 看 Web UI 底部"缓存命中 %"（实测可到 97%）

## 排障速查

| 现象 | 解法 |
|---|---|
| 端口占 | `netstat -ano \| findstr 3080` → kill |
| 模型无响应 | 查 settings.yaml + API key |
| 插件装不上 404 | 依赖用 `^0.1.0-rc.6` 线 |
| 长任务崩 | 全局安装（绕 npx）+ 降推理档 |

## 术语（速记）

`profile` 形态 · `bundle` 插件组 · `host/client 半` 服务端/界面 · `扩展点` 官方钩子 · `waterfall` 请求链 · `compaction` 上下文压缩 · `headless` 一次性 CLI · `locations` 产物路径

---

完整教程见 [dsh-handbook 白皮书](https://github.com/Electricitysheep/dsh-handbook)。
