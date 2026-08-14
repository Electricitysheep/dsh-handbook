[English](./14-cost.en.md) | [中文](./14-cost.md) · [← Back](../README.md)

# Chapter 14: Caching & Cost Engineering

> **Goal of this chapter:** Turn "it's cheap" from folklore into engineering — the conversation-cache mechanism, measured hit rates and how to improve them, the cost model, reasoning-tier interplay, real-task budgeting, and how to *see* where every token goes.

## TL;DR (30-second version)

1. **Cache is the #1 cost variable**: DeepSeek's context cache bills repeated input at a **98% discount (Flash) / 99%+ discount (Pro)** — agent workloads are input-heavy, so the hit rate directly determines the cost scale
2. **Measured hit rate in this handbook: 97%**: session continuity + stable tool schemas + the nature of multi-step agent workloads (Section 5.1.1); community long-run measurements reach 99.7% ([#560](https://github.com/deepseek-ai/deepseek-harness/discussions/560))
3. **Three hit-rate principles**: keep the session alive (don't keep creating new ones), keep the prefix stable (don't keep changing config), interrupt less (write clear acceptance criteria once)
4. **Two independent levers**: reasoning tier controls *how much thinking*, cache controls *the input unit price* — they stack, so `low` + high hit rate = the cheapest combination
5. **Cost must be visible**: the session stats line shows cache hit %; per-turn token counts are awaiting official implementation ([#735](https://github.com/deepseek-ai/deepseek-harness/discussions/735)) — until then, use the stats line + a community cost-tracker plugin

<details><summary>Chapter navigation</summary>
- [14.1 How Conversation Caching Works](#141-how-conversation-caching-works)
- [14.2 Measured Hit Rate: Where 97% Comes From](#142-measured-hit-rate-where-97-comes-from)
- [14.3 Optimizing the Hit Rate in Practice](#143-optimizing-the-hit-rate-in-practice)
- [14.4 Cost Model: How the Hit Rate Drives Your Bill](#144-cost-model-how-the-hit-rate-drives-your-bill)
- [14.5 Reasoning Tiers and Caching: the Cost Matrix](#145-reasoning-tiers-and-caching-the-cost-matrix)
- [14.6 Budget in Practice: Cost Estimate for Case A](#146-budget-in-practice-cost-estimate-for-case-a)
- [14.7 Measurement: Making Token Usage Visible](#147-measurement-making-token-usage-visible)
- [14.8 Cost Pitfall Checklist](#148-cost-pitfall-checklist)
- [14.9 Decision Recommendations at a Glance](#149-decision-recommendations-at-a-glance)
</details>

## 14.1 How Conversation Caching Works

DeepSeek's API **context cache** (prompt caching): repeated/similar input tokens are billed at the **cache price** instead of full price. dsh's input for every model request = system prompt + skill catalog + conversation history + tool schemas (Section 8.3) — **the stable prefix portion is the natural cache candidate**, which is why agent workloads have far higher cache potential than ordinary chat.

**Billing rules** (Section 5.1.1 pricing table):

| Charge | Miss price | Cache-hit price | Discount |
|---|---|---|---|
| Input (Flash) | $0.14/M | $0.0028/M | **98%** |
| Input (Pro) | $0.435/M | $0.003625/M | **99%+** |

**Input structure per request** (Section 8.3) — determines which tokens can hit:

```text
system prompt (stable) + skill catalog (stable) + conversation history (incremental) + tool schemas (stable) + this turn's messages (incremental)
      └────────────────────── cache-hit zone (repeated) ──────────────────────┘   └── miss zone (new increments) ──┘
```

**The bigger the hit zone and the smaller the increments → the higher the hit rate.** Once you understand this structure, the three optimization levers in 14.3 are all really "make the hit zone bigger."

**Cache isn't just cheaper, it's faster**: cold start with context injection takes ~110s on the first turn; a hot cache takes ~1s (measured in Chapter 1) — first-token time drops by an order of magnitude on hits.

> Detail note: hits depend on "repeated/similar prefix"; the exact matching rule is decided API-side (inferred, pending verification). In practice, "keep the prefix stable" is enough to reliably capture the discount.

## 14.2 Measured Hit Rate: Where 97% Comes From

This handbook measured a cache hit rate of up to **97%** in real dsh session stats (Section 5.1.1). Why dsh's hit rate is unusually high:

| Reason | Explanation |
|---|---|
| Session continuity | Multiple turns in one session repeat the system prompt / skill catalog / history → hits |
| Stable tool schemas | Every step carries the same tool definitions → hits |
| Agent workload nature | Multi-step tool chains repeatedly carry the same context → naturally high hit rate |

**Boundary (honest edition)**: 97% depends on "repetitive conversation patterns" — **brand-new tasks / cold starts drop noticeably** (Section 12.5). Community long-run measurements reach **99.7%** ([#560](https://github.com/deepseek-ai/deepseek-harness/discussions/560)), confirming "longer sessions → higher hit rates."

**How it was measured**: the "cache hit %" in the session stats line at the bottom of the Web UI (Section 6.6); the comparison baseline is 5.1.1's "50-step tool chain task, 2.4M input tokens" — a typical sample of the input scale.

| Metric | Where to look | Behavior on hits |
|---|---|---|
| Cache hit % | Session stats line (bottom of Web UI) | Stays high (97%+ in long sessions) |
| First token | Per-turn end line | Drops by an order of magnitude from 10s+ to under 1s (FAQ Q4 in Chapter 6) |
| Total tokens | Session overview | Small increments = the hit zone is growing (14.1 structure) |

## 14.3 Optimizing the Hit Rate in Practice

Three levers, ordered by cost-effectiveness:

| Lever | What to do | Why it works |
|---|---|---|
| **Session continuity** | Keep long tasks in one session; avoid creating new sessions frequently; batch tasks in the same session/prefix | Repeated history messages → hits |
| **Stable prompts** | Keep the system prompt / skill catalog prefix stable; don't churn config; keep tool schemas unchanged | Identical prefix → hits |
| **Fewer interruptions** | Write clear acceptance criteria once (Section 5.7 / the lesson in Chapter 10's cases) instead of "reopening sessions and re-explaining context" | Avoids rebuilding the prefix → full-price restart |

**Grounding check**: when the hit rate drops below expectations, the first thing to suspect is "did the prefix change?" — changing config, switching tiers, or touching the skill catalog all invalidate the cache (Section 6.6 monitoring line).

## 14.4 Cost Model: How the Hit Rate Drives Your Bill

**Cost model in one line** (Section 6.6): `total cost ≈ output tokens × output price + missed input × miss price + hit input × hit price` — agent workloads are input-heavy, so **the cache hit rate is the #1 cost variable**.

Using Chapter 5's Flash input prices, here's a worked example (**10k input tokens**, hit-rate comparison). Arithmetic sample (90% hits): `9,000 × $0.0028/M + 1,000 × $0.14/M ≈ $0.000165` — split hits from misses first, then multiply each by its own price:

| Hit rate | Hit tokens | Miss tokens | Input cost (Flash) | Relative cost |
|---|---|---|---|---|
| **90%** | 9,000 | 1,000 | ≈ $0.000165 | 1× |
| 50% | 5,000 | 5,000 | ≈ $0.000714 | ≈ 4.3× |
| **10%** | 1,000 | 9,000 | ≈ $0.001263 | ≈ 7.6× |

Scaled to 1M input tokens: 90% hits ≈ **$0.0165**, 10% hits ≈ **$0.126**, full price $0.14 — **nearly an order of magnitude apart**.

Scaled again to this handbook's measured scale (5.1.1: 50-step tool chain, 2.4M input tokens): 97% hits ≈ **$0.017** vs full price ≈ **$0.34** — roughly **20×**. That's the numerical source of 5.1.1's "cost far below the naive miss-price estimate."

> Note: this table only covers the input side — Chapter 5's pricing table only records input prices; for the output side, check the official pricing page. In input-heavy agent scenarios, the input side *is* the dominant variable.

## 14.5 Reasoning Tiers and Caching: the Cost Matrix

Reasoning tiers control "how much thinking," and cache is an **orthogonal lever**: tiers affect total token count, cache affects the input unit price, and they multiply. Fewer thinking tokens → lower total tokens (Section 6.6), and the context-repeated portion enjoys the cache discount too (inferred, pending verification).

| Tier | Thinking tokens | Relative cost | Best for (Section 6.2) | Cost strategy |
|---|---|---|---|---|
| `low` | Fewest | Lowest | Simple/deterministic turns: file ops, batch jobs, cheap steps in a tool chain | Default tier for batch jobs |
| `high` | Medium | Medium | Everyday agent tasks (default) | Default quality/cost balance |
| `max` | Most | Highest | Complex reasoning, long-chain planning, debugging | Fine for one-off complex tasks; don't run it in batch loops |

**How the levers combine:**

- **Long tool-chain tasks (20–50 steps) benefit the most**: the cumulative effect of downgrading thinking per step is significant (FAQ Q2 in Chapter 6) — both levers (tier × hit rate) act on every step
- Simple turns at `low` show almost no quality difference; complex reasoning at `low` may skip critical steps (FAQ Q3 in Chapter 6)
- **Stacked example** (2.4M-input-scale task, Flash prices): `low` + 97% hits ≈ under $0.017 (fewer thinking tokens → actually less; inferred, pending verification); `max` + repeated cold starts ≈ over $0.34 — **the same task is 20×+ apart with both levers fully on vs fully off**
- Note: `low/high/max` are the tier names of the gateway this handbook measured on (pi-ai/opencode-go); the default deepseek-official adapter uses `off/high/max` (Section 6.2 note)

## 14.6 Budget in Practice: Cost Estimate for Case A

Budget using Chapter 10's **Case A (data-quality analysis, 186s)** as the sample: tool chain `read → write(clean.py) → bash → write(visualize.py) → bash → read → summarize`, ~6–8 steps. Scaled from the 5.1.1 magnitude (50 steps ≈ 2.4M input tokens), Case A's input is roughly **500k tokens (inferred, pending verification)**:

| Scenario | Hit rate | Input cost (Flash, estimated) |
|---|---|---|
| Session continuity + stable prefix (recommended) | 97% | ≈ **$0.0035** |
| New session mid-way / prefix changed | 10% | ≈ $0.063 |
| Extreme: full price every time | 0% | $0.07 |

**Step-level breakdown** (why session continuity saves money) — only the first turn is a full-price cold start; every later turn misses only its small increment of "this turn's messages + tool results" (inferred, pending verification):

| Step | Content | Input tokens (inferred, pending verification) | Hit status |
|---|---|---|---|
| 1 | read(sales_data.json) | ~50k | Cold start (miss) |
| 2–6 | write/bash/write/bash/read/summarize | ~450k | Prefix hit zone, tiny increments |

**Conclusion**: a real 3-minute task costs under **1 cent** on the input side; the same work, done differently (session continuity vs repeated cold starts), differs by **~18×**. The output side (two scripts + summary) is orders of magnitude smaller than the input, so total cost stays in the single-digit cents (inferred, pending verification). This is the per-task source of "dsh with V4-Flash costs about 1/10 to 1/30 of Claude" (measured in Chapter 1).

## 14.7 Measurement: Making Token Usage Visible

**What exists today**:
- Session stats line at the bottom of the Web UI: `N turns · M steps | LLM Xs · Tool calls Ys | Avg first token ...` (Section 6.3)
- Per-turn end line: `10:14 · took 9m34s · first token 1.7s · 79 tok/s` ([#735](https://github.com/deepseek-ai/deepseek-harness/discussions/735) original-thread screenshot)
- Session overview shows total-token stats; the stats line shows "cache hit %" (Section 6.6)

**The gap**: **per-turn token counts**. Official discussion [#735](https://github.com/deepseek-ai/deepseek-harness/discussions/735) (filed 2026-08-14, title "【友好显示】希望在每轮对话中加入本轮对话token消耗量" / "Friendly display: add per-turn token usage to each turn", 2 comments) is exactly this request — confirmed to exist in the thread; not yet implemented officially.

**Community suggestion (already posted to #735's comment thread)**: the per-turn display should split into **two numbers** — ① total tokens this turn (quick glance at spend); ② hit/miss tokens this turn (see the optimization headroom). Looking at total tokens alone misleads: the same 10k tokens costs 7.6× more at a 90% vs 10% hit rate (see 14.4).

**Interim tooling**: the community `dsh-plugin-cost-tracker` (Sections 9.5/9.6; real-time token-cost tracking, plugin/MCP form) — implemented through Chapter 4's plugin extension points, tallying `usage` on request/session events (inferred, pending verification); or reconcile manually from session logs / the API usage field. Chapter 11 predicts "cache-hit-rate tooling" is the mid-term theme (11.2) — once #735 lands, the cost-transparency loop closes.

## 14.8 Cost Pitfall Checklist

| # | Pitfall | Symptom | Fix |
|---|---|---|---|
| 1 | Misreading cache hits as "the model got faster" | A/B comparison skewed by 1s vs 110s (Chapter 6 pitfall #6) | A/B tests must use a **fresh prompt** |
| 2 | Creating new sessions constantly burns money | Every task cold-starts; input billed at full price | Keep long/batch tasks in one session |
| 3 | Config changes silently kill the hit rate | Hit % suddenly drops; cost climbs | Monitor the hit % in the stats line; keep the prefix stable |
| 4 | Judging cost by total tokens alone | 10k tokens at 90% vs 10% differs by 7.6× | Split hit/miss and look at both (#735 suggestion) |
| 5 | Budget missing the output side | Input-only math doesn't add up | Add output prices from the official pricing page (Chapter 5 only lists input prices) |
| 6 | Tier roulette | `max` on batch jobs doubles the cost | Use `low` for batch, `max` only for complex tasks |

## 14.9 Decision Recommendations at a Glance

| Scenario | Recommendation |
|---|---|
| Long tool-chain tasks (20–50 steps) | `high` + session continuity + stable prefix; 2.4M-input scale ≈ $0.017 (97% hits) |
| Batch / simple turns | `low` + batched in the same session (biggest hit bonus) |
| Complex reasoning / debugging | `max` (quality over cost); cold start is acceptable for one-off tasks |
| Cost-sensitive batch processing | `low` + headless + serial in one session |
| Performance/cost comparison tests | Fresh prompt + fixed tier + median of multiple runs (Sections 6.4/6.6) |
| Hit rate dropping abnormally | Check whether the prefix changed first (config / skill catalog / model tier) |

---

## Hands-on exercises

1. **Understand**: why is "cache hit rate the #1 cost variable"? Use the 14.4 10k-token table to explain how many times more 90% costs vs 10% hits
   > Check yourself: the 14.4 comparison table (7.6×) and the 6.6 cost-model one-liner
2. **Hands-on**: run a 3-step task and watch the session stats line at the bottom of the Web UI and the per-turn end line (time / first token / tok/s); estimate how much of this task hit cache
   > Check yourself: the 14.7 measurement methods and the 6.3 stats-line format
3. **Hands-on**: run the same batch of tasks two ways — "a new session per item" vs "all in one session" — and compare wall-clock times; the new-session version will almost certainly be noticeably slower on the first turn (cold start)
   > Check yourself: 14.1's measured 110s cold start vs 1s hot cache
4. **Think**: why does "looking only at this turn's total tokens" misjudge cost? Which two numbers did the #735 comment thread suggest splitting the per-turn display into?
   > Check yourself: the "Community suggestion" paragraph in 14.7
5. **Hands-on**: using #735's suggested metric, manually split one session's total tokens into "hit/miss" parts, price them with 14.4's unit prices, and verify the "order of magnitude" claim
   > Check yourself: the 14.4 comparison table and the 14.2 measurement table

## FAQ

- **Q: What's the highest possible cache hit rate?** 97% measured in this handbook (Section 5.1.1); community long runs reach 99.7% ([#560](https://github.com/deepseek-ai/deepseek-harness/discussions/560)). But **brand-new tasks / cold starts drop noticeably** (Section 12.5) — the hit rate is a function of *how you work*, not a constant of the model.
- **Q: Does the `low` tier noticeably hurt quality?** Almost no difference for simple deterministic tasks (file ops, batch processing); complex reasoning, long-chain planning, and debugging at `low` can miss critical steps (FAQ Q3 in Chapter 6). Recommended: `high` for everyday, `low` for batch/simple tasks.
- **Q: When will the official per-turn token display ship?** [#735](https://github.com/deepseek-ai/deepseek-harness/discussions/735) is a feature request filed 2026-08-14 (2 comments) — **not implemented yet**. Until then: the session stats line's hit % + the community `dsh-plugin-cost-tracker` (Chapter 9).
- **Q: Do third-party gateways / self-hosted providers get the cache discount too?** The cache discount is a DeepSeek API-side capability (Chapter 5 pricing table); third-party gateways' cache support and billing must be checked on their own pricing pages (inferred, pending verification).
- **Q: Why does a task get noticeably faster after a cache hit?** The hit prefix doesn't need recomputing, so first-token time drops by an order of magnitude (cold start ~110s vs hot cache ~1s, measured in Chapter 1). Tell-tale sign: first token suddenly drops from 10s+ to under 1s — almost certainly a hit (FAQ Q4 in Chapter 6). Use fresh prompts for performance comparisons to avoid cache interference (Chapter 6 pitfall #6).

---

*Info as of 2026-08-14 (dsh 0.1.0-rc.6). Pricing and cache policy are subject to the official docs; items marked "(inferred, pending verification)" are extrapolations or estimates — corrections via PR after real-world testing are welcome.*
