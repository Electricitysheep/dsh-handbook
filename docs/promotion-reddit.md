# DeepSeek Harness (dsh) — zero-to-one handbook: 12 chapters + same-model multi-agent benchmark

**Repo**: https://github.com/Electricitysheep/dsh-handbook (bilingual 中文/EN, PDF, one-page cheatsheet)

DeepSeek open-sourced its agent runtime **DeepSeek Harness (dsh)** (2026-08-13) — "everything is a plugin" on Cordis, with `web` + `headless` profiles. Official docs are architecture-focused, so I wrote the missing beginner path — a 12-chapter handbook, every command verified on real hardware.

**What's inside (12 chapters):**
1. What dsh is (vs Claude Code / Codex / OpenCode) + capability matrix
2. 5-min quickstart (web + headless, reasoning-effort tiers low/high/max)
3. Profiles & the plugin system (extension points, 6 real pitfalls incl. rc.1 dependency breakage)
4. Plugin development hands-on (full working code: `agent/request` waterfall + pure-function policy)
5. Real-world cases (3 actual open-source PRs broken down + cache-hit-rate deep dive, measured 97%)
6. Performance tuning (thinking time is ~90% of tool-chain latency — lowering reasoning effort is the highest-leverage speedup)
7. Ecosystem & how to join (official repo not accepting external PRs yet → plugins are the named contribution path)
8. Tools & context system (60+ official capability packages)
9. MCP, subagents & workflows (the 4-stage path to Agent systems)
10. Complex real cases (dsh actually ran: data-cleaning pipeline 186s, 5-bug fix + 49 tests 94s)
11. Future outlook (tech / ecosystem / competition / risk)
12. **Known limitations — honest edition** (rc instability, Windows path bugs, early ecosystem)

**Bonus: same-model × different-agent benchmark** (all deepseek-v4-flash, same gateway, same key, 3 rounds median):

| Agent | Total time | Correct |
|---|---|---|
| omp | 36s | 27/27 ✅ |
| dsh | 85s | 27/27 ✅ |
| opencode | 114s | 27/27 ✅ |

Same model → capability is equal (27/27 all correct); the difference is agent-engineering efficiency. Useful when choosing your agent.

**Also included**: bilingual PDF (中文/EN), one-page cheatsheet, clone-and-run plugin template, config reference, FAQ.

For devs who want to build agents on DeepSeek, plugin developers, and anyone evaluating agent tools. Star + Issues welcome.
