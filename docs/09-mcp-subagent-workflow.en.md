[English](./09-mcp-subagent-workflow.en.md) | [中文](./09-mcp-subagent-workflow.md) · [← Back](../README.md)

# Chapter 9: MCP, Subagents & Workflows

> **Goal of this chapter:** Understand dsh's three extension capabilities — MCP (connecting external tools), subagents (parallel tasks), and workflows (multi-step orchestration). **These are the switches that upgrade dsh from a "single agent" to an "agent system."**

> ⚠️ This chapter is based on official architecture docs (`packages/AGENTS.md`) and package structure. Some feature examples are marked "pending live testing" — rc versions iterate quickly, so defer to the official changelog for exact usage.

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

```
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
- Plugin development / speed-up tools (e.g. `dsh-tool-turbo`, the companion to this handbook)

The ecosystem is growing fast. **Now is a great time to start building.**

---

**Appendix A**: [Glossary & Command Quick Reference](./appendix-glossary.md)
