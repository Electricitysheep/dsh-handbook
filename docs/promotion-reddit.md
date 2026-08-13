# DeepSeek Harness (dsh) — zero-to-one handbook with a 3-agent benchmark

**Repo**: https://github.com/Electricitysheep/dsh-handbook (MIT, bilingual 中文/EN, PDF included)

DeepSeek open-sourced its agent runtime **DeepSeek Harness (dsh)** yesterday (2026-08-13) — "everything is a plugin" architecture on Cordis, with `web` + `headless` profiles and a plugin ecosystem. Official docs are architecture-focused, so I wrote the missing beginner path:

**What's inside (7 chapters, every command verified on real hardware):**
1. Understanding dsh (what a harness is, vs Claude Code/Codex/OpenCode)
2. 5-min quickstart (web + headless, reasoning-effort tiers)
3. Profiles & the plugin system (extension points, real pitfalls)
4. Plugin development hands-on (full working code: `agent/request` waterfall + pure-function policy)
5. Real-world cases (3 actual open-source PRs broken down)
6. Performance tuning (thinking time is ~90% of tool-chain latency)
7. Ecosystem & how to join

**Bonus: same-model × different-agent benchmark** (all on deepseek-v4-flash, same gateway, same key, 3 rounds median):

| Agent | 3 tasks total | Correct |
|---|---|---|
| omp | 36s | 27/27 |
| dsh | 85s | 27/27 |
| opencode | 114s | 27/27 |

Same model → capability is equal (27/27); the difference is agent-engineering efficiency.

Also shipped: [dsh-tool-turbo](https://github.com/Electricitysheep/dsh-tool-turbo) — a plugin that auto-downgrades reasoning effort for simple tool rounds (live-verified `high → low` in dsh logs).

Feedback / issues / translation PRs welcome. Star if useful ⭐
