[English](./09-mcp-subagent-workflow.en.md) | [中文](./09-mcp-subagent-workflow.md) · [← Back](../README.md)

# Chapter 9: MCP, Subagents & Workflows

> **Goal of this chapter:** Understand dsh's three extension capabilities — MCP (connecting external tools), subagents (parallel tasks), and workflows (multi-step orchestration). **These are the switches that upgrade dsh from a "single agent" to an "agent system."**

> ⚠️ This chapter is based on official architecture docs (`packages/AGENTS.md`) and package structure. Some feature examples are marked "pending live testing" — rc versions iterate quickly, so defer to the official changelog for exact usage.

## TL;DR (30-second version)

1. **MCP = plug external tools into the agent**: connect to databases, browsers, internal systems via the MCP protocol. Get the built-in tools working first, then add MCP when you have a clear gap.
2. **Subagents = work in parallel**: delegate tasks to sub-agents for parallel execution (large-repo research, long-task decomposition, independent verification). Master single-agent workflow first.
3. **Workflows = deterministic process orchestration**: unlike "multi-turn conversation" (model freestyles), workflows define steps as a flow executed in order or by condition. Suited for fetch → clean → report → validate.
4. **Combined = agent system**: parent agent plans → subagents research in parallel → tool chain + MCP → workflow aggregates → artifacts.
5. **Beginner path, four stages**: single agent + built-in tools → + MCP → + subagents → + workflows. Stack gradually, don't skip levels.

## 9.1 MCP: Connecting to the External Tool Ecosystem

**MCP (Model Context Protocol)** is an open protocol for "plugging external tools into an agent." dsh provides an `mcp` client package (`@deepseek-ai/dsh-mcp-client`).

**What it does:** Connect to any MCP server via MCP (databases, browsers, charts, internal company systems, etc.). For example, the community's `dsh-plugin-cost-tracker` (token tracking) is an MCP/plugin hybrid.

**Positioning for newcomers:** MCP is an "ecosystem extension." Only reach for it once you have a clear tool gap inside dsh. Get the built-in tools working first, then add MCP.

## 9.2 Subagents: Working in Parallel

**What they are:** Delegate tasks to sub-agents for parallel execution (`packages/subagent/*`).

**Typical scenarios:**
- Multi-module research in a large repo (one subagent per module)
- Long-task decomposition (parent agent plans, subagents execute)
- Independent verification (subagents cross-check each other)

**For newcomers:** Subagents are "advanced weaponry." Master the single-agent workflow first, understand task decomposition, then move to subagents. A common anti-pattern is "spawning a subagent for everything," which just adds coordination overhead.

## 9.3 Workflows: Multi-Step Orchestration

**What they are:** `packages/workflow/*` provides multi-step workflow orchestration (worker-thread provider + tool Consumer).

**How they differ from "multi-turn conversation":** A normal conversation is "the model freestyles." A workflow is "steps are defined as a flow, executed in order or by condition." This suits **deterministic processes** (e.g. fetch data → clean → generate report → validate).

**Official examples** (`packages/examples/`): Runnable cordis.yml workflow samples are available.

## 9.4 Putting It Together: What an "Agent System" Looks Like

<!-- [style] 流程图代码块统一补 text 语言标签 -->
```text
Your prompt (goal)
  ↓
Parent Agent (planning)
  ├── Subagent A: Research module A (parallel)
  ├── Subagent B: Research module B (parallel)
  └── Tool chain: read/grep/bash + MCP (database)
  ↓
Workflow (e.g. validate → aggregate → output report)
  ↓
Artifacts (openable / trackable)
```

**Suggested beginner path:**
1. **Stage 1:** Single agent + built-in tools (Chapters 2–5)
2. **Stage 2:** + MCP (connect external tools)
3. **Stage 3:** + Subagents (parallelism)
4. **Stage 4:** + Workflows (deterministic flows)

## 9.5 Community Ecosystem Examples (Snapshot as of 2026-08-13)

Community projects already appearing in the official Discussions:
- `dsh-plugin-cost-tracker` — real-time token cost tracking (plugin/MCP hybrid)
- Plugin development / speed-up tools (e.g. the example speed-up plugin in Chapter 4 of this handbook)

The ecosystem is growing fast. **Now is a great time to start building.**

---

## Hands-on exercises

1. **MCP exploration**: search GitHub for MCP servers (e.g. database, browser, chart). Pick one. Read its documentation. What would it add to dsh?
2. **Subagent design**: think of a task that could benefit from parallelism (e.g. "research 5 modules in a large repo"). How would you decompose it into subagent tasks? What would the parent agent do?
3. **Workflow sketch**: design a deterministic workflow for a real task (e.g. "daily data pipeline: fetch → clean → analyze → report"). What are the steps? What conditions or branches exist?
4. **Agent system diagram**: draw a diagram of an "agent system" that combines all four capabilities (single agent + MCP + subagents + workflow). What does each component do?
5. **Beginner path check**: which stage are you at? If you're at stage 1 (single agent), master it first. If you're at stage 2 (MCP), what external tool are you connecting? What gap does it fill?
6. **Think**: why does the guide say "don't skip levels"? What goes wrong if you spawn subagents before mastering single-agent workflow?

## FAQ

- **Q: When should I add MCP?** Only when you have a clear tool gap. If dsh's built-in tools (read/write/bash/grep) can't do what you need (e.g. query a database, interact with a browser), then MCP is the answer.
- **Q: Do subagents speed up every task?** No. Subagents add coordination overhead. They're useful for parallelizable tasks (research, decomposition, verification). For sequential tasks, they just add complexity.
- **Q: What's the difference between a workflow and a multi-turn conversation?** A conversation is "the model freestyles." A workflow is "steps are defined as a flow." Workflows are deterministic; conversations are adaptive. Use workflows for repeatable processes.
- **Q: Can I combine subagents and workflows?** Yes. A workflow can spawn subagents for parallel steps. This is the "agent system" pattern: parent plans, subagents execute, workflow orchestrates.
- **Q: Are subagents and workflows stable in rc?** They're part of the official architecture, but rc versions iterate quickly. Check the changelog and `packages/AGENTS.md` for the latest status.
- **Q: Where do I find MCP servers?** Search GitHub for "MCP server" or check the official MCP documentation. The ecosystem is growing fast.

---

**Appendix A**: [Glossary & Command Quick Reference](./appendix-glossary.md)
