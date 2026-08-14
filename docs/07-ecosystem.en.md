[English](./07-ecosystem.en.md) | [中文](./07-ecosystem.md) · [← Back](../README.md)

# Chapter 7: Ecosystem & Resources

> **Goal of this chapter:** Give you a map for "joining the dsh ecosystem" — official entry points, the state of the community, and how to participate.

## TL;DR (30-second version)

1. **Official entry points**: GitHub repo (source + issues), API docs, Discord, Discussions. The current contribution entry is primarily via Discussions.
2. **External PRs are not accepted yet** (as of 2026-08-13), but the official team encourages dsh-plugin ecosystem projects, tutorials, and blog posts.
3. **Plugin ecosystem snapshot**: `DSH-better-sidebar` (most complete community plugin), an example speed-up plugin (Chapter 4 full breakdown), this handbook. Search `topic:dsh-plugin` to discover more.
4. **Beginner participation path**: use it → make small improvements (PRs to community plugins) → publish your own plugin → write content.
5. **Ecosystem day-zero = first-mover advantage**: every early ecosystem has a "first crab" bonus. Now is the time to get in.

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
| Example speed-up plugin | Tool-call speed-up (automatic reasoning_effort adjustment) | Teaching example (Chapter 4) |
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
| Performance tuning | Chapter 6 → Chapter 4 example source |
| Deep customization | Official AGENTS.md (architecture) → docs/architecture.md → packages/ source code |

## Closing Words

dsh was open-sourced on 2026-08-13. **Every day of the ecosystem is "early days."** This handbook will keep updating as dsh evolves. If a command in some chapter stops working, it's most likely due to rc version iteration. Always defer to the official changelog.

---

## Hands-on exercises

1. **Explore the official repo**: go to https://github.com/deepseek-ai/deepseek-harness. Read the README, then open `packages/AGENTS.md`. What architecture insights can you find?
2. **Join the community**: join the Discord or browse the Discussions tab. What topics are people talking about? What questions are unanswered?
3. **Install a community plugin**: if you haven't already, install `dsh-better-sidebar` or build the example speed-up plugin from Chapter 4. Use it for a day. What works well? What could be improved?
4. **Submit a suggestion**: go to the official Discussions tab. Write a proposal for a feature or improvement. Be specific: what problem does it solve? How would it work?
5. **Publish a plugin**: start from the minimal host plugin in Chapter 4. Add a feature (e.g. a new tool, a UI tweak). Tag it with `dsh-plugin` and publish to npm.
6. **Think**: why does the official team encourage ecosystem projects instead of accepting PRs? What are the advantages and risks of this approach?

## FAQ

- **Q: Can I contribute code to the official repo?** Not via PR at the moment (2026-08-13). The official team encourages ecosystem projects (plugins, tutorials, tools) instead. Check the CONTRIBUTING guide for updates.
- **Q: How do I discover community plugins?** Search GitHub for `topic:dsh-plugin`. The ecosystem is growing fast, so new plugins appear regularly.
- **Q: What's the best way to get help?** Join the Discord or post in the official Discussions tab. The community is active and responsive.
- **Q: Do I need to publish my plugin to npm?** No, but it's recommended. If you want others to use it easily, publish to npm and tag it with `dsh-plugin`.
- **Q: Is it too late to join the ecosystem?** No. The ecosystem was open-sourced on 2026-08-13. Every day is "early days." First-movers have an advantage, but the ecosystem is still small enough that quality contributions stand out.

---

Go claim your spot in this brand-new ecosystem. 🚀
