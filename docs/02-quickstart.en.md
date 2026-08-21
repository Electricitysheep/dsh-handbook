# Chapter 2: 5-Minute Quickstart

> Goal: **follow along and get it running.** Every command shows its expected output and common errors. Open a terminal and go.

## 2.1 Prerequisites (30-second check)

| Need | Check | Pass |
|---|---|---|
| Node.js ≥ 22 | `node --version` | `v22.x`+ (24 recommended) |
| npm | `npm --version` | prints a version |
| Network | npm registry reachable | can install packages |
| (optional) DeepSeek API key | https://platform.deepseek.com | for real conversations |

> dsh starts without a key (UI opens), but conversations need one. Examples assume it's configured.

## 2.2 Install (two ways)

**One-liner (recommended for new users)**

```bash
npx -y @deepseek-ai/dsh --version
```

First run downloads dsh (large package, 40+ plugin modules, 1-3 min). You're good when you see:

<!-- [style] 输出/目录类代码块统一补 text 语言标签 -->
```text
0.1.0-rc.7
```

> ⚠️ **Version vs npm dist-tag skew** (verified 2026-08-21): `0.1.0-rc.8` shipped on 2026-08-19, but npm's `latest` tag still points at `0.1.0-rc.7` (`next` points at `0.1.1-rc.1`). So the command above actually installs **rc.7, not rc.8**. Pin the version explicitly to get rc.8:
>
> ```bash
> npx -y @deepseek-ai/dsh@0.1.0-rc.8 --version
> npm install -g @deepseek-ai/dsh@0.1.0-rc.8
> ```
>
> Check what the tags resolve to at any time: `npm view @deepseek-ai/dsh dist-tags`

**Global install (recommended for frequent use)**

```bash
npm install -g @deepseek-ai/dsh
dsh --version
```

## 2.3 Mode 1: Web UI (`dsh web`)

### Start

```bash
dsh web
```

Expected output:

```text
dsh web: http://127.0.0.1:3080
```

Open http://127.0.0.1:3080 in your browser.

### UI map (see screenshot)

| Area | What's there |
|---|---|
| Left | session list / workspace switch / new session |
| Center | chat: input box, model selector (`DeepSeek V4 Flash`), reasoning level (`High`) |
| Right/bottom | plugin sidebar (empty by default; appears after installing community plugins) |
| Top-right | Session log / Trajectory |

### First conversation

1. Click **New session**
2. Type: `Hello, introduce yourself in one sentence`
3. Press Enter

Expected reply (roughly):

> Hello! I'm a DeepSeek-powered AI coding assistant... 

### Models & reasoning effort

Click the model selector next to the input:

| Model | Positioning |
|---|---|
| `deepseek-v4-flash` (default) | value: fast, cheap, enough for daily work |
| `deepseek-v4-pro` | flagship: stronger, more expensive/slower |

**Reasoning effort** (three steps since 2026-08-13):

| Level | Speed | Quality | Suggested use |
|---|---|---|---|
| `low` | fastest | adequate | simple/deterministic rounds, batch, cheap chain steps |
| `high` (default) | medium | good | daily agent tasks |
| `max` | slowest | best | hard reasoning, long planning |

> 💡 **Key performance insight**: the model re-thinks **before every tool call**. Measured: a "create file" task spends ~90% of wall-clock in thinking; a 50-step tool chain accumulates minutes. **Lowering the reasoning effort is the highest-leverage speedup** (Ch.6 + the example speed-up plugin).

## 2.4 Mode 2: Headless (one-shot tasks, scripts/CI)

```bash
dsh --profile headless "Hello, introduce yourself in one sentence"
```

Expected output (prints result, process exits):

```text
Hello! I'm a DeepSeek-powered AI coding assistant...
```

**Headless value**:
- **Automation**: CI, servers, cron
- **Script-friendly**: non-zero exit = failure; output pipes
- **Isolation**: fresh session per call (`--resume` restores; see `dsh --profile headless --help`)

**Example**: daily digest script:

```bash
dsh --profile headless "Read today's git log in the workspace and write a Chinese daily summary" > daily-report.md
echo "exit=$?"
```

## 2.5 Your first plugin: a Git panel for web

dsh's sidebar is empty by default — install community plugin `dsh-better-sidebar` to feel "everything is a plugin" (mechanics in Ch.3; here just get it running):

```bash
# 1. locate your web profile
#    Windows: %USERPROFILE%\.dsh\profiles\web
#    macOS/Linux: ~/.dsh/profiles/web

# 2. add one line to package.json dependencies
#    "dsh-better-sidebar": "link:C:\\path\\to\\DSH-better-sidebar"

# 3. add to cordis.patch.yml
#    - insert:
#        - id: better-sidebar
#          name: dsh-better-sidebar

# 4. install & restart
cd ~/.dsh/profiles/web && pnpm install
dsh web
```

After restart, the sidebar gains file manager / terminal / **Git panel** / browser tabs.

> The panel's fetch/pull/push buttons are a community PR (Ch.5) — **this is how the plugin ecosystem works.**

## 2.6 Config & paths

First run creates:

```text
~/.dsh/
├── settings.yaml          # global settings (model, reasoning effort)
├── profiles/              # profile dirs
│   └── web/
│       ├── package.json      # plugin deps + manifest
│       └── cordis.patch.yml  # your patch layer
├── sessions/              # session data
└── storages/              # persistence
```

`settings.yaml` example:

```yaml
agent-default-model:
  model: deepseek-v4-flash
  reasoningEffort: high
```

## 2.7 Command cheatsheet

| Command | Purpose |
|---|---|
| `dsh web` | start Web UI (alias `dsh --profile web`) |
| `dsh --profile headless "task"` | one-shot task, print result, exit |
| `dsh plugin --profile <name> add <pkg>` | add a plugin to a profile |
| `dsh --dump-config` | print composed config tree |
| `dsh --profile tui` | TUI mode (plugin-provided; not built-in) |
| `dsh --version` | version |

## 2.8 Troubleshooting

| Symptom | Cause & fix |
|---|---|
| `dsh: profile "tui" does not exist` | tui needs a plugin (`dsh plugin --profile tui add <pkg>`) |
| `npx` very slow | first-run package size; `npm i -g` helps |
| browser can't reach 3080 | port busy: `netstat -ano \| findstr 3080` → kill PID |
| model not responding | check `~/.dsh/settings.yaml` + API key |
| plugin install 404 | **rc.1 dependency break**: use `^0.1.0-rc.6` line (Ch.3 pitfall #1) |
| behavior changed after upgrade | rc-stage breaking changes; check changelog |

---

**Next**: [Chapter 3: Profiles & the Plugin System](./03-profiles.md)
