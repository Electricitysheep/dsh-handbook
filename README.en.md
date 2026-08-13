# DeepSeek Harness Handbook · dsh-handbook

> **From zero to one with DeepSeek Harness — the beginner's encyclopedia for DeepSeek's open-source agent runtime.**
> [中文](./README.md) · English · Live-updating with dsh rc releases

<div align="center">

![dsh-handbook](https://img.shields.io/badge/dsh--handbook-handbook-blue)
![chapters](https://img.shields.io/badge/chapters-7-green)
![pdf](https://img.shields.io/badge/PDF-1.25MB-orange)
![license](https://img.shields.io/badge/license-CC--BY--NC--SA--4.0-lightgrey)
![dsh](https://img.shields.io/badge/dsh-0.1.0--rc.6-8A2BE2)

</div>

## What this is

**DeepSeek Harness (`dsh`)** is the agent runtime open-sourced by DeepSeek on 2026-08-13 — an "everything is a plugin" framework. Official docs focus on architecture; **this handbook fills the beginner path**: from "what is an agent runtime" to install, usage, plugin development and performance tuning — every command copy-pasteable and verified on real hardware. **Any developer can go from zero to productive.**

## 30-second quickstart

```bash
# 1. Install (needs Node.js ≥ 22)
npx -y @deepseek-ai/dsh web

# 2. Open http://127.0.0.1:3080 and chat
# 3. Or run a one-shot task (scripts / CI)
dsh --profile headless "Hello, introduce yourself in one sentence"
```

## Table of contents (zero → one)

| # | Chapter | What you'll learn | Status |
|---|---|---|---|
| 1 | [Understanding DeepSeek Harness](./docs/01-intro.md) | What it is, why it matters, vs Claude Code | ✅ |
| 2 | [5-Minute Quickstart](./docs/02-quickstart.md) | Install, web/headless modes, models & reasoning effort, troubleshooting | ✅ |
| 3 | [Profiles & the Plugin System](./docs/03-profiles.md) | The customizable skeleton, mounting plugins, host/client halves, extension points, real pitfalls | ✅ |
| 4 | [Plugin Development, Hands-On](./docs/04-plugin-dev.md) | Write your first plugin (full code + tests + live verification) | ✅ |
| 5 | [Real-World Cases](./docs/05-cases.md) | Three real open-source PRs, end to end | ✅ |
| 6 | [Advanced & Performance Tuning](./docs/06-advanced.md) | reasoning_effort strategy, latency analysis, pitfalls | ✅ |
| 7 | [Ecosystem & Resources](./docs/07-ecosystem.md) | Official entry points, how to join, reading paths | ✅ |

## Demo

| Demo | What it shows |
|---|---|
| [📺 30s overview of dsh](./docs/demo.md) | Install → Web UI → Headless → plugins (real screenshots) |
| [⚡ Community plugin demo](./docs/demo-plugin.md) (planned) | Git panel / tool-turbo hands-on |

## PDF

- **Chinese full edition**: [DeepSeek-Harness-白皮书.pdf](./DeepSeek-Harness-白皮书.pdf) (7 chapters, 1.25MB)
- English PDF will be published as English chapters land

## Why read this (vs official docs)

| Official docs | This handbook |
|---|---|
| Architecture view (AGENTS.md / architecture.md) | **Beginner view**: a zero-to-one path |
| Scattered examples | **Every chapter runnable**, commands verified |
| English only | **Bilingual**, Chinese-first |
| No ecosystem practice | **Real plugin/PR breakdowns** (pitfalls & safety included) |

## Ecosystem links

Methodology comes from real open-source work:
- [dsh-tool-turbo](https://github.com/Electricitysheep/dsh-tool-turbo) — tool-call latency optimizer (source of chapters 4/6)
- [DSH-better-sidebar](https://github.com/omdsh-dev/DSH-better-sidebar) — community sidebar plugin (chapter 5 cases)

## Contribute

- Commands broken? rc releases iterate fast — open an issue
- Want to help? See [Chapter 7: Ecosystem](./docs/07-ecosystem.md)

## Version

- Based on dsh `0.1.0-rc.6` / DeepSeek-V4-Flash-0731 (open-sourced 2026-08-13)
- Verified on Windows 11 + Node 24

## License

Content [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) · Example code MIT
