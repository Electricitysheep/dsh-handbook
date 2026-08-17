[English](./08-tools-context.en.md) | [中文](./08-tools-context.md) · [← Back](../README.md)

# Chapter 8: Tools & Context System

> **Goal of this chapter:** Understand dsh's "capability engine" — which tools the model can call, how context is fed to the model, and how long conversations are handled. **This is the key chapter for going from "it runs" to "I understand how it runs."**

## TL;DR (30-second version)

1. **60+ official capability packages**: tools (fs/shell/web/skill/todo), context (context/compaction), session, subagent, MCP, workflow, safety, model, UI. Everything is a plugin.
2. **Built-in tool names are short verbs**: `read`/`write`/`grep`/`glob`/`edit`/`bash`/`todo`/`skill`. When writing prompts, just say "read the file" or "search" and it works.
3. **Tool returns carry `locations` → artifact tracking**: the model can see which files it changed, and the UI lets you open them directly (artifact chips at the end of the conversation).
4. **Context = system prompt + skill catalog + conversation history + tool results**: layered injection, with tool schemas carried in every request.
5. **Long conversations are auto-compressed (compaction)**: detect overflow → prune history → optional summarization → fallback to overflow agent. Important info should be written into the prompt manually.
6. **Plugin behavior can be tested without a provider key**: use the built-in headless smoke test or mock LLM, and add a community auditor only when waterfall-level evidence is required.

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

<!-- [style] 示意图代码块统一补 text 语言标签 -->
```text
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

## 8.7 Testing Plugin Runtime Behavior Without an API Key

> This method originated in official Discussion [#462](https://github.com/deepseek-ai/deepseek-harness/discussions/462). The steps below distinguish **capabilities built into the official repository** from those supplied by a **community audit plugin**.

Static checks only prove that a plugin loads. They do not prove that it preserves behavior in a real agent loop. Waterfall listeners must `await next()` and forward its result; otherwise, a plugin can silently swallow downstream behavior. The [contract tests in Chapter 4](./04-plugin-dev.en.md#45-testing) cover that boundary first, while this section exercises the assembled runtime.

### 8.7.1 Built-in keyless smoke test

The official source tree contains an in-process mock adapter and an assembled headless smoke test. It makes no provider request:

```bash
# From the root of a complete deepseek-harness source checkout
pnpm install --frozen-lockfile
pnpm run build:lib:host

DSH_EXAMPLE_MODE=lib pnpm exec vitest run \
  --config vitest.e2e.config.ts \
  examples/headless-agent/tests/keyless-smoke.e2e.ts
```

The test passes when it exits with code 0. These commands were run successfully against official commit `47f9438` (1 file / 1 test). This lane validates the official headless composition; it does not automatically load a third-party plugin. Add the plugin to the test composition through a patch, or use the HTTP mock path below.

### 8.7.2 HTTP mock with the real DeepSeek adapter

`mock:llm` is the official repository's OpenAI-compatible HTTP/SSE test server. This script emits a `bash` tool call for the first request and a normal text response for the second, exercising the real adapter, agent loop, and tool pipeline.

Terminal 1:

```bash
pnpm run mock:llm -- \
  --port 8000 \
  --api-key mock-key \
  --sequence tool_call_success,success \
  --repeat-last \
  --tool-name bash \
  --tool-arguments '{"command":"ls","description":"list files"}'
```

Terminal 2:

```bash
DEEPSEEK_BASE_URL=http://127.0.0.1:8000/v1 \
DEEPSEEK_API_KEY=mock-key \
DSH_TELEMETRY_DISABLED=1 \
pnpm dsh --profile headless "run the bash tool once and report"
```

Install a local plugin into the headless profile first:

```bash
pnpm dsh plugin --profile headless add /absolute/path/to/your-plugin
```

For CI, prefer `--patch ./plugin-test.cordis.yml` to inject the test plugin without mutating a persistent profile. A passing run should satisfy all of these conditions:

- the headless process exits with code 0 and stdout contains the final assistant text;
- the session JSONL contains `tool/call` and `tool/result`;
- `turn/end.reason.kind` is `completed`;
- plugin-specific logs or observable artifacts match expectations.

### 8.7.3 Full waterfall auditing is a community extension

`DSH_EVENT_AUDIT_DUMP`, the audit snapshot's `byMode` field, and the “74 events / 12 waterfalls” result are **not built into the official repository**. They come from the community plugin `@qing3a/dsh-event-auditor` used in Discussion #462. This variable is meaningful only after installing that plugin:

```bash
DSH_EVENT_AUDIT_DUMP=/tmp/audit.json \
pnpm dsh --profile headless "run the bash tool once and report"
```

Do not assert one fixed event count across releases. Stable assertions are that the waterfalls relevant to the plugin occur, default behavior after `next()` still occurs, the tool returns a result, and the turn completes.

### 8.7.4 Common failures

- **Argument separator:** write `pnpm run mock:llm --` with exactly one `--`; omitting or duplicating it can shift argument parsing.
- **Incomplete source checkout:** use a full clone. Missing `vendor/` prevents `@deepseek-ai/cordis` from resolving.
- **Build scope:** headless requires `build:lib:host`; add client/Web builds only when the plugin under test depends on those artifacts.
- **Service injection:** headless does not provide `webServer`; making it a required injection leaves the plugin waiting forever.
- **Version drift:** trust the target checkout's CLI `--help`, `lib/types/`, and event catalog instead of fixed numbers copied from another rc/master revision.

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
