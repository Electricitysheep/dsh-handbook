[English](./07-ecosystem.en.md) | [中文](./07-ecosystem.md) · [← Back](../README.md)

# Chapter 7: Ecosystem & Resources

> **Goal of this chapter:** Give you a map for "joining the dsh ecosystem" — official entry points, the state of the community, and how to participate.

## 7.1 Official Entry Points

| Resource | URL | Purpose |
|---|---|---|
| Official repository | https://github.com/deepseek-ai/deepseek-harness | Source code, architecture docs, issues |
| API documentation | https://api-docs.deepseek.com | Models, pricing, API guides |
| Discord | Link in official README | Community discussion |
| Discussions | Official repo Discussions | Proposals / help requests (currently the recommended contribution entry point) |

**Note:** The official CONTRIBUTING guide states "external PRs are not accepted at this time" (as of 2026-08-13). However, the following are encouraged:
- Submit suggestions in Discussions (the team evaluates them)
- **Build dsh-plugin ecosystem projects** (an officially endorsed contribution path)
- Write tutorials and blog posts

## 7.2 Plugin Ecosystem (Snapshot as of 2026-08-13)

| Project | Focus | Status |
|---|---|---|
| `DSH-better-sidebar` | File management / terminal / Git / browser sidebar | Most complete community plugin |
| `dsh-tool-turbo` | Tool-call speed-up (automatic reasoning_effort adjustment) | Community speed-up plugin |
| `dsh-handbook` (this handbook) | Beginner tutorial | Ecosystem documentation |

**Discovering plugins:** Search GitHub for `topic:dsh-plugin`.
**Publishing a plugin:** Add the `dsh-plugin` topic to your repo + publish on npm.

## 7.3 How to Join the Ecosystem (Beginner Path)

1. **Use it:** `dsh web` + install two community plugins, integrate into your daily workflow
2. **Small improvements:** Submit PRs to community plugins (read the three cases in Chapter 5 for a complete PR paradigm)
3. **Publish a plugin:** Start from the minimal host plugin in Chapter 4, tag it with `dsh-plugin`
4. **Write content:** Tutorials / reviews / pitfall guides (officially encouraged); cross-reference this handbook

## 7.4 Recommended Reading Path

| Goal | Path |
|---|---|
| Quick start | Chapter 2 → install better-sidebar → use daily |
| Plugin development | Chapter 3 → Chapter 4 → follow the Chapter 5 cases |
| Performance tuning | Chapter 6 → tool-turbo source code |
| Deep customization | Official AGENTS.md (architecture) → docs/architecture.md → packages/ source code |

## Closing Words

dsh was open-sourced on 2026-08-13. **Every day of the ecosystem is "early days."** This handbook will keep updating as dsh evolves. If a command in some chapter stops working, it's most likely due to rc version iteration. Always defer to the official changelog.

Go claim your spot in this brand-new ecosystem. 🚀
