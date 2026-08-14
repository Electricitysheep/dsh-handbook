# Chapter 12: Known Limitations & Boundaries — the Honest Edition

> Goal: list dsh's **known limitations** and usage boundaries without hype. When this handbook was written, dsh was still at `0.1.0-rc.6` (pre-release). These limitations are "facts of this moment", not "permanent fate" — they will change as versions iterate.
>
> All "known issues" come from hands-on testing + public feedback in the official repo discussions (deepseek-ai/deepseek-harness, as of 2026-08-13).

## TL;DR (30-second version)

1. **The rc stage is the biggest uncertainty**: API/config can break at any time — pin your version line before investing
2. **Plugin ecosystem is early**: 60+ official packages but limited coverage; few third-party plugins; interactive forms (TUI) missing
3. **Cross-platform gaps**: real path/encoding bugs on Windows (UTF-16, 0x00)
4. **Performance boundaries unverified**: high concurrency, large codebases lack public stress data
5. **Official strategy risk**: open-source commitment vs commercialization is the black swan you must consider when choosing

---

## 12.1 rc-stage instability

### Breaking changes happen anytime

dsh has gone through at least one **dependency breakage** from rc.1 to rc.6: inconsistent `@deepseek-ai/*` version lines caused plugins to fail installing (404/ERR_MODULE_NOT_FOUND). rc.6 has converged a lot, but **nothing guarantees rc.7 or the stable release won't break again**.

**Real impact on you**:
- Tutorials/plugins may need rewriting every couple of weeks
- Pinning the version line (`^0.1.0-rc.6`) is the baseline; but whether an rc-line upgrade is "backward compatible" or "start over" depends on the official team's mood

> [!WARNING]
> Evaluate carefully before production use. At writing time the official team is iterating fast — **what works today may be deprecated tomorrow**.

### Known rc pitfalls (reproduced locally / in the community)

| Pitfall | Symptom | Status |
|---|---|---|
| link-dev dependency breakage | `@deepseek-ai/*` ERR_MODULE_NOT_FOUND when linking locally, but works via npm install | Root-caused (flat fallback dir mechanism); pin the dependency line to avoid |
| Windows path 0x00 | workspace creation fails with Chinese/special-char paths (ENOENT) | Community-reported (#151/#396) |
| fs-sandbox race | post-check path check races with workspace-write | Community-reported (#159) |
| TUI missing | no interactive terminal UI in official examples (community builds exist, not merged) | Proposed (#392) |

## 12.2 Early plugin ecosystem

**Current state**: 60+ official packages, but the ecosystem is overall at "day zero".

- **Few third-party plugins**: plugin threads in Discussions are exploding, but quality varies — most are first-plugin practice pieces
- **Missing interactive forms**: headless/JSON-RPC/Web are complete, but **no official example of terminal-native UI (TUI)** (the community deepseek-harness-tui proved it viable; not merged into official)
- **Docs lag the code**: official docs are architecture-focused; onboarding paths and pitfall records depend on community output (which is exactly why this handbook exists)
- **Version-line chaos**: multiple version lines coexist on npm; installing the wrong line = 404

**Judgment**: entering the ecosystem now is early-mover dividend (less competition, official willingness to support), but **don't expect "just follow the official docs and it runs"** — hitting pitfalls is the norm.

## 12.3 Cross-platform gaps

dsh is mature on macOS/Linux, but Windows support has a clear "second-class citizen" feel:

- **Path handling**: real bugs with Chinese/special-character paths (0x00 truncation, ENOENT); multiple community reports
- **Encoding**: UTF-16 handling has defects; occasional garbled terminal output
- **CLI/TUI debate unsettled**: there's an ongoing dispute in official Discussions about "CLI is the way vs TUI is the interactive future" (#386); investing in a terminal-UI form before the direction settles carries risk

## 12.4 Unverified performance boundaries

The handbook's benchmark covers **single agent, normal task scale**. These scenarios lack public data:

- **High concurrency**: parallel agents, large-scale task distribution
- **Large codebases**: context management and tool-call latency at million-line scale
- **Long-running stability**: hours-long sessions, memory-leak risk
- **Cache-hit boundaries**: the measured ~97% hit rate depends on "repetitive conversation patterns" — brand-new/cold-start tasks drop noticeably

## 12.5 Gaps vs mature agents

Compared with Claude Code, Codex, and other mature products, dsh's gaps are **structural** (not fixed by adding a few features):

| Dimension | dsh (rc.6) | Mature agents |
|---|---|---|
| Ecosystem stage | day zero, few third-party assets | mature, complete |
| Out of the box | requires understanding profiles/plugin system | install & run |
| Stability | rc stage, breaking-change risk | stable releases, long-term compatibility promises |
| Docs | official is architecture-focused; onboarding via community | complete official docs + rich tutorials |
| IDE/toolchain integration | early | deep |

**dsh's positioning**: not an "out-of-the-box car", but a "programmable LEGO base". Choosing dsh = choosing **freedom**, at the cost of **assembling it yourself**.

## 12.6 Official strategy risk

Black swans a selector must consider:

- **Open-source commitment**: MIT with no noise so far, but "official-grade plugin system" means the ecosystem is deeply bound to the official cadence
- **Model-binding tendency**: default experience favors DeepSeek models (any model via the llm plugin, but "official optimization" is DeepSeek-first)
- **Commercialization shift**: once dsh user numbers rise, the official team may launch managed services/paid tiers — whether the open-source edition keeps parity is unknown
- **Direction drift**: rc-stage features are added/removed frequently (the CLI/TUI debate is a signal); betting on the wrong direction = sunk cost

## 12.7 This handbook's own limitations

Finally, honestly about this handbook itself:

- **Written against rc.6**: every command, config, and data point verified on rc.6 — **newer versions may invalidate everything**
- **Limited benchmark sample**: single machine, single model, limited task set — not an authoritative evaluation
- **Chinese-first**: the English edition is a translation/condensation and may lag the Chinese content
- **Incomplete coverage**: dsh has 60+ official packages; this handbook deep-dives the core path; long-tail plugins aren't covered one by one

> **Usage advice**: treat this handbook as an "rc.6 snapshot + methodology", not an "eternal bible". When versions update, run through the [roadmap learning path](./roadmap.md) acceptance checks first, then decide whether to update your dependency line.

---

*Info as of 2026-08-13 (dsh 0.1.0-rc.6). For newer versions, issues/PRs are welcome to correct.*
