[English](./05-cases.en.md) | [中文](./05-cases.md) · [← Back](../README.md)

# Chapter 5: Real-World Cases

> **Goal of this chapter:** Walk through three **real, merged open-source PRs** to demonstrate the full plugin development loop: requirements → implementation → testing → live verification. All are genuine community PRs you can study against the source code.

## 5.1 Case 1: Git Panel — Adding push / pull / fetch

**Background:** The community plugin `DSH-better-sidebar` provides a Git panel, but it only supports local operations (stage/commit/restore). **No remote sync.**

**Implementation** (4 files, all following the "pure function + routing + UI" layering):

```
src/git.ts              # Pure function layer: upstreamInfo / fetchRemote / pull / push
src/index.ts            # Routing layer: git.upstream / git.fetch / git.pull / git.push
src/client/GitView.tsx  # UI layer: upstream badge (↓behind ↑ahead) + three buttons
tests/git-sync.spec.ts  # Integration tests: full chain with a local bare repo
```

**Key design** (worth copying):

```ts
// push only allows --force-with-lease, never bare --force — safety red line, documented
export async function push(cwd: string, force = false): Promise<string> {
  const args = ['push']
  if (force) args.push('--force-with-lease')
  return runGit(cwd, args)
}
```

**Tests** (local bare repo, no network, no global git config):

```ts
// Covers: upstream tracking / push / pull fast-forward / fetch doesn't move HEAD /
//         force-with-lease refuses to clobber others' commits
it('force push refuses to clobber unseen remote commits', async () => {
  // Another clone pushed commits first; local rewrites history but doesn't fetch (lease is stale)
  await expect(git.push(clone, true)).rejects.toThrow()
  // Remote still holds the other party's commits — safety guarantee holds
})
```

**Live verification** (Playwright driving a real dsh web instance):
- Three buttons render correctly; pull/push are properly disabled when no upstream exists
- Clicking "Fetch remote" → network request `git.fetch [200]` → panel auto-refreshes

> PR: https://github.com/omdsh-dev/DSH-better-sidebar/pull/10

## 5.2 Case 2: HTML Preview — Supporting Unsaved Drafts

**Background:** After editing an HTML file, the preview only shows the **saved version** (a known limitation in the README). Seems simple, but there's a security constraint: **a non-sandboxed `srcdoc` iframe inherits the parent origin** (stated explicitly in official code comments).

**Solution:** Extract a pure function for the "safety decision":

```ts
// When sandbox is on, dirty drafts use srcdoc (opaque origin, safe);
// when sandbox is off, refuse srcdoc and fall back to route-src (cross-origin guarantee)
export function htmlPreviewTarget(input): HtmlPreviewTarget {
  if (input.isHtml && input.dirty && input.draft !== null && !input.sandboxOff) {
    return { srcDoc: input.draft }
  }
  return { src: input.routeUrl }
}
```

**Lesson:** A UI feature may look like "just add a button," but the security model is a hard constraint. **Read the "why" in code comments first, then write code.**

> PR: https://github.com/omdsh-dev/DSH-better-sidebar/pull/11

## 5.3 Case 3: tool-turbo Speed-Up Plugin

(Fully broken down in Chapter 4; here we just summarize results)

- **Decision logic:** Pure function `decideEffort`, 6/6 unit tests passing
- **Injection pipeline:** `agent/request` waterfall; live logs confirm `high → low`
- **Value proposition** (important correction): dsh is already fast on simple tasks. **The speed-up benefit is in long tool-chain tasks** — the cumulative effect of downgrading reasoning effort at every step

## 5.4 Shared Methodology Across All Three Cases

1. **Pure function isolation:** Decision/computation logic has zero dependencies → unit tests cover every branch
2. **Extension point integration:** Routing/waterfall/events — never touch the core
3. **Live verification loop:** Unit tests (logic) + real dsh logs/network requests (wiring) — dual evidence

---

**Next chapter**: [Chapter 6: Advanced & Performance Tuning](./06-advanced.en.md) (planned).
