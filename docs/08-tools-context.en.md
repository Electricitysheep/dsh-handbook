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

## Hands-on exercises

1. **Tool inventory**: open a `dsh web` session. Ask the model: "List all the tools you can call." Compare the list with Section 8.2. Are there any surprises?
2. **Artifact tracking**: give dsh a task that modifies multiple files (e.g. "Create a Python project with a main script, a test file, and a README"). After the task, check the artifact chips at the end of the conversation. Can you open each file?
3. **Context inspection**: open the session log (top-right in `dsh web`). Look for "Context injection" lines. What sections are injected? How much of the context is system prompt vs conversation history?
4. **Long conversation test**: have a 20+ turn conversation with dsh. At what point does compaction kick in? Check the logs for compaction events. Does the model still remember early context?
5. **Permission modes**: in the Web UI, switch between different access modes (e.g. "Workspace Write"). What changes? What operations are restricted?
6. **Think**: why are tool names short verbs instead of descriptive names? How does this affect the model's ability to use them correctly?

## FAQ

- **Q: What's the difference between `edit` and `write`?** `write` creates or overwrites a file. `edit` (or `str_replace_editor`) makes precise replacements within a file. Use `edit` for small changes, `write` for new files or major rewrites.
- **Q: Why does the model sometimes use `bash` instead of `read`?** The model chooses tools based on the task. If it needs to run a command (e.g. `cat file.txt`), it uses `bash`. If it just needs to read the file content, it uses `read`. Both work, but `read` is more efficient.
- **Q: What happens when the context window fills up?** dsh's compaction plugins detect the overflow, prune the history, and optionally summarize. You don't need to manually clear the conversation, but important context may be lost. For critical info, write it into the prompt.
- **Q: Can I add custom tools?** Yes, via a host plugin. Use the `tools` capability to register new tools. The model will see them in the tool schema and can call them.
- **Q: What's a "skill" and how is it different from a tool?** A skill is a higher-level capability injected via the skill catalog. The model calls skills via the `skill` tool. Skills are typically more complex than tools (e.g. "review this code" vs "read this file").
- **Q: Is sandboxing enabled by default?** Yes. Tool execution has isolation and approval layers. Dangerous operations (e.g. `bash` commands) may require confirmation. You can configure the sandbox via the `sandbox/*` and `interaction/*` packages.

---

**Next chapter**: [Chapter 9: MCP, Subagents & Workflows](./09-mcp-subagent-workflow.en.md)
