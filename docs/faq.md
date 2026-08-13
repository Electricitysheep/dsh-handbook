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

## 模型与性能

**Q：推理档位怎么选？**
`low`（简单/批量/工具轮）/ `high`（日常）/ `max`（复杂）。工具链 90% 时间在思考——降档最快提速。

**Q：为什么我的任务慢？**
先看是不是思考档位高 + 是否冷启动。长任务建议 `low` + 会话延续（缓存命中）。

**Q：缓存命中率怎么提升？**
保持会话延续、prompt 前缀稳定、批量同会话。实测可到 97%（见[第 5 章](./05-cases.md)）。

## 插件开发

**Q：插件装不上（404）？**
rc.1 依赖断裂——确认用 `^0.1.0-rc.6` 线（第 3 章坑 #1）。

**Q：`agent/request` 的 `next()` 要 await 吗？**
**必须**。不 await 会丢 provider/model 报错（第 4 章坑）。

**Q：怎么写插件最快？**
克隆[插件模板](../examples/plugin-template/)，改纯函数逻辑，挂载即用。

## 安全与生产

**Q：dsh 安全吗？**
工具执行有沙箱 + 审批层。医疗/法律等高风险输出需人工审核。

**Q：能进生产吗？**
rc 阶段有破坏性变更；核心依赖等 `0.1.0` 正式版，生态玩法现在可入。

**Q：长任务会崩吗？**
建议全局安装（绕 npx）+ 降推理档 + 观察内存（实测 50 步任务内存显著上涨）。

## 生态

**Q：官方收外部 PR 吗？**
当前明确"暂不接受"（CONTRIBUTING）。走 Discussion 提案 + 社区渠道（见第 7 章）。

**Q：怎么推广我的插件？**
加 `dsh-plugin` topic + npm 发布 + 官方 Discussion Show-and-tell + awesome 列表。

---

**更多**：术语表见[附录 A](./appendix-glossary.md) · 命令速查见[一页卡](./cheatsheet.md)
