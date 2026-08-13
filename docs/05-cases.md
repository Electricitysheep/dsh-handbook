# 第 5 章：实战案例

> 本章目标：用三个**真实提交到开源仓库**的案例，演示插件的完整开发闭环——需求 → 实现 → 测试 → 实机验证。全部是社区真实 PR，可对照源码学习。

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

**下一章**：[第 6 章：进阶与性能调优](./06-advanced.md)（规划中）。
