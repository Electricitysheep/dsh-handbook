[English](./05-cases.en.md) | [中文](./05-cases.md) · [← Back](../README.md)

# Chapter 5: What dsh Can Do for You — Application Scenarios

> Goal: step out of the "how to build dsh" lens and look from the **user's** perspective — where dsh genuinely helps in daily work. Every scenario has a copy-paste task example with real measured timing.

## TL;DR (30-second version)

1. **dsh is a general-purpose agent runtime** — not just a coding assistant: data analysis, documentation, automation, and code comprehension all work.
2. **Five core scenarios**: daily coding / data processing / documentation & knowledge / automation & ops / code understanding & refactoring.
3. **One usage pattern**: describe the goal in one sentence + state the acceptance criteria; dsh orchestrates the toolchain itself.
4. **Real speed**: simple tasks in seconds, complex multi-step tasks in 1–5 min (V4-Flash + high effort, measured).
5. **Golden prompt rule**: tell dsh *what "done" looks like* ("run and verify") — more effective than describing the process.

## 5.1 Scenario overview

| Scenario | Typical tasks | dsh tools | Measured |
|---|---|---|---|
| **Daily coding** | write functions, fix bugs, add tests | write / read / bash / grep | 5-bug fix + 49 tests: 94s |
| **Data processing** | clean, analyze, visualize, report | read / write / bash / python | clean + visualize: 186s |
| **Docs & knowledge** | API docs, tutorials, summaries, translation | read / write | API docs: 1m04s |
| **Automation & ops** | batch, CI tasks, log analysis | bash / headless | headless scripting |
| **Code understanding** | refactor, review, tech research | grep / glob / read / bash | refactor: 4m37s |

> All timings from real cases in [Chapter 10](./10-complex-cases.en.md) (synthetic data); see [benchmark](./benchmark.md).

## 5.1.1 High cache-hit rate: dsh's hidden cost weapon

**The most underrated advantage of the dsh ecosystem.** DeepSeek's API **context cache** bills repeated/similar input tokens at a discounted rate. Measured in real dsh sessions: **cache hit rate up to 97%**.

**Why dsh hits cache so often**:

| Reason | Explanation |
|---|---|
| Session continuity | multi-turn conversations repeat system prompt / skill catalog / history |
| Stable tool schema | every step carries the same tool definitions |
| Agent workload | multi-step tool chains repeatedly carry the same context |

**Cost impact (98% cache discount)**:

| Charge | Miss | Cache hit | Discount |
|---|---|---|---|
| Input (Flash) | $0.14/M | **$0.0028/M** | **98%** |
| Input (Pro) | $0.435/M | $0.003625/M | 99%+ |

**Practical meaning**: in a long agent session, most input tokens hit cache — a 50-step tool chain with 2.4M input tokens costs far less than the miss-price estimate. For high-frequency / batch / long-session workloads this is an order-of-magnitude advantage.

> To raise hit rate: keep sessions alive, keep prompt prefixes stable (don't churn system prompt/skill catalog), batch within the same session/prefix.

## 5.2 Scenario 1: Daily coding (best entry point)

**Typical tasks**: write a function/module from a spec; fix bugs (locate → modify → verify); add unit tests.

```bash
dsh --profile headless "Review buggy_calculator.py: find all bugs, fix them, write complete tests, run and verify all pass"
# measured: 5 bugs fixed + 49 tests pass (94s)
```

**Why dsh fits**: coding has the fullest toolchain — read files, write code, run commands, see results. Produced files are directly openable at the end of the conversation.

**Prompt tip**: always say "run and verify" — dsh closes the loop; "fix my bug" alone stops after editing.

## 5.3 Scenario 2: Data processing & analysis

```bash
dsh --profile headless "Analyze sales_data.json for quality issues (missing/type/duplicate/outliers), write a cleaning script + visualization script, run and verify, summarize your approach"
# measured: 52→35 rows zeroed + chart + trade-off notes (186s)
```

**Highlight**: dsh doesn't just execute — it explains trade-offs ("median imputation creates a spike", "whether to drop outliers depends on business") — direct evidence of an agent that *thinks*.

## 5.4 Scenario 3: Documentation & knowledge work

```bash
dsh --profile headless "Generate complete Markdown API docs for user_module.py (8 functions): params, returns, exceptions, examples, edge cases"
# measured: 423-line ReadTheDocs-style doc (1m04s), proactively flags contract-vs-implementation gaps
```

**Highlight**: defensive writing — notes calling traps (negative limit behavior, empty-argument behavior), flags where docs and code disagree.

## 5.5 Scenario 4: Automation & ops (headless is the ace)

```bash
# cron daily digest
dsh --profile headless "Read today's git log in the workspace and write a Chinese daily summary" > daily-report.md

# batch: convert all .txt in docs/ to .md
dsh --profile headless "Convert all .txt files under docs/ to .md (preserve structure)"
```

**Why headless is the ace**: full process-level tools + non-zero exit on failure + pipeable output — **an agent you can put in CI**.

## 5.6 Scenario 5: Code understanding & refactoring

```bash
dsh --profile headless "Refactor legacy_orders.py to OOP with separated responsibilities, keep behavior identical, write tests verifying output parity"
# measured: 17/17 tests pass incl. script-level artifact comparison (4m37s)
```

**Highlight**: engineering awareness — merges duplicated logic into one entry point, keeps backward compatibility, **notices a sandbox tempfile-permission issue and switches approach**.

## 5.7 Three prompt rules that make scenarios work

1. **State acceptance criteria, not process**: "run and verify" > "write a script" — dsh figures out the steps.
2. **Give context**: one sentence of background (where files are, what the data looks like, who the audience is).
3. **One task at a time**: split big goals into rounds of small closed loops.

## 5.8 Your first real task (15 minutes)

1. Make a test dir with a small file (code / data / notes).
2. Run: `dsh --profile headless "Summarize this file and list 3 improvement points"`.
3. Run: `dsh --profile headless "Write a test / generate docs for this file"`.
4. Compare output — did it give a real artifact, or a vague answer? Were your acceptance criteria clear enough?

## 5.9 Industry view: how dsh opens in different domains

> Same toolchain, different industries. Generic scenarios only (no real business data); regulated fields (medical/legal) require human review.

### Finance & research
`dsh --profile headless "Read this financial data and generate a summary with YoY/MoM changes"` — data pipeline + high cache hit make long-session reports cheap.

### Education & learning
`dsh --profile headless "Turn this chapter into 10 self-test questions with explanations"` — document generation + structuring are strong; batch question generation.

### Sales & support
`dsh --profile headless "Group 100 customer feedback entries by issue type and suggest improvements"` — batch text processing + classification.

### Operations & content
`dsh --profile headless "Read this week's data files and generate an ops weekly report (with chart code)"` — data + docs + automation combined.

### Research & review
`dsh --profile headless "Compare the methods and conclusions of these 3 papers, output a comparison table"` — long-doc processing + structured output (1M context).

### ⚠️ Compliance note
High-risk domains (medical diagnosis, legal advice, financial advice): dsh output needs human review — tools are sandboxed, but **content responsibility is on the user**.

---

## Hands-on exercises

1. **Scenario mapping**: classify 3 of your daily tasks into the five scenarios.
2. **Prompt comparison**: write two prompt versions for the same task — one describing process, one stating acceptance criteria — run both and compare.
3. **Headless scripting**: turn "daily git digest" into one cron/bash command; verify output.
4. **Multi-step task**: design a cross-scenario task (read code → generate docs → output report) and watch dsh orchestrate.
5. **Think**: which scenarios is dsh NOT suitable for? (Hint: real-time interaction, sensitive operations needing human approval.)

## FAQ

- **Q: Is dsh just a coding assistant?** No — its toolchain (read/write/run/search) makes it general; data/docs/automation all verified.
- **Q: How long do complex tasks take?** 1–5 min measured (V4-Flash); lower reasoning effort for speed (Ch.6).
- **Q: What if a task fails?** Trace the tool calls in output; usually the acceptance criteria were unclear — rewrite and rerun.
- **Q: Can it run automated?** Yes — headless + non-zero exit + pipeable output works in cron/CI.
- **Q: Is it safe?** Tool execution has sandbox + approval layers; sensitive ops should be human-confirmed (Ch.8).
- **Q: How is this different from using Claude Code directly?** Same-model capability is close, but dsh lets you customize toolchains/UI/plugins (Ch.1 matrix).

---

**Next**: [Chapter 6: Advanced & Performance Tuning](./06-advanced.en.md)
