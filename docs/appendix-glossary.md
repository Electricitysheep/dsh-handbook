# 附录 A：术语表与命令速查

## 术语表

| 术语 | 一句话解释 |
|---|---|
| **Harness** | 套在模型外的工程层：会话、工具、上下文、循环控制 |
| **dsh** | DeepSeek Harness 的命令行名（`dsh` 命令） |
| **Profile** | 一种可启动形态（web / headless / 自定义），= bundle 栈 + patch 层 |
| **Bundle** | 一组插件的集合（官方：dsh-base、dsh-web-app、dsh-headless） |
| **Cordis** | dsh 底层的插件容器（依赖注入、事件、生命周期） |
| **插件（Plugin）** | cordis 插件；可同时携带 host 半（Node）与 client 半（浏览器） |
| **host 半 / client 半** | 插件在 Node 侧（工具/服务/事件）与浏览器侧（UI）的两副面孔 |
| **扩展点** | 官方提供的钩子（agent/request、settings、conversationEvents、slots） |
| **agent/request waterfall** | 每步模型请求前可改配置的事件链（插件在此注入 reasoningEffort 等） |
| **reasoning_effort** | 思考强度（low/high/max）——速度与质量的权衡旋钮 |
| **headless** | 一次性 CLI 任务模式（`dsh --profile headless "任务"`） |
| **compaction** | 长对话上下文压缩 |
| **subagent** | 子代理（并行委派任务） |
| **MCP** | 模型上下文协议（接入外部工具服务器） |
| **workflow** | 多步确定性工作流编排 |
| **locations** | 工具返回的文件路径（驱动产物追踪） |
| **extension point** | 官方钩子（agent/request 等），插件接入点 |
| **waterfall** | 事件链：监听者可改配置传给下一个（agent/request 用此注入） |
| **reasoning_effort** | 思考强度旋钮（low/high/max） |
| **context cache** | DeepSeek 提示词缓存（重复输入按折扣价计费） |
| **缓存命中率** | 输入 token 走缓存价的比例（dsh 实测可到 97%） |
| **headless** | 一次性 CLI 任务模式 |
| **TUI** | 终端 UI（官方未内置，需插件） |
| **turn** | 对话的一轮（用户+助手+工具调用） |
| **step** | turn 内的一个推理步骤 |
| **guard** | 循环卫生/工具超时插件 |
| **skill** | 技能（skill-catalog 注入上下文，模型按需调用） |
| **inject** | cordis 依赖注入（插件声明所需服务） |
| **产物文件** | 模型创建/修改的文件（对话末尾的可打开 chips） |
| **sandbox** | 命令执行的隔离沙箱 |
| **reasoning_effort** | 同「思考强度」 |
| **rc** | 预发布版本（0.1.0-rc.6），迭代快、可能有破坏性变更 |

## 命令速查

### dsh 核心

```bash
dsh web                                        # 启动 Web UI
dsh --profile headless "任务"                  # 一次性任务（脚本/CI）
dsh --version                                  # 版本
dsh --dump-config                              # 合成配置树
dsh plugin --profile <name> add <pkg>          # 安装插件
```

### 环境

```bash
node --version                                 # 需 ≥ 22
npm install -g @deepseek-ai/dsh                 # 全局安装
npx -y @deepseek-ai/dsh web                     # 免安装运行
```

### 排障

```bash
netstat -ano | findstr 3080                    # 端口占用（Windows）
taskkill /PID <pid> /F                          # 杀进程
cat ~/.dsh/settings.yaml                        # 全局配置（模型/推理档位）
```

### 插件开发

```bash
# 挂载到 profile（web 为例）
# ① package.json 加依赖: "pkg": "link:C:\\path\\to\\pkg"
# ② cordis.patch.yml 加:
#    - insert:
#        - id: <插件id>
#          name: <npm包名>
cd ~/.dsh/profiles/web && pnpm install          # 安装
```

## 配置参考（settings.yaml）

```yaml
agent-default-model:
  model: deepseek-v4-flash     # 或 deepseek-v4-pro
  reasoningEffort: high        # low / high / max
```

---

**附录 B**：[同模型多 Agent 实测](./benchmark.md)
