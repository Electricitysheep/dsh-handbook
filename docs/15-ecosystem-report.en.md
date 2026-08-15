[English](./15-ecosystem-report.en.md) | [中文](./15-ecosystem-report.md) · [← Back](../README.md)

# Chapter 15: The dsh Ecosystem Panorama — What 1,800+ Plugins and 780 Discussion Posts Tell Us

> **Goal of this chapter:** Cross-validate the **community plugin inventory (1,804 plugins)** against **this handbook's 780-post discussion-board observations plus 195-post response experience**, and draw the panorama of the dsh ecosystem — where it's booming, where the gaps are, and where the opportunities lie.
> **Data sources:** the Blue-Whale-Harness plugin master list (community-maintained; 1,804 repos crawled 2026-08, of which 1,663 are flagged "true DSH"); discussion-board observations as of 2026-08.

## TL;DR (30-second version)

1. **The ecosystem is exploding**: 1,804 plugin repos grown from zero within two weeks; design/UI generation (348 / 94K★) and vision (132 / 90K★) are the hottest demand
2. **"Whatever the official side didn't build, the community did" is the theme**: desktop shells (140+), TUIs, memory, vision bridges — all filled in by the community
3. **Clear gaps**: finance (8), database (14), audio (19), evaluation (37) are nearly empty — yet the demand side exists
4. **Windows and remote are the sore spot**: the Chinese-path family (#107 and 15+ posts), subprocess (#717), LAN RPC (#755)
5. **The differentiation bet**: full session logs + everything-is-a-plugin + sandbox/permission system → enterprise / evaluation / compliance scenarios

---

## 15.1 Ecosystem Data Snapshot (1,804 repos)

### Category Distribution

| Category | Plugins | Read |
|---|---|---|
| tools | 569 | Tools are the hottest category (the core value carrier of an agent) |
| utility | 345 | General-purpose utilities |
| session | 229 | Session management (logs / recovery / statistics) |
| orchestration | 197 | Orchestration / workflows |
| ui | 176 | UI enhancements (sidebar / panels / components) |
| llm | 159 | Model adaptation |
| acp | 66 | ACP protocol |
| skills | 51 | Skill packs |
| sandbox | 9 | **Only 9 sandbox plugins — security tooling is scarce** (see 15.4) |

### Theme Heat (plugins / total stars / read)

| Theme | Plugins | Total ★ | Read |
|---|---|---|---|
| Design / UI generation | 348 | 94K | **Hottest demand** (agents producing visuals is a hard need) |
| IDE integration | 221 | 89K | High demand |
| Vision / image reading | 132 | 90K | **Text-only models reading images is a hard need** (corroborated by the vision-bridge family in #1153 / #1269 / #1378) |
| Desktop / clients | 140 | 90K | No official desktop shell; the community filled the gap (Windows / macOS / Android) |
| Content creation | 40 | 88K | **High value per project** (few projects but high stars — most valuable for non-programmer scenarios) |
| Workflow / orchestration | 94 | 17K | Medium |
| Memory / persona | 77 | 7.7K | Gaining traction (#1822 memory core / #1448 / #1478 etc., many routes) |
| Code quality / review | 65 | 1.7K | Medium |
| **Finance / trading** | 8 | 28 | **Gap** |
| **Database** | 14 | 137 | **Gap** |
| **Multimodal / audio** | 19 | 26 | **Gap** |
| **Evaluation / testing** | 37 | 117 | **Gap** (contrasts with the official 100%-coverage gate) |

## 15.2 Qualitative Insights (780-post discussion-board observation, cross-validated with data)

### Insight 1: Windows is the #1 pain point (60+ posts)

Data side: Windows compatibility is the highest-frequency topic; discussion side: **Chinese-path truncation (#107 / #151 / #396 / #800 and 15+ posts with the same root cause)**, koffi native crashes (#197 / #293), reserved port ranges (#589), subprocesses without graceful termination (#717), sandbox temp-dir cleanup crashes (#758).

**Cross-validation**: the data side's "poor Windows compatibility" and the discussion side's 60+ posts fully corroborate each other — **this is the most certain ecosystem shortcoming**.

### Insight 2: "Whatever the official side didn't build, the community did"

Data side: 140+ desktop shells, multiple TUIs, 77 memory, 132 vision; discussion side: within two weeks the community filled in CLI / TUI / desktop / memory / vision (#391 / #405 / #386 etc.).

**Cross-validation**: the official side (focused on the core during 0.1.0-rc) and the community (filling niche positions) form a healthy complement — **the strongest signal of ecosystem vitality**.

### Insight 3: Security auditing is unusually active

Data side: **only 9 plugins in the sandbox category** (security tooling is scarce); discussion side: dense security-audit threads (#243 / #250 / #278 / #381 / #454 / #774 / #817 systematic audits; vm escape / approval loops / clickjacking — real findings) plus a security toolchain (vetting / egress-guard / read-confine / check-dsh-profile).

**Cross-validation**: security demand is high (active auditing) but security tools are few (9 sandbox plugins) — **a supply gap**.

### Insight 4: A family of serialization / boundary bugs is breaking out at once

Discussion side: unknown tool "" (#725 / #1405), reasoning serialization elision (#739 / #1850), truncated tool-call contamination (#1519), run_code async callback drops (#1476), corrupted sessions dragging down boot (#1473 / #1497) — **all boundary issues in the llm-deepseek serialization layer / session state machine**.

**Read**: this cluster of bugs concentrated in the rc period = the official side's next iteration battleground, and a goldmine for community patches / fix branches (#1519 / #725 both ship with test-backed fixes).

### Insight 5: Cost transparency is a hidden must-have

Data side: content creation 40 / 88K★; discussion side: dense token-consumption / cache-hit discussions (#735 / #1052 / #1234 / #1374 / #1520), cost tools springing up like mushrooms (dsh-usage / usage-panel / Show Me How Much / balance-meter).

**Cross-validation**: a 97% cache hit rate (measured) is a cost advantage, but it's "invisible" — cost tooling moving from "statistics" to "engineering" (Chapter 14) is a certain direction.

## 15.3 Capability Gaps the Official Side Could Prioritize (double-verified by data + discussion)

| Capability gap | Data basis | Discussion basis | Feasibility |
|---|---|---|---|
| **Multimodal / vision channel** (OCR + vision-service abstraction) | 132 vision / 90K★ | #1378 / #1327 / #2024 raised repeatedly | High (a core implementation is already emerging) |
| **Memory / persona seam** (officially replaceable) | 77 memory / 7.7K★ and gaining traction | #1822 memory-core proposal | High (session already keeps full records) |
| **Desktop / TUI shell protocol** (standardize and absorb) | 140+ fragmented desktop shells | Multiple coexisting clients | High |
| **Evaluation / verification loop** (session → report) | Only 37 eval / 117★ | Official 100%-coverage gate culture | Medium-high |
| **First-class Windows support** (subprocess / sandbox / paths / remote) | Windows is the highest-frequency topic | #107 family / #717 / #755 | Medium-high (large engineering effort) |
| **Plugin registry + compatibility contract** | 1,804 repos need distribution | #1825 plugin-market meta-plugin | Medium |

## 15.4 Advice for Ecosystem Participants

### If you're a plugin developer
1. **Prioritize the gaps**: finance / database / audio / evaluation are blue ocean (few competitors, confirmed demand)
2. **Security tooling is scarce**: only 9 plugins in the sandbox category — security / permission / audit plugins are under-supplied
3. **Vision / memory are hotspots**: but competition is fierce — differentiation (vertical scenarios / enterprise) beats following the crowd

### If you're evaluating options
1. **The differentiation bet**: full session logs + everything-is-a-plugin + sandbox/permissions → **enterprise / evaluation / compliance scenarios** (the advantage zone double-verified by data and discussion)
2. **Risk points**: Windows / remote scenarios are currently the sore spot; teams primarily on Windows need to evaluate carefully
3. **Cost advantage**: 97% cache hit × discount, and the cost-transparency toolchain is already complete (Chapter 14)

### If you're watching from the sidelines
- **The early-ecosystem dividend is still here**: 1,804 plugins, but vertical domains (finance 8 / database 14 / audio 19) are nearly empty — the window is clear
- **First movers, be patient**: the official rc iteration is fast; capability gaps will keep appearing

## 15.5 Methodology Notes for This Report

- The data side (1,804 repos) comes from the community master list, with the scope annotated (README mentions dsh, includes some non-true plugins) — **a directional reference, not precise statistics**
- The qualitative side (780 posts + 195-post responses) comes from this handbook's ongoing observation — every post number is traceable
- The two sides are compared, and conclusions take "what both data and discussion point to", reducing one-sided bias

> The ecosystem is changing; this report will keep updating along with the discussion board (see [feedback pipeline](./research/feedback-pipeline.md)).
