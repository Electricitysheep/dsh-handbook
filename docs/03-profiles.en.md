[English](./03-profiles.en.md) | [中文](./03-profiles.md) · [← Back](../README.md)

# Chapter 3: Profiles & the Plugin System

> **Goal of this chapter:** Understand dsh's customizable skeleton, how profiles are organized, how plugins are mounted, and what the host/client dual halves are. **This is the watershed moment from "user" to "developer."**

## TL;DR (30-second version)

1. **Profile = a launchable form factor**: a `~/.dsh/profiles/<name>/` directory composed of `package.json` (plugin manifest) + `cordis.patch.yml` (patch layer).
2. **Mounting a plugin takes two steps**: add a dependency in `package.json` + add a mount line in `cordis.patch.yml`, then `pnpm install` and restart.
3. **Host half runs in Node, client half runs in the browser**: one npm package carries both faces via `exports["."]` and `exports["./client"]`.
4. **To change behavior, look for extension points first, don't fork the core**: `agent/request` waterfall, `conversationEvents`, `ctx.slots.inject`, and the `settings` service are the four most common hooks.
5. **Three rc-stage pitfalls**: use the `^0.1.0-rc.8` dependency line, always `await next()`, and client tests need the dsh runtime.

## 3.1 Profile: A Launchable Configuration Stack

dsh uses **profiles** to represent "a launchable form factor." Two are built in; the rest are created via plugins:

| Profile | Purpose | Command |
|---|---|---|
| `web` | Web UI (conversation + sidebar + tools) | `dsh web` |
| `headless` | One-shot CLI tasks | `dsh --profile headless "task"` |
| `tui` (plugin required) | Terminal UI | `dsh --profile tui` (not built in; requires a plugin) |

A profile directory looks like this (`~/.dsh/profiles/<name>/`):

<!-- [style] 目录树代码块统一补 text 语言标签 -->
```text
profiles/web/
├── package.json        # Plugin dependencies + dsh.profile manifest (bundles order)
├── cordis.patch.yml    # Your patch layer: mount/override plugin declarations
├── cordis.yml          # (Generated) Composite configuration
├── pnpm-workspace.yaml
└── node_modules/
```

**Loading order** (from official docs): Built-in bundles (`dsh-base` → `dsh-web-app`) → profile's `cordis.patch.yml` → user-level `~/.dsh/cordis.patch.yml` → `--patch` overlay.

## 3.2 Mounting a Plugin: Two Changes

Here's how to mount the community plugin `dsh-better-sidebar` (a real operation):

**① Add the dependency in `package.json`** (using `link:` to point to local source, or an npm package name):

```json
{
  "dependencies": {
    "dsh-better-sidebar": "link:C:\\path\\to\\DSH-better-sidebar"
  }
}
```

**② Add the mount line in `cordis.patch.yml`**:

```yaml
- insert:
    - id: better-sidebar
      name: dsh-better-sidebar
```

**③ Install and restart**:

```bash
cd ~/.dsh/profiles/web && pnpm install
dsh web   # Takes effect after restart
```

> 💡 Plugins are **isolated per session** by default (e.g. `better-sidebar`'s layout/tabs persist per session). Mounting is profile-level, but state is session-level.

## 3.3 Host Half & Client Half: One Package, Two Faces

A plugin can carry two runtime halves simultaneously:

| Half | Runs In | Responsibility | Example |
|---|---|---|---|
| **Host half** | Node process | Tools, services, events, filesystem, processes | `apply(ctx)` registers tools/services |
| **Client half** | Browser (web profile) | UI, interaction, DOM | `dsh.client` declaration in `package.json` + `src/client/` |

How to declare the client half in `package.json`:

```json
{
  "dsh": {
    "client": {
      "inject": ["@deepseek-ai/dsh-client-runtime", "@deepseek-ai/dsh-client-locale"],
      "platform": "web"
    }
  },
  "exports": {
    ".": { "types": "./lib/types/index.d.ts", "default": "./lib/index.js" },
    "./client": { "types": "./lib/types/client/index.d.ts", "default": "./lib/client.js" }
  }
}
```

- Host half: `exports["."]` → `apply(ctx)` (the cordis plugin body)
- Client half: `exports["./client"]` → `apply(ctx)` on the browser side
- `inject`: Declares required services (cordis dependency injection)

## 3.4 Extension Points: Look for Hooks First, Don't Fork the Core

Official principle (stated in CONTRIBUTING/AGENTS.md): **"Plugins, not loop changes: new behavior goes on documented extension points."** The most common mistake newcomers make is modifying the core loop. The correct approach is to use extension points.

Confirmed commonly-used extension points (each explored hands-on in later chapters):

| Extension Point | Location | Purpose |
|---|---|---|
| `agent/request` waterfall | `agent-loop` | **Modify config before every model request** (provider/model/reasoningEffort/tools). This is what the speed-up plugin example uses. |
| `agent/request-error` | `agent-loop` | Intervene on request failure (the official compaction plugin uses this for context-window overflow recovery) |
| `conversationEvents.register` | Client runtime | Subscribe to / inject conversation events (tool/call, turn/start, etc.) |
| `ctx.slots.inject` | Client UI slots | Inject UI into interface slots (e.g. turnTail to display artifact file lines) |
| `settings` service | dsh-settings | Register user-configurable namespaces (settings page auto-renders them) |
| `ctx.provide` / `ctx.get` | cordis | Provide services across plugins |

## 3.5 Common Pitfalls (Battle-Tested)

| Pitfall | Symptom | Fix |
|---|---|---|
| **rc.1 broken dependency chain** | `pnpm install` reports `@deepseek-ai/dsh-type-meta@0.0.1-rc.1` 404 | Several packages from the rc.1 era were never published; upgrade to the `^0.1.0-rc.8` line |
| Plugin missing `main` | `dsh: No "exports" main defined` | The host plugin's `package.json` must expose a `.` entry (`"main": "src/index.ts"` can be loaded directly by tsx) |
| Event handler forgets `await next()` | Request loses provider/model and errors out | `next()` in `agent/request` returns a **Promise**; you must await it before spreading |
| Type error: `'agent/request' is not assignable to keyof Events` | npm types don't re-export the official type augmentations | Use a relaxed signature (`ctx.on as unknown as ...`) at the boundary |
| Client package depends on `window.__ModuleLoader__` | jsdom can't run client tests directly | Component-level tests need the dsh web runtime (run in official CI) |

---

## Hands-on exercises

1. **Locate your profile**: find the `web` profile directory on your machine. Read `package.json` and `cordis.patch.yml`. Identify which plugins are currently mounted.
2. **Mount a plugin**: follow Section 3.2 to mount `dsh-better-sidebar` (or any community plugin). Verify it appears after restart.
3. **Trace the host/client split**: pick a plugin that has both halves. Find the `dsh.client` declaration in its `package.json` and the `apply(ctx)` function in its entry file.
4. **Find an extension point**: read the `agent/request` waterfall description above. In the dsh source, search for where this waterfall is called. What other waterfalls or hooks can you spot?
5. **Pitfall reproduction**: deliberately forget to `await next()` in a test plugin. Observe the error. Then fix it and confirm the config flows through.
6. **Think**: why does dsh separate "profile" from "plugin"? What would break if plugins were global instead of profile-scoped?

## FAQ

- **Q: What's the difference between a profile and a plugin?** A profile is a *launchable form factor* (a directory with config + patch). A plugin is a *capability unit* mounted into a profile. You can think of a profile as a "container" and plugins as "modules inside it."
- **Q: Do I need to create a new profile for every project?** No. Most users stick with `web` for interactive work and `headless` for scripting. Custom profiles are for advanced use cases (TUI, desktop, bots).
- **Q: Why does `pnpm install` fail with 404 errors?** The rc.1 dependency chain is broken. Use the `^0.1.0-rc.8` line in `package.json` (see Section 3.5).
- **Q: Can I use a plugin without modifying `cordis.patch.yml`?** No. Adding the dependency alone doesn't activate the plugin. You must declare it in the patch layer for Cordis to load it.
- **Q: Why can't I run client-half tests with jsdom?** The client half depends on `window.__ModuleLoader__`, which is bootstrapped by the dsh web runtime. Component tests need the official CI environment.

---

**Next chapter**: [Chapter 4: Plugin Development, Hands-On](./04-plugin-dev.en.md) (planned) — Write your first host plugin from scratch.
