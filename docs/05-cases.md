# 第 5 章：实战案例

> 本章目标：用三个**真实提交到开源仓库**的案例，演示插件的完整开发闭环——需求 → 实现 → 测试 → 实机验证。全部是社区真实 PR，可对照源码学习。

## TL;DR（本章核心，30 秒版）

1. **案例一（Git 面板）**：补全 push/pull/fetch 远端同步，4 文件分层（纯函数 + 路由 + UI + 集成测试），安全红线文档化
2. **案例二（HTML 预览）**：支持未保存草稿，核心是安全决策纯函数——沙箱开启才用 srcdoc（opaque origin）
3. **案例三（tool-turbo）**：第 4 章完整拆解，价值在长工具链任务的累计降档效果
4. **共同方法论**：纯函数隔离（零依赖单测）→ 扩展点接入（不碰核心）→ 实机验证闭环（双证据）
5. **PR 范式**：每个案例都是"小切口 + 完整测试 + 实机截图/日志"——社区 PR 的标准模板

## 5.1 案例一：Git 面板补全 push / pull / fetch

**背景**：社区插件 `DSH-better-sidebar` 提供 Git 面板，但只有本地操作（暂存/提交/还原），**没有远端同步**。

**实现**（4 个文件，全部走"纯函数 + 路由 + UI"分层）：

```
src/git.ts              # 纯函数层：upstreamInfo / fetchRemote / pull / push
src/index.ts            # 路由层：git.upstream / git.fetch / git.pull / git.push
src/client/GitView.tsx  # UI 层：上游徽标（↓behind ↑ahead）+ 三个按钮
tests/git-sync.spec.ts  # 集成测试：本地 bare-repo 全链路
```

**关键设计**（值得抄的部分）：

```ts
// push 只允许 --force-with-lease，绝不裸 --force —— 安全红线文档化
export async function push(cwd: string, force = false): Promise<string> {
  const args = ['push']
  if (force) args.push('--force-with-lease')
  return runGit(cwd, args)
}
```

**测试**（本地 bare repo，无网络、无全局 git 配置）：

```ts
// 覆盖：上游跟踪 / 推送 / 拉取快进 / fetch 不动 HEAD / force-with-lease 拒绝覆盖他人提交
it('force push refuses to clobber unseen remote commits', async () => {
  // 其他 clone 先推了提交；本地改写历史但不 fetch（lease 过期）
  await expect(git.push(clone, true)).rejects.toThrow()
  // 远端仍持有对方提交 —— 安全保证生效
})
```

**实机验证**（Playwright 操作真实 dsh web）：
- 三按钮渲染，pull/push 在无 upstream 时正确禁用
- 点击"拉取远端"→ 网络请求 `git.fetch [200]` → 面板自动刷新

> PR 见：https://github.com/omdsh-dev/DSH-better-sidebar/pull/10

## 5.2 案例二：HTML 预览支持未保存草稿

**背景**：HTML 文件编辑后，预览只显示**已保存版本**（README 已知限制）。看似简单，但有安全约束：**非沙箱的 `srcdoc` iframe 会继承父 origin**（官方代码注释明确）。

**解决**：抽纯函数做"安全决策"：

```ts
// 沙箱开启时 dirty 草稿才用 srcdoc（opaque origin，安全）；
// 沙箱关闭时拒绝 srcdoc，保持 route-src（跨源保证）
export function htmlPreviewTarget(input): HtmlPreviewTarget {
  if (input.isHtml && input.dirty && input.draft !== null && !input.sandboxOff) {
    return { srcDoc: input.draft }
  }
  return { src: input.routeUrl }
}
```

**教训**：UI 看似"加个功能"，但安全模型是硬约束——**先读代码注释里的为什么，再动手**。

> PR 见：https://github.com/omdsh-dev/DSH-better-sidebar/pull/11

## 5.3 案例三：tool-turbo 提速插件

（第 4 章完整拆解过，此处只讲结果）

- **决策逻辑**：纯函数 `decideEffort`，6/6 单测
- **注入链路**：`agent/request` waterfall，实机日志证明 `high → low`
- **价值定位**（重要修正）：简单任务 dsh 本来就快；**提速收益在长工具链任务**——每步思考降档的累计效果

## 5.4 三个案例的共同方法论

1. **纯函数隔离**：决策/计算逻辑零依赖 → 单测全分支
2. **扩展点接入**：路由/waterfall/事件——不碰核心
3. **实机验证闭环**：单测（逻辑）+ 真实 dsh 日志/网络请求（接线）双证据

---

## 动手练习（检验你是否真懂了）

1. **理解题**：案例一（Git 面板）的 4 个文件分别对应哪三层架构？`tests/git-sync.spec.ts` 为什么用"本地 bare repo"而不是真实 GitHub 仓库？
   > 自查：参考本章 5.1 节文件结构 + 测试代码注释
2. **理解题**：案例二（HTML 预览）里，为什么"沙箱关闭时拒绝 srcdoc"？如果不拒绝，会有什么安全风险？
   > 自查：参考本章 5.2 节"安全约束"段落 + `htmlPreviewTarget` 纯函数
3. **动手题**：案例一的 `push` 函数只允许 `--force-with-lease`，不允许裸 `--force`。请你写出一个测试用例，验证"裸 force 被拒绝"的行为
   > 自查：参考本章 5.1 节测试代码示例，用 `expect(...).rejects.toThrow()` 模式
4. **动手题**：假设你要给 Git 面板加一个"查看远端分支列表"功能，按本章的分层方法论，写出你会改哪几个文件、每个文件加什么
   > 自查：参考本章 5.1 节"4 个文件分层"结构 + 5.4 节共同方法论
5. **思考题**：三个案例都强调"实机验证闭环"。如果只跑单测不跑实机，案例一的 Git 面板可能漏掉什么问题？案例二的 HTML 预览呢？
   > 自查：参考本章 5.4 节"双证据"原则 + 各案例的实机验证段落
6. **思考题**：案例三（tool-turbo）的价值定位做了"重要修正"——简单任务 dsh 本来就快，提速收益在长工具链。这个修正对"怎么写插件 README"有什么启示？
   > 自查：参考本章 5.3 节"价值定位"段落

## 常见疑问 FAQ

**Q1：我想给社区插件提 PR，需要先和作者沟通吗？**
建议先开 issue 或在 Discussions 描述你想加的功能，确认作者接受后再提 PR。案例一的 PR 就是先有需求讨论再实现的。直接提大 PR 可能被拒或要求大改。

**Q2：案例一的测试用了"本地 bare repo"，这是什么？**
bare repo 是"没有工作区的 git 仓库"（只有 `.git` 内容），常用于服务器端。测试里用它模拟"远端仓库"，好处是零网络依赖、零全局 git 配置依赖、测试可重复跑。

**Q3：案例二的 `srcdoc` 和 `src` 有什么区别？为什么安全模型不同？**
`srcdoc` 是内联 HTML 内容（直接写在 iframe 属性里），默认继承父页面的 origin（除非加 sandbox）。`src` 是 URL 指向独立文件，天然跨源。所以"未保存草稿用 srcdoc"必须确认沙箱开启，否则草稿 JS 能访问父页面的 cookie/localStorage。

**Q4：我的插件测试通过了，但实机跑起来行为不对，怎么排查？**
三步：① 看 dsh 进程日志有没有插件输出（`console.log` 会打到 stdout）；② 检查 `cordis.patch.yml` 的挂载顺序（waterfall 类插件的执行顺序依赖挂载顺序）；③ 用 `dsh --dump-config` 看合成配置，确认插件确实被加载。

**Q5：三个案例都是"小切口"（一个功能点），为什么不做大而全的插件？**
社区 PR 的范式就是"小切口 + 完整测试 + 实机证据"。大而全的 PR 难审查、难合并、难维护。拆成多个小 PR，每个独立可验证，是开源协作的最佳实践。

**Q6：我想复刻案例一的开发流程，但不会 React/TSX 怎么办？**
先跑通第 2 章的安装 + 第 3 章的插件挂载，再读 `DSH-better-sidebar` 的源码（重点看 `src/git.ts` 纯函数层，不需要懂 React）。UI 层可以后学，纯函数层和路由层是核心。

---

**下一章**：[第 6 章：进阶与性能调优](./06-advanced.md)（规划中）。
