[English](./06-advanced.en.md) | [中文](./06-advanced.md) · [← Back](../README.md)

# Chapter 6: Advanced & Performance Tuning

> **Goal of this chapter:** Go from "it runs" to "it runs well" — reasoning effort strategy, tool-call latency analysis, and a real-world pitfall checklist.

## TL;DR (30-second version)

1. **Where the time goes**: model thinking takes ~90%, tool execution <1%, network/rendering ~10%. Optimizing thinking time is the highest-leverage speedup.
2. **Three-tier strategy**: `low` (simple/batch turns), `high` (everyday default), `max` (complex reasoning/debug). Choose manually via the UI or let a plugin adjust automatically.
3. **Latency visualization**: the stats line at the bottom of the Web UI (`LLM Xs / Tool calls Ys`) is the fastest way to locate bottlenecks.
4. **Seven real pitfalls**: rc.1 dependency break, missing plugin `main`, un-awaited `next()`, unrecognized event types, client tests that won't run, cache-hit misattribution, port conflicts.
5. **Evaluation three questions**: who tested it, which harness, how strict is the verifier. Always read benchmarks with context.

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
**Automatic:** A plugin dynamically downgrades per tool turn (example speed-up plugin, Chapter 4).

## 6.3 Tool-Call Latency Visualization

dsh's session stats line (at the bottom of the Web UI) shows: `N turns · M steps | LLM Xs · Tool calls Ys | Avg first token ...` — this is the fastest way to locate bottlenecks.

Advanced: A host plugin can listen to tool events for per-tool timing (the example speed-up plugin already includes a host-side logging version), surfacing "which tool is the slowest."

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

## Hands-on exercises

1. **Measure your own task**: run a simple file-creation task in `dsh web`. Check the stats line at the bottom. What's the LLM time vs tool-call time? Does it match the 90% / <1% split?
2. **Effort comparison**: run the same task twice, once with `reasoningEffort: low` and once with `high`. Compare wall-clock time and output quality. When is `low` good enough?
3. **Pitfall hunt**: open the pitfall checklist (Section 6.4). For each of the 7 pitfalls, try to reproduce it (or find a log/example where it occurred). Write down the fix.
4. **Plugin timing**: if you've built the example speed-up plugin (Chapter 4), check its logs. How much time does each step save? Calculate the cumulative gain over a 50-step task.
5. **Benchmark skepticism**: find an official DeepSeek benchmark scorecard. Ask the three evaluation questions (Section 6.5). What harness did they use? How strict was the verifier?
6. **Think**: why does dsh re-think before every tool call? What would happen if it cached the reasoning across steps? What are the trade-offs?

## FAQ

- **Q: Why is model thinking 90% of the time?** Because dsh uses a reasoning model that generates a chain-of-thought before every action. In a multi-step task, each step triggers a new reasoning pass. This is by design for quality, but it's slow.
- **Q: Can I just set `reasoningEffort: low` forever?** For simple, deterministic tasks (file ops, batch jobs), yes. For complex reasoning, planning, or debugging, you'll get better results with `high` or `max`. The plugin approach (Chapter 4) gives you dynamic adjustment.
- **Q: Why did my task suddenly run 100x faster?** Likely a context-cache hit. DeepSeek's API caches repeated input tokens at a 98% discount. If your prompt/history is similar to a previous request, most tokens hit cache. This is a good thing, but it makes A/B testing tricky (use fresh prompts).
- **Q: What's the "overflow agent" in compaction?** When a conversation exceeds the context window and compression fails, dsh routes to a fallback "overflow agent" that tries to salvage the task. It's a last-resort mechanism.
- **Q: How do I read the stats line?** `N turns · M steps | LLM Xs · Tool calls Ys | Avg first token ...` — LLM time is total model thinking, tool-call time is total tool execution. If LLM time dominates, lower the effort. If tool time dominates, optimize the tool.
- **Q: Are official benchmarks reliable?** They're a starting point, but always ask: who tested it, which harness, how strict is the verifier. Independent benchmarks with strict verifiers are more trustworthy.

---

**Next chapter**: [Chapter 7: Ecosystem & Resources](./07-ecosystem.en.md) (planned).
