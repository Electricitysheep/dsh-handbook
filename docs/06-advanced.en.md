[English](./06-advanced.en.md) | [中文](./06-advanced.md) · [← Back](../README.md)

# Chapter 6: Advanced & Performance Tuning

> **Goal of this chapter:** Go from "it runs" to "it runs well" — reasoning effort strategy, tool-call latency analysis, and a real-world pitfall checklist.

## 6.1 Performance Model: Where Does dsh Spend Its Time

Measured latency breakdown for a "create a file" task:

| Phase | Share | Notes |
|---|---|---|
| Model thinking (Think) | ~90% | **Re-thinks before every tool call** — the overwhelming majority |
| Tool execution | <1% | File writes and similar, millisecond-level |
| Network / rendering | ~10% | API round-trip + UI updates |

**Implications:**
- Simple tasks → optimize thinking time (lower reasoning effort)
- Long tool-chain tasks → save thinking time at every step; cumulative gains are largest
- Slow tools themselves (search / large files) → optimize the tool implementation, not the effort level

## 6.2 reasoning_effort Strategy (Official Three Tiers)

| Tier | Recommended Use |
|---|---|
| `low` | Simple / deterministic turns: file operations, batch jobs, cheap steps in a tool chain |
| `high` | Everyday agent tasks (default) |
| `max` | Complex reasoning, long-chain planning, debugging |

**Manual:** The "Reasoning Level" selector in the UI, or `reasoningEffort` in `~/.dsh/settings.yaml`.
**Automatic:** A plugin dynamically downgrades per tool turn (`dsh-tool-turbo`, Chapter 4).

## 6.3 Tool-Call Latency Visualization

dsh's session stats line (at the bottom of the Web UI) shows: `N turns · M steps | LLM Xs · Tool calls Ys | Avg first token ...` — this is the fastest way to locate bottlenecks.

Advanced: A host plugin can listen to tool events for per-tool timing (tool-turbo already includes a host-side logging version), surfacing "which tool is the slowest."

## 6.4 Pitfall Checklist (Battle-Tested, with Fixes)

| # | Pitfall | Symptom | Fix |
|---|---|---|---|
| 1 | rc.1 broken dependency chain | `pnpm install` 404 (`dsh-type-meta` etc. were never published) | Use the `^0.1.0-rc.6` dependency line |
| 2 | Plugin missing `main` | `No "exports" main defined` | Expose a `.` entry; `"main": "src/index.ts"` can be loaded by tsx |
| 3 | `next()` not awaited | Provider/model lost, error thrown | `next()` in `agent/request` returns a Promise; must await |
| 4 | Event type not recognized | `'agent/request' is not assignable to keyof Events` | npm doesn't re-export type augmentations; relax the signature at the boundary |
| 5 | Client tests won't run | jsdom reports `window.__ModuleLoader__` undefined | Client artifacts depend on dsh's bootstrap mechanism; run component tests in official CI |
| 6 | Misattributing "suddenly faster" on simple tasks | 1s vs 110s difference misattributed | DeepSeek context cache hits also speed things up — A/B tests must use a fresh prompt |
| 7 | Port conflict | `dsh web` won't start | `netstat -ano | findstr 3080` to find the PID, then kill it |

## 6.5 Evaluation Perspective: Official Scorecards vs. Independent Benchmarks

(With the 0813 official release in mind) When reading agent model scorecards, ask three questions:
1. **Who tested it?** Official self-tests (their own harness) vs. independent third parties (AA, etc.)
2. **Which harness?** Different frameworks yield very different scores (official Terminal-Bench 87.9 vs. AA independent 79)
3. **How strict is the verifier?** Lenient verifier (SWE-bench Verified has 8.5% false positives) vs. strict (DeepSWE 0.3%)

dsh's `agent/request` waterfall makes model benchmarks reproducible. That's an engineering advantage over closed-source products.

---

**Next chapter**: [Chapter 7: Ecosystem & Resources](./07-ecosystem.en.md) (planned).
