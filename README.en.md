# DeepSeek Harness Handbook · dsh-handbook

> **From zero to one with DeepSeek Harness — the beginner's encyclopedia for DeepSeek's open-source agent runtime.**
> English · [中文](./README.md)

**📖 [Read online](https://electricitysheep.github.io/dsh-handbook/) · 📄 [Download PDF](./DeepSeek-Harness-Handbook.pdf) · ⭐ [Star us](https://github.com/Electricitysheep/dsh-handbook/stargazers)**

<p align="center">
  <img src="./docs/assets/banner.svg" alt="dsh-handbook banner" width="720"/>
</p>

<div align="center">

![GitHub stars](https://img.shields.io/github/stars/Electricitysheep/dsh-handbook?style=flat&color=yellow)
![GitHub release](https://img.shields.io/github/v/tag/Electricitysheep/dsh-handbook?label=release&color=success)
![dsh-handbook](https://img.shields.io/badge/dsh--handbook-handbook-blue)
![chapters](https://img.shields.io/badge/chapters-15-green)
![pdf](https://img.shields.io/badge/PDF-1.6MB-orange)
![license](https://img.shields.io/badge/license-CC--BY--NC--SA--4.0-lightgrey)
![dsh](https://img.shields.io/badge/dsh-0.1.0--rc.8-8A2BE2)

</div>

> [!WARNING]
> dsh is currently at `0.1.0-rc.8` (pre-release). API/config may change with breaking changes; evaluate carefully before production use.

## 🚀 30-Second Quickstart

```bash
# 1. Install (needs Node.js ≥ 22)
npx -y @deepseek-ai/dsh web

# 2. Open http://127.0.0.1:3080 and start chatting
# 3. Or run a one-shot task (scripts / CI)
dsh --profile headless "Hello, introduce yourself in one sentence"
```

<p align="center">
  <img src="./docs/assets/demo-webui.gif" alt="dsh Web UI live demo" width="720"/>
  <br/>
  <sub><b>30 seconds to "get it"</b>: new session → type a task → pick model → send → AI replies</sub>
</p>

> Want the full path? [🗺 3-day learning path](./docs/roadmap.md) · Jump straight in: [Chapter 2: 5-min quickstart](./docs/02-quickstart.en.md) · Cheat sheet: [📇 one-page card](./docs/cheatsheet.md)

## 🎯 What Is DeepSeek Harness

**DeepSeek Harness (`dsh`)** is the agent runtime open-sourced by DeepSeek on 2026-08-13 — an "everything is a plugin" framework built on Cordis, with `web` + `headless` profiles and a plugin ecosystem.

<img width="614" height="230" alt="dsh overview" src="https://github.com/user-attachments/assets/19482c24-2208-468e-ad38-9096d9270f8d" />

But the official docs focus on architecture — **the beginner path is missing**. This handbook fills it: from "what is an agent runtime" to install, usage, plugin development and performance tuning. **Every chapter is copy-paste runnable and verified on real hardware. Any developer can go from zero to productive.**

### Why read this (instead of the official docs)

| Official docs | This handbook |
|---|---|
| Architecture view (AGENTS.md / architecture.md) | **Beginner view**: a zero-to-one path |
| Scattered examples | **Every chapter runnable**, commands verified |
| English only | **Bilingual**, Chinese-first + English chapters |
| No ecosystem practice | **Real plugin/PR breakdowns** (pitfalls & safety included) |

## 🎁 What You Get

| If you are… | You get |
|---|---|
| 🆕 **New to dsh** | A 3-day zero-to-one path (daily goals + acceptance checks) |
| 🛠 **A developer** | Clone-and-run plugin template + full config reference |
| ⚖️ **Evaluating options** | 6-agent comparison (table + prose) + same-model benchmark |
| ⚡ **Tuning for speed** | Reasoning-effort strategy + cache-hit deep dive (measured ~97%) |
| 📚 **Looking for cases** | 5 real complex cases (with timing / artifacts / verification) |

## 📚 Table of Contents (Zero → One)

### 🟢 Stage 1 · Understand & Onboard

<div align="center">

| 📖 **[Ch. 1 · Understanding Harness](./docs/01-intro.en.md)** | ⚡ **[Ch. 2 · 5-Minute Quickstart](./docs/02-quickstart.en.md)** |
|---|---|
| What it is, vs Claude Code/Codex/OpenCode, capability matrix | Install, web/headless modes, reasoning effort, troubleshooting |

</div>

### 🔵 Stage 2 · Build: Skeleton & Plugins

<div align="center">

| 🧩 **[Ch. 3 · Profiles & Plugin System](./docs/03-profiles.en.md)** | 🛠️ **[Ch. 4 · Plugin Dev, Hands-On](./docs/04-plugin-dev.en.md)** |
|---|---|
| Customizable skeleton, mounting, host/client halves, extension points, real pitfalls | Write your first plugin (full code + tests + live verification) |

</div>

### 🟠 Stage 3 · Practice: Scenarios & Tuning

<div align="center">

| 📦 **[Ch. 5 · Real-World Cases](./docs/05-cases.en.md)** | 🚀 **[Ch. 6 · Advanced & Performance](./docs/06-advanced.en.md)** |
|---|---|
| 3 real open-source PRs, cache-hit-rate deep dive, industry views | reasoning_effort strategy, latency analysis, 7 pitfalls |

</div>

### 🟣 Stage 4 · Ecosystem: Capability & Orchestration

<div align="center">

| 🌐 **[Ch. 7 · Ecosystem & Resources](./docs/07-ecosystem.en.md)** | 🧰 **[Ch. 8 · Tools & Context System](./docs/08-tools-context.en.md)** | 🔗 **[Ch. 9 · MCP, Subagents & Workflows](./docs/09-mcp-subagent-workflow.en.md)** |
|---|---|---|
| Official entry points, how to join, reading paths | 60+ capability packages, built-in tools, compaction | External tools, parallel subagents, multi-step orchestration |

</div>

### 🔴 Stage 5 · Advanced: Complex Cases & Outlook

<div align="center">

| 🧪 **[Ch. 10 · Complex Real Cases](./docs/10-complex-cases.en.md)** | 🔮 **[Ch. 11 · Future Outlook](./docs/11-future.en.md)** | ⚠️ **[Ch. 12 · Known Limitations](./docs/12-limitations.en.md)** |
|---|---|---|
| Run live in dsh: data pipeline 186s, 5-bug fix 94s | Tech / ecosystem / competition / risk predictions | rc instability, Windows bugs, early ecosystem — honest edition |

</div>

<div align="center">

| 🛡️ **[Ch. 13 · Security & Sandbox](./docs/13-security.en.md)** | 💰 **[Ch. 14 · Cache & Cost](./docs/14-cost.en.md)** |
|---|---|
| sandbox model · permissions · approval flow · plugin audit checklist | cache hit 97% · cost model · reasoning-effort × cost · budget |

| 📊 **[Ch. 15 · Ecosystem Report](./docs/15-ecosystem-report.en.md)** | |
|---|---|
| 1,804 plugins × 780 posts cross-validated: 5 insights + 6 capability gaps + advice for ecosystem players |

</div>

### 📎 Appendix

<div align="center">

| 📚 **[App. A · Glossary](./docs/appendix-glossary.md)** · 📦 **[App. B · Official Packages](./docs/appendix-packages.md)** · 📊 **[App. C · Benchmark](./docs/benchmark.md)** |
|---|
| 30+ terms · command cheatsheet · official @deepseek-ai/* package list · same-model 3-agent benchmark |

</div>

## 💎 Key highlights (open to read, not just links)

<details>
<summary><b>📖 Ch. 1 — three intuitions + capability matrix</b></summary>

- dsh = the LEGO base for agents; harness = the engineering layer around the model; 2026 = the programmable-agent era
- MIT · TypeScript · "everything is a plugin" · released 2026-08-13
- dsh vs 5 agents (Claude Code / Codex / OpenCode / Gemini / Kimi): open-source ✅, model-agnostic ✅, **official-grade plugin system** (unique), custom UI ✅, headless CI ✅
</details>

<details>
<summary><b>⚡ Ch. 2 — 30 seconds to running</b></summary>

- One command: `npx -y @deepseek-ai/dsh web` → http://127.0.0.1:3080
- Dual modes: web (chat UI) / headless (`dsh --profile headless "task"`, CI-friendly)
- Reasoning effort: `low` (fast/simple) · `high` (default) · `max` (hard reasoning) — **thinking is ~90% of tool-chain latency**
</details>

<details>
<summary><b>🧩 Ch. 3 — profiles & the plugin system</b></summary>

- profile = bundle stack + your patch layer (`package.json` + `cordis.patch.yml`)
- Mounting a plugin = 2 edits (add dependency + add insert line)
- host/client halves: one npm package = Node-side tools/services + browser-side UI
- 5 extension points + 6 real pitfalls (rc.1 dependency breakage, missing `main`, un-awaited `next()`…)
</details>

<details>
<summary><b>🛠 Ch. 4 — plugin development, full working code</b></summary>

- From-scratch speed-up plugin (full walkthrough): pure-function decision + `agent/request` waterfall injection
- Key trick: extract decision logic into pure functions (millisecond unit tests) → verify only "did injection happen" on real hardware
- Live log evidence: `calls=[{name:"write"}] => reasoningEffort=low`
</details>

<details>
<summary><b>📦 Ch. 5 — three real open-source PRs, end to end</b></summary>

- Git panel push/pull/fetch (PR #10): `--force-with-lease` safety line + local bare-repo integration tests + Playwright verification
- HTML draft preview (PR #11): srcdoc decision pure function under sandbox constraints
- Speed-up plugin example: step-by-step reasoning downgrade
</details>

<details>
<summary><b>🚀 Ch. 6 — where the time goes</b></summary>

- Performance model: ~90% of tool-chain time is model thinking (before every tool call)
- Strategy: `low` for simple rounds / `high` daily / `max` complex — **downgrading is the highest-leverage speedup**
- 7 real pitfalls, incl. the evaluation trap "task suddenly faster = cache hit"
</details>

<details>
<summary><b>🌐 Ch. 7 — the map to the dsh ecosystem</b></summary>

- Official entry: repo / API docs / Discord / Discussions
- Current status: official repo isn't accepting external PRs → **plugins are the named contribution path**
- Beginner path: use it → small PR → ship a plugin → write content
</details>

<details>
<summary><b>🧰 Ch. 8 — tools & context system</b></summary>

- 60+ official capability-package map: tools/context/session/subagents/MCP/workflows/security
- Built-in tools (verified): read/write/grep/glob/edit/bash/todo/skill
- Artifact tracking: tool returns locations → open at end of conversation
- Context injection (layered system prompt + skill catalog), auto-compaction, sandbox/permission/approval security layer
</details>

<details>
<summary><b>🔗 Ch. 9 — MCP, subagents & workflows</b></summary>

- MCP: connect external tool servers (community token-tracking plugin exists)
- Subagents: parallel delegation (large-repo research / long-task decomposition)
- Workflows: deterministic multi-step orchestration (fetch → clean → report → verify)
- 4-stage path: single agent → +MCP → +subagents → +workflows
</details>

<details>
<summary><b>🧪 Ch. 10 — complex cases actually run by dsh</b></summary>

- Case A: data-quality analysis → cleaning → visualization (186s, chart.png, trade-offs documented)
- Case B: 5-bug fix + 49 tests (94s, pytest 49 passed, edge cases covered)
- Profile: auto-orchestrated tool chains, real judgment, traceable artifacts
- Privacy: all synthetic data / self-written code
</details>

<details>
<summary><b>📚 Appendix — glossary + commands</b></summary>

- 30+ terms: harness/profile/bundle/cordis/extension point/waterfall/compaction…
- Command cheatsheet: dsh core / env / troubleshooting / plugin dev
- Benchmark: same-model 3-agent (3-round median)
</details>

<details>
<summary><b>🔮 Ch. 11 — future outlook across five dimensions</b></summary>

- Tech / ecosystem / competition / opportunity / risk predictions + timeline
- Opportunity: the ecosystem is day-zero — building dsh-plugin projects is the early-mover entry point
</details>

<details>
<summary><b>⚠️ Ch. 12 — known limitations & boundaries (rc honest view)</b></summary>

- Instability: fast rc iterations, frequent breaking changes
- Early ecosystem: 60+ official packages but plugin ecosystem just starting
- Cross-platform gaps: Windows-family pitfalls (incl. the Node version red line)
</details>

<details>
<summary><b>🛡️ Ch. 13 — security & sandbox model</b></summary>

- Sandboxing: process isolation (bwrap/Landlock/Seatbelt) + permission tiers + approval flow
- Community-audited boundaries: node:vm is not a security boundary, approval loops, recursive workspace-write deletion
- Plugin security audit checklist (third-party audit methodology, [#454](https://github.com/deepseek-ai/deepseek-harness/discussions/454))
</details>

<details>
<summary><b>💰 Ch. 14 — cache & cost engineering</b></summary>

- Caching: context cache + measured hit rate 97% (Flash discount 98% / Pro 99%+)
- Cost model: where tokens go + reasoning-effort interplay + real-task budgets
- Visibility: session logs / balance plugins to see every cent of spend
</details>

<details>
<summary><b>📊 Ch. 15 — ecosystem panorama report (1,804 plugins × 780 posts)</b></summary>

- Data snapshot: 1,804 plugin repos (1,663 flagged "true DSH") — tools 569 / utility 345 / session 229 … sandbox only 9
- 5 insights: Windows = #1 pain point (60+ posts) · "community fills what the official side doesn't build" · security audits active but security tooling scarce · serialization/boundary bug family · cost transparency as a hidden must-have
- 6 capability gaps (data + discussion double-verified): vision channel · memory seam · desktop/TUI shell protocol · evaluation loop · first-class Windows support · plugin registry
- Advice for plugin developers / evaluators / onlookers — full report: [Ch. 15](./docs/15-ecosystem-report.en.md)
</details>

## 🖥 Demo

### ① Web UI chat (`dsh web`)

```bash
dsh web    # → http://127.0.0.1:3080
```

![dsh Web UI chat](./docs/assets/demo-web-chat.png)

### ② Headless CLI (one-shot task, scripts/CI)

```bash
dsh --profile headless "Hello, introduce yourself in one sentence"
# → Hello! I'm a DeepSeek-powered AI coding assistant...
```

### ③ Plugin ecosystem (Git panel, `dsh-better-sidebar`)

![dsh Git panel (better-sidebar plugin)](./docs/assets/demo-git-panel.png)

## 🧰 Quick Assets (Essentials Right Here)

<details>
<summary><b>📇 One-page cheatsheet</b> — install · commands · reasoning effort · troubleshooting</summary>

```bash
npx -y @deepseek-ai/dsh web          # install & launch Web UI
dsh --profile headless "task"        # one-shot task (scripts/CI)
```
Reasoning effort: `low` (fastest/simple) · `high` (default) · `max` (hardest)
> Full card: [docs/cheatsheet.md](./docs/cheatsheet.md)
</details>

<details>
<summary><b>🔧 Plugin template</b> — mount in 2 steps</summary>

```yaml
# ① package.json dependency
"my-plugin": "link:C:\\path\\to\\my-plugin"
# ② cordis.patch.yml mount
- insert:
    - id: my-plugin
      name: my-plugin
```
```bash
cd ~/.dsh/profiles/web && pnpm install && dsh web
```
> Clone-and-run template (pure functions + waterfall + tests): [examples/plugin-template/](./examples/plugin-template/README.md)
</details>

<details>
<summary><b>⚙️ Config reference</b> — settings.yaml core</summary>

```yaml
agent-default-model:
  model: deepseek-v4-flash    # or deepseek-v4-pro
  reasoningEffort: high       # off (fastest/no thinking) / high (default) / max (strongest)
                              # Note: 'low' is only for custom gateways (pi-ai); the official DeepSeek adapter accepts off/high/max only
```
> Full reference (profile/cordis.patch.yml/scenarios): [docs/config-reference.md](./docs/config-reference.md)
</details>

<details>
<summary><b>❓ FAQ Top 5</b></summary>

1. **Is dsh a model?** No — a runtime; models plug in via the llm plugin
2. **vs Claude Code?** Claude Code is the "whole car"; dsh is the "LEGO base" (open, customizable)
3. **Does it cost money?** dsh is free/open-source; conversations billed per use (cache discount: Flash tier 98% / Pro tier 99%+, ~97% session cache hit rate measured)
4. **Plugin 404?** rc.1 dependency breakage — pin the `^0.1.0-rc.8` line
5. **Production-ready?** rc stage has breaking changes; ecosystem play is fine now
> Full FAQ: [docs/faq.md](./docs/faq.md)
</details>

## ⚖️ dsh vs mainstream agents (capability matrix)

| Dimension | **dsh** | Claude Code | OpenAI Codex | OpenCode | Gemini CLI | Kimi CLI |
|---|---|---|---|---|---|---|
| Open source | ✅ MIT | ❌ | ❌ | ✅ MIT | ❌ | ❌ |
| Model binding | model-agnostic | Claude family | GPT family | any | Gemini family | Kimi family |
| **Plugin system** | **official-grade: everything is a plugin, 60+ packages** | config/hooks | config | config | none | none |
| Custom UI | ✅ (client half) | ❌ | ❌ | partial | ❌ | ❌ |
| Automation/CI | ✅ headless | ✅ | ✅ | ✅ | ✅ | ✅ |
| TUI | plugin-able | ✅ built-in | ✅ built-in | ✅ built-in | ✅ | ✅ |
| Ecosystem stage | day zero (2026-08-13) | mature | mature | mature | mature | early |
| Best for | deep customization + ecosystem | out of the box | out of the box | OpenCode users | Google | Kimi |

## 📊 Same model × different agents (measured 2026-08-13)

> Same model `deepseek-v4-flash` (same gateway, same key) — only the agent engineering layer differs. All 5 tasks completed correctly; the difference is efficiency:

| Agent | Total time | Correct |
|---|---|---|
| **omp** | **70s** | 45/45 ✅ |
| **dsh** | **130s** | 45/45 ✅ |
| **opencode** | 172s | 45/45 ✅ |

> 5 tasks × 3 rounds, median; all 45/45 correct. Full methodology: [📊 Benchmark appendix](./docs/benchmark.md)

<p align="center">
  <img src="./docs/assets/benchmark-bar.svg" alt="benchmark bar chart: omp 70s / dsh 130s / opencode 172s" width="720"/>
</p>


## 📄 PDF

- **Chinese full edition**: [DeepSeek-Harness-白皮书.pdf](./DeepSeek-Harness-白皮书.pdf) (15 chapters + appendices A–C, ~130k+ chars, 5.5MB, professional typesetting: cover/TOC/styles)
- **English edition**: [DeepSeek-Harness-Handbook.pdf](./DeepSeek-Harness-Handbook.pdf) (14 chapters + appendices, 81 pages, ~150k chars, 1.6MB, professional typesetting: cover/TOC/styles; appendices in Chinese original — EN edition covers 14 chapters; Ch. 15 available online)

## 🌐 Ecosystem Links

Methodology comes from real open-source work:
- [DSH-better-sidebar](https://github.com/omdsh-dev/DSH-better-sidebar) — community sidebar plugin (ch. 5 cases)

### 🧩 Recommended Community Plugins (from Official Discussions / [awesome-dsh-plugin](https://github.com/awesome-dsh-plugin/awesome-dsh-plugin))

| Plugin | Description |
|---|---|
| [dsh-specflow](https://github.com/lonelymoon87/dsh-specflow) | Spec-driven development: skills, commands, target tracking, progress context |
| [dsh-gitflow](https://github.com/lonelymoon87/dsh-gitflow) | Approval-gated Git workflows (status/diff/commit/branch) |
| [dsh-guardian](https://github.com/lonelymoon87/dsh-guardian) | Guardrails: dangerous operation policy check + output sanitization |
| [dsh-code-intel](https://github.com/lonelymoon87/dsh-code-intel) | Tree-sitter code symbol indexing + hybrid search |
| [dsh-tianshu-tui](https://github.com/huiliyi37/dsh-tianshu-tui) | Terminal UI (TUI) for dsh |
| [dsh-computer-use](https://github.com/Anionex/dsh-computer-use) | Accessibility-first macOS computer control |
| [dsh-data-agent](https://github.com/omdsh-dev/dsh-data-agent) | Database connection & SQL-writing agent |
| [dsh-balance-meter](https://github.com/Ghost011118/dsh-balance-meter) | Real-time balance and session cost tracking |

> Full list at [awesome-dsh-plugin](https://github.com/awesome-dsh-plugin/awesome-dsh-plugin) (122+ plugins). Want yours listed? [Community Case Submissions](https://github.com/Electricitysheep/dsh-handbook/discussions/12)

### 📣 Active on Official Discussions

Active on [deepseek-ai/deepseek-harness](https://github.com/deepseek-ai/deepseek-harness) Discussions — 8 threads: #380 plugin pitfalls / #401 Windows path bugs / #392 TUI suggestions / #384 visionDS / #118 / #655 community five projects / #735 token cost / #781 LSP proposal

## 🙏 Contribute

- ⭐ Found it useful? Star it — it drives continued updates
- 📝 **Run a real case?** Submit it to be featured in the handbook (with author credit + quarterly curated PDF): [Community Case Submissions](https://github.com/Electricitysheep/dsh-handbook/discussions/12) ← reply directly, template ready
- Commands broken? rc releases iterate fast — open an issue
- Want to help? See [CONTRIBUTING.md](./CONTRIBUTING.md) · [ROADMAP.md](./ROADMAP.md) · [Ch. 7: Ecosystem](./docs/07-ecosystem.en.md)

## ℹ️ Version

- Based on dsh `0.1.0-rc.8` / DeepSeek-V4-Flash-0731 (open-sourced 2026-08-13)
- Verified on Windows 11 + Node 24

## 📜 License

Content [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) · Example code MIT
