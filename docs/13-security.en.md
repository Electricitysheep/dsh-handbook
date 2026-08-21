[English](./13-security.en.md) | [中文](./13-security.md) · [← Back](../README.md)

# Chapter 13: Security & the Sandbox Model

> **Goal of this chapter:** Understand dsh's security skeleton — what the sandbox governs, how permissions are tiered, how approvals gate dangerous actions — and the real boundary cases the community has found. **This is the chapter that takes you from "it runs" to "safe enough for production."**

## TL;DR (30-second version)

1. **Three layers of defense**: sandbox (where it executes) → permission presets (what it can do) → approval (whether dangerous actions need a human nod) — execution is *not* naked by default
2. **The sandbox only governs file effects**: `read-only` / `workspace-write` / `danger-full-access`; network and process visibility are outside its vocabulary (so cases like `taskkill` killing the host are "outside the vocabulary", not a sandbox breach)
3. **Permissions = two knobs bundled into presets**: `sandbox/mode` + `approval/policy`; two default presets: `workspace-write` (workspace writes + ask) and `danger-full-access` (no sandbox + never)
4. **Approval is fail-closed**: only `allowed-once` grants; ask with no responder = rejected (`unavailable`), never rejects deterministically — the default headless posture
5. **Community audits found real boundaries**: #159 fs-sandbox race, #584 scrubbedParentEnv collateral damage, #381 iframe clickjacking, #817 audit report (vm escape + unauthenticated local RPC)
6. **Enterprise baseline in one line**: default `workspace-write` + ask, keep loopback, install plugins only from trusted sources, keep sensitive directories out of the workspace

<details><summary>Chapter navigation</summary>
- [13.1 Security Design Philosophy: The Three Layers](#131-security-design-philosophy-the-three-layers)
- [13.2 Sandbox Mechanics: FS Boundaries and Tool Sandboxing](#132-sandbox-mechanics-fs-boundaries-and-tool-sandboxing)
- [13.3 Permission Model: Tool Permission Tiers](#133-permission-model-tool-permission-tiers)
- [13.4 Approval Flow: From Request to Grant](#134-approval-flow-from-request-to-grant)
- [13.5 Plugin Security Audit Checklist](#135-plugin-security-audit-checklist)
- [13.6 Known Security Cases from the Community](#136-known-security-cases-from-the-community)
- [13.7 Enterprise Security Baseline](#137-enterprise-security-baseline)
</details>

## 13.1 Security Design Philosophy: The Three Layers

dsh's security skeleton is three layers, each with one job (based on the official `docs/subsystems/*` architecture docs, verified: `sandbox.md` / `permission-presets.md` / `approval.md`; cross-checked against the hands-on measurements in Section 8.5):

| Layer | What it governs | Official packages | One-liner |
|---|---|---|---|
| Sandbox | Where code runs, which files it can touch | `sandbox/sandbox`, `sandbox/sandbox-local`, `sandbox/sandbox-policy` | Isolates the file effects of command execution |
| Permissions | What the agent may do | `interaction/permission-presets` | Bundles sandbox + approval into named presets |
| Approval | Whether dangerous actions need a human confirm | `interaction/user-approval` | The last gate before least privilege |

**Least privilege** is the shared design intent across all three layers: the default preset only grants "workspace writes + ask before critical operations"; any escalation (switching to `danger-full-access`, changing the approval policy) happens explicitly and is written to the session log — the `permission/preset` event is a **log-only record of user intent**, kept out of the model transcript, so you can always look back at "who raised privileges, and when."

**Threat model in one line**: the three layers defend against "untrusted input driving the agent across its boundaries" — prompt injection, malicious plugins, induced high-privilege operations (#381 iframe hijacking is a direct shot at this chain). They do *not* promise to defend against "trusted code going rogue" (a plugin *is* executable code, see 13.5), nor against network/process-level attacks.

> Core takeaway: **dsh's tool execution has isolation and approval layers by default — it is not naked execution.** But it is not a "security operating system" either — the sandbox doesn't block network or processes, and approval can be self-answered by the model (13.6).

## 13.2 Sandbox Mechanics: FS Boundaries and Tool Sandboxing

The official sandbox doc is explicit: **the sandbox only governs file effects (filesystem effects)** — network and process visibility are not part of its vocabulary.

**The three modes** (`SandboxMode`):

| Mode | Allowed file effects | Notes |
|---|---|---|
| `read-only` | Read-only + required sinks (e.g. `/dev/null` on POSIX) | Windows ACL backend has no explicit writable root → reports `partial` |
| `workspace-write` | Workspace root + backend-promised temp areas writable | **Default preset**; root comes from the session's immutable cwd |
| `danger-full-access` | Unrestricted | Spawns the original argv directly, bypassing `ctx.sandbox` |

**Execution details:**

- **Policy is per-call**: `SandboxExecutionPolicy` (mode + workspaceRoot + sessionId) is resolved at each capability call rather than being pinned to a provider — the same provider can serve a `read-only` bash and a subagent that needs a writable state directory
- **Workspace root canonicalization**: first canonicalize per filesystem semantics (`symlink/..` resolved to real directories), then apply lexical normalization — prevents symlink-based boundary escapes
- **Backend matrix**: Linux bwrap/Landlock, macOS Seatbelt, Windows ACL restricted-token; `enforcement: full | partial` — old Landlock ABIs and the Windows ACL Everyone/hard-link boundaries are the current `partial` cases (**when the promise is watered down, consumers must treat it as `partial`**)
- **FS tools share the boundary**: file tools like `write`/`edit` are held to the same `workspace-write` constraint — it's not "file tools pass through, only bash is sandboxed" (#149's recursive workspace deletion happened under `workspace-write`)
- **Writes restricted, reads not**: the current permission model constrains **writes**; content outside the workspace can still be read (#492 raised this when proposing an evaluation isolation mode)

**Tool sandboxing**: `bash`/`pwsh` go through `bash-sandbox` / `pwsh-sandbox` (consuming `ctx.sandbox`) and spawn child processes inside the sandbox. On Windows, the pwsh sandbox has ACL constraints (we hit temp-permission issues in Chapter 8's hands-on testing; #758 also reports that cleaning up the Windows sandbox temp directory can permanently crash it).

**Related family cases**: #159's race is a TOCTOU (the path is swapped between check and use); #278 is a different widening trick — when `/tmp` is the workspace, a restricted child process can use rebinding to widen the `workspace-write` grant. Shared lesson: **choose a trusted location for the boundary root, and never rely on a single path check alone.**

## 13.3 Permission Model: Tool Permission Tiers

The official permission presets bundle **two knobs** — `sandbox/mode` and `approval/policy` — into named presets, surfaced to the client as a single "Permissions" selector. Two default presets:

| Preset | sandbox/mode | approval/policy | Semantics |
|---|---|---|---|
| `workspace-write` | workspace-write | ask | Writable inside workspace, asks before operations (default) |
| `danger-full-access` | danger-full-access | never | No sandbox, no asking |
| `custom` (derived state) | any combination | any | The "non-preset" state after manually turning the knobs; cannot be a switch target |

**Tool permission tiers** (ordered by blast radius; "suggested preset" per tool is derived from the official docs, not tested tool-by-tool — **inferred, pending verification**):

| Tier | Representative tools | Suggested preset | Risk | Notes |
|---|---|---|---|---|
| Read-only probing | `read`/`grep`/`glob` | read-only compatible | Low | Read-only, nothing written; reads not limited to the workspace |
| Workspace writes | `write`/`edit`/`str_replace_editor` | workspace-write | Medium | Write boundary = workspace root + temp areas |
| Command execution | `bash`/`pwsh` | workspace-write (sandboxed) | High | The sandbox doesn't block network or processes |
| Full access | any (switch to danger-full-access) | danger-full-access | Extreme | All gates off |

> The official docs are explicit that the sandbox **only governs files** — so the high risk of the "command execution" tier can't be sandboxed away. It must be backstopped by approval and trust boundaries (13.5 / 13.7).

**Real boundary cases** (details in 13.6): recursive deletion of the entire workspace with zero confirmation under `workspace-write` (#149); `danger-full-access` accidentally deleting an entire home directory (#461, real incident); on Windows, the minimal preset allows out-of-workspace writes with no approval (#523); an agent inside the sandbox can `taskkill` the host (#466 — process visibility is outside the sandbox vocabulary).

## 13.4 Approval Flow: From Request to Grant

The official approval doc: approval answers one question — "can this specific action happen?"

**Fail-closed result set** (`ApprovalOutcome`):

| Outcome | Meaning | Effect on the caller |
|---|---|---|
| `allowed-once` | One-time grant (only for the action asked about) | ✅ proceed |
| `rejected` | Explicit denial | ❌ abort |
| `cancelled` | Request withdrawn (AbortSignal) | ❌ abort |
| `unavailable` | No responder / responder errored | ❌ abort (fail-closed by default) |

**Policy** (`ApprovalPolicy`): `ask` (default — handed to the responder chain; empty chain → `unavailable`); `never` (deterministically rejects everything, dispatches no responders — the strict headless/CI posture).

**Flow**: tool call → `approval/request` waterfall (plugins can intercept/rewrite) → responder (a human in the Web UI, or a one-shot machine decision via the ACP bridge) → every request writes a paired audit pair `approval/asked` + `approval/decided` (same `ApprovalRequestId`).

**Request content** (`ApprovalRequest`): agent (a responder only answers for the agents it owns) + toolName + callId (linked to the already-streamed tool call, so parameters aren't re-rendered) + reason (why the question is being asked) + signal (AbortSignal for withdrawal).

**Three known pitfalls:**

1. **Approval loop**: #250 reproduced "model self-approving danger-full-access" for real (the Web approval channel can be driven by the model itself) — **approval is not a security boundary**, only a human-in-the-loop gate
2. **Concurrent misrouting**: #453 — clicking Allow during concurrent sandbox approvals aborts a *different* call (UI response and callId mismatched)
3. **Reconnect drops pending approvals**: #646 — silent loss of pending approvals on reconnect (resync clears them + replay race); headless approval behavior is undefined (#291)

## 13.5 Plugin Security Audit Checklist

Plugins are dsh's capability boundary ("everything is a plugin", see Chapter 4) — **installing a plugin = installing executable code.** The checklist distilled from community audits (#817 and family):

| # | Check | Community basis | Disposition |
|---|---|---|---|
| 1 | Is the source trustworthy? `dsh plugin add` has no signature/source validation | #587 | Install only from official/well-known sources; read the source before installing |
| 2 | Minimal boot-time permissions? Plugins get write access to the whole config tree at boot | #587 | Beware plugins that "auto-edit your config after install" |
| 3 | Not treating the vm as a security boundary? Workflow/dynamic-plugin vms can escape | #243 #451 #774 #778 | Treat the vm as an isolation engine, not a security layer |
| 4 | Child-process env scrubbed correctly? `scrubbedParentEnv` substring-matching hits legitimate variables | #584 | Check whether variables containing the `KEY` substring (e.g. KEYBOARD/MONKEY) get wrongly scrubbed (**mechanism inferred from the thread title**) |
| 5 | Secret redaction not fail-open? `settings role('secret')` has redaction gaps | #226 | Don't put secrets into prompts; verify the redaction logic |
| 6 | Security hooks not silently disabled? `timeout: 0` fails open | #460 #583 | Set positive hook timeouts; loading failures must surface as errors |
| 7 | Audit trail? `approval/asked`/`decided` pairs are queryable | official approval.md | Critical operations traceable per session |
| 8 | No plaintext session leakage? `.tmp` plaintext session residue after crashes | #674 | Disable crash dumps in sensitive environments / clean up periodically |

## 13.6 Known Security Cases from the Community

All 4 threads below verified to exist via `gh api graphql` (deepseek-ai/deepseek-harness Discussions, 2026-08-14):

| Thread | One-liner | Type | Impact |
|---|---|---|---|
| [#159](https://github.com/deepseek-ai/deepseek-harness/discussions/159) | `fs-sandbox` post-check pathname race can bypass the `workspace-write` file boundary | Sandbox race | TOCTOU: the path is swapped between check and use, enabling out-of-bounds writes |
| [#584](https://github.com/deepseek-ai/deepseek-harness/discussions/584) | `scrubbedParentEnv` substring-matching wrongly scrubs legitimate env vars like KEYBOARD/MONKEY (cherry-pickable fix included) | Child-process env | Legitimate env vars get scrubbed → behavioral anomalies |
| [#381](https://github.com/deepseek-ai/deepseek-harness/discussions/381) | Default localhost web UI can be clickjacked via cross-site iframe, inducing a `Full access` grant and driving high-privilege operations | Frontend clickjacking | Malicious webpages trick users into clicking out high privileges in the dsh UI |
| [#817](https://github.com/deepseek-ai/deepseek-harness/discussions/817) | Security audit report: sandbox/approval boundary bypasses + unauthenticated local RPC (PoC available privately) | Systematic audit | Covers vm escape (family #243 #778), unauthenticated local `/api` (family #451, CVSS 8.8), approval loop (#250) |
| [#2562](https://github.com/deepseek-ai/deepseek-harness/discussions/2562) | On Windows the `workspace-write` fence resolves the literal `/tmp` to `C:\tmp`, silently granting a machine-wide writable directory | Platform resolution | The editor plane can write there while the ACL sandbox denies the shell plane the same path, so two write planes disagree about one path |

**High-value family supplements** (thread numbers from `docs/research/discussion-mining.md` §2.6 in this repo; that report says all 780 threads were programmatically verified):

| Thread | One-liner | Lesson |
|---|---|---|
| #149 | Whole-workspace recursive deletion with zero confirmation under `workspace-write` | Workspace contents also need protection from "self-destruction" |
| #250 | Web approval loop: model self-approving danger-full-access | Approval is not a security boundary |
| #461 | Full Access mode deleted an entire home directory (real incident) | High-privilege preset risk, proven in the wild |
| #587 | Third-party plugins get whole-config-tree write access at boot | Plugin trust = supply-chain security |
| #466 | An agent inside the sandbox can `taskkill` the host | Process visibility is outside the sandbox vocabulary |
| #674 | `.tmp` plaintext session residue after crashes is never cleaned | Privacy risk |

> Disclaimer: these are community reports from the rc.8 era (within 48h of the 2026-08-13 release); some may already be fixed in newer rcs — keep the version context in mind when citing.

### 13.6.1 Runtime failure signatures under the Windows restricted token

The rows above are policy-level boundaries. The Windows ACL backend has another class of problem that only appears at **runtime**, and the errors do not look like permission errors, which makes them expensive to diagnose. All three below were measured on `windows-latest` or on real hardware.

| Symptom | Signature | Notes |
|---|---|---|
| Every HTTPS request fails | `SEC_E_NO_CREDENTIALS` | The restricted token breaks the Windows credential stack. Schannel clients (curl, PowerShell) all fail; OpenSSL clients (node, python) are unaffected. It looks like a network problem |
| MSYS / Git Bash dies during startup | `cygheap_user::init: NtSetInformationToken (TokenDefaultDacl), 0xC0000022` | Cygwin's cygheap init needs a token operation the restricted token denies, so the shell never reaches a prompt. It looks like a PTY problem and is an ACL one |
| Same wall, another machine | `CreateFileMapping Win32 error 5` | A second signature of the same failure, reproduced independently by a third party |

**The actionable conclusion**: a persistent shell under the restricted token needs a shell with no POSIX emulation layer. busybox-w32 `ash` completes a send/read round trip under the same restricted token (measured in `windows-latest` CI). Git Bash requires switching the permission mode to `danger-full-access`.

Source: [#2184](https://github.com/deepseek-ai/deepseek-harness/discussions/2184).

## 13.7 Enterprise Security Baseline

Decision guidance for "going to production / rolling out to a team" (aligned with Chapter 6's style):

| Dimension | Baseline | Basis |
|---|---|---|
| Network exposure | **Keep loopback** (official rejection of `--host 0.0.0.0` is intentional); don't bypass until remote auth matures | #76 #130 #397 |
| Permission preset | Default `workspace-write` + ask; `danger-full-access` only on isolated machines / one-shot tasks | official preset table + #461 |
| Approval policy | Human responder chain required; headless uses `never` (deterministic rejection) with a review gate in front | approval.md + #291 |
| Plugin governance | Whitelisted sources + run the 13.5 checklist before installing; ban bare `dsh plugin add github:` | #587 #656 |
| Workspace boundary | Sensitive directories (home/keys) stay out of the workspace; workspace contents go under version control regularly | #149 #461 |
| Audit | Session logs retained (approval pairs traceable); guard against `.tmp` plaintext residue | approval.md + #674 |
| Upgrade discipline | Re-run the 13.5 checklist on every rc upgrade (sandbox backends / preset table can change) | Chapter 12 rc-integrity stance |

**Decision memo**: local personal dev → default preset is enough; team-shared → `workspace-write` + ask + plugin whitelist; CI/unattended → headless + `never` + code review gate in front; don't run `danger-full-access` long-term anywhere just for convenience.

**Scenario → recommended combination** (decision guidance, derived from the baseline table above):

| Scenario | Recommended combination | Why |
|---|---|---|
| Local personal dev | Default `workspace-write` + ask | Works out of the box; approval isn't annoying |
| Team-shared host | workspace-write + ask + plugin whitelist | Multi-user; plugin supply-chain risk is amplified |
| CI / unattended | headless + `never` + review gate in front | Deterministic rejection; nothing hangs waiting on a human |
| Isolated machine / one-shot task | `danger-full-access` (the machine itself is isolated) | Maximum authorization, but blast radius capped at one box |

---

## Hands-on exercises

1. **Understand**: what file effects does each of the three sandbox modes allow? Why is "network and processes are outside the sandbox vocabulary"?
   > Check yourself: Section 13.2's three-mode table and the "backend matrix" paragraph
2. **Understand**: why is `never` under headless the "strictest" rather than the "loosest"?
   > Check yourself: Section 13.4's "Policy" paragraph (deterministic rejected)
3. **Hands-on**: open `dsh web`, look at the two presets in the Permissions selector; switch to `danger-full-access` and back, and watch the `permission/preset` event in the session log
   > Check yourself: Section 13.3's preset table
4. **Hands-on**: before installing a community plugin, walk it through the 13.5 checklist item by item (source/source code/permissions/audit) and write the conclusion into your notes
   > Check yourself: Section 13.5's checklist table
5. **Think**: why does #250's "model self-approval" prove that approval is not a security boundary? If approval can't stop it, what does an enterprise fall back on?
   > Check yourself: Section 13.6 + the 13.7 baseline table

## FAQ

- **Q: Can the sandbox stop malicious code?** No — don't use it as a security boundary. The sandbox only governs file effects; network (e.g. SSRF) and processes (e.g. #466's `taskkill`) are outside its vocabulary. Defending against malicious code relies on plugin trust (13.5) and network/process-level isolation (containers/VMs/remote sandboxes — the official docs are explicit these are sibling implementations of the capability seam, not `ctx.sandbox` providers).
- **Q: Why is `never` under headless actually safer?** `never` isn't the lax "never ask" mode — it's **deterministic rejection**: any approval request is directly `rejected`, with no responders dispatched — unattended runs never "hang waiting for someone to click Allow." Actions that need to happen rely on an upfront review gate or explicit configuration, not runtime questions.
- **Q: So is `workspace-write` safe?** Relatively safe inside the boundary — but #149 shows "recursively deleting the whole workspace" gets zero confirmation under `workspace-write`. The sandbox stops *boundary crossing*, not *self-destruction inside the boundary*. Put important code under version control.
- **Q: Chapter 12 already mentioned #159 — why cover it again here?** Chapter 12 was a "known-issues quick table" (one-liner + status); this chapter expands the mechanism (how the post-check race happens), the family (#278 /tmp rebind), and the mitigations (don't trust a single path check, keep critical directories out of the workspace).
- **Q: Can these security thread numbers be trusted? Surely someone could have made them up?** The 4 core threads (#159 #584 #381 #817) were each verified to exist via `gh api graphql` (links in the 13.6 table); the family supplements come from `docs/research/discussion-mining.md` in this repo (780 threads fetched with full pagination and programmatically verified).

---

**Next chapter**: [Chapter 14: Caching & Cost Engineering](./14-cost.en.md)
