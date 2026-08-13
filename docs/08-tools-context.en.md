[English](./08-tools-context.en.md) | [中文](./08-tools-context.md) · [← Back](../README.md)

# Chapter 8: Tools & Context System

> **Goal of this chapter:** Understand dsh's "capability engine" — which tools the model can call, how context is fed to the model, and how long conversations are handled. **This is the key chapter for going from "it runs" to "I understand how it runs."**

## TL;DR (30-second version)

1. **60+ official capability packages**: tools (fs/shell/web/skill/todo), context (context/compaction), session, subagent, MCP, workflow, safety, model, UI. Everything is a plugin.
2. **Built-in tool names are short verbs**: `read`/`write`/`grep`/`glob`/`edit`/`bash`/`todo`/`skill`. When writing prompts, just say "read the file" or "search" and it works.
3. **Tool returns carry `locations` → artifact tracking**: the model can see which files it changed, and the UI lets you open them directly (artifact chips at the end of the conversation).
4. **Context = system prompt + skill catalog + conversation history + tool results**: layered injection, with tool schemas carried in every request.
5. **Long conversations are auto-compressed (compaction)**: detect overflow → prune history → optional summarization → fallback to overflow agent. Important info should be written into the prompt manually.

## 8.1 Official Capability Map (60+ Packages at a Glance)

All of dsh's capabilities are provided as packages (`packages/<group>/<name>`). The ones newcomers need to know first:

| Capability Domain | Official Packages | Purpose |
|---|---|---|
| **Tools** | `fs/tool-fs`, `fs/tool-fs-search`, `fs/tool-str-replace-editor`, `shell/tool-bash`, `web`, `skill`, `todo` | Callable tools for files, terminal, web, skills, todos, etc. |
| **Context** | `context/*`, `compaction/*` | Request context assembly, long-conversation compression |
| **Session** | `session/*` | Persistence, titles, telemetry |
| **Subagent** | `subagent/*` | Delegate sub-tasks |
| **MCP** | `mcp/*` | MCP client (external tool servers) |
| **Workflow** | `workflow/*` | Multi-step workflow orchestration |
| **Safety** | `sandbox/*`, `guard/*`, `interaction/*` | Sandboxing, loop hygiene, permissions/approvals |
| **Model (LLM)** | `llm/*`, `llm-deepseek`, `llm-retry` | Model integration, retries |
| **Skill** | `skill/*` | Skill provider registry |
| **Client (UI)** | `client/*` (ui-conversation, ui-tool, …) | Web UI components |

> Full list: see `packages/AGENTS.md` in the official repository.

## 8.2 Built-In Tools (Observed in Practice)

The actual tool names the model can call are **short verbs** (observed from dsh web sessions and agent/request logs):

| Tool Name | Purpose | Notes |
|---|---|---|
| `read` | Read files | fs capability |
| `write` | Write files | fs capability |
| `grep` | Content search | fs-search |
| `glob` | File pattern matching | fs-search |
| `edit` / `str_replace_editor` | Precise editing | Tool results include `locations` (used for artifact tracking) |
| `bash` / `pwsh` | Execute commands | Sandbox isolation |
| `todo` | Todo management | Long-task planning |
| `skill` | Skill invocation | Injected via skill-catalog |

**Tool results and artifact tracking** (important concept): Tool return values carry `locations` (file paths). dsh uses these to build "artifact file lines" — the artifact chips at the end of a conversation come from here. **The model can see which files were changed, and the UI lets you open them directly.**

## 8.3 How Context Is Fed to the Model

A single model request's context = system prompt + skill catalog + conversation history + tool results. This is visible in session logs:

```
Context injection @deepseek-ai/dsh-system-prompt   ← Official system prompt
Context injection skill-catalog                    ← Skill catalog
```

dsh's context mechanism:
- **Layered system prompts:** Official plugins register prompt sections via `systemPrompt.section()` (e.g. ui-deliverables registers "artifact file reference" guidance)
- **Skill catalog injection:** The list of available skills enters the context; the model calls them as needed
- **Tool schemas:** Every request carries tool definitions

## 8.4 Long Conversations: Compaction

Long conversations blow up the context window. dsh's `compaction` plugins (e.g. `compaction-basic`) handle:
- Detecting context overflow (`CONTEXT_WINDOW_EXCEEDED` via `agent/request-error`)
- Compressing history (model-agnostic pruning + optional summarization)
- Routing to an "overflow agent" on failure

> For newcomers: **Just know that "long conversations are auto-compressed."** The details are an advanced topic. In production, note that compression loses detail — important context should be written into the prompt manually.

## 8.5 Permissions & Security Model (Awareness Level)

- **Access modes:** The UI shows modes like "Workspace Write" (permission presets)
- **Interactive approvals:** `interaction/*` provides permission/approval capabilities (dangerous operations can require confirmation)
- **Sandboxing:** `sandbox/*` isolates command execution (e.g. the pwsh sandbox has ACL constraints — temp directory permission issues have been observed in practice)
- **Tool timeouts:** `guard/*` provides loop hygiene and tool timeouts

> Deep security configuration is beyond the scope of this handbook. The key takeaway: **dsh's tool execution has isolation and approval layers by default.** It's not bare execution.

## 8.6 Three Things Newcomers Should Remember Most

1. **Tool names are short verbs** (read/write/grep/glob/edit/bash) — when writing prompts or plugins, just say "read the file" or "search" and it works
2. **Tool returns include `locations` → artifact tracking** — files the model changed appear in the conversation's artifact area
3. **Long conversations are auto-compressed** — no need to manually clear history (but important info should go into the prompt)

---

**Next chapter**: [Chapter 9: MCP, Subagents & Workflows](./09-mcp-subagent-workflow.en.md)
