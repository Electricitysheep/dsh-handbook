# Chapter 16 Migrating from Claude Code, Codex, and OpenCode

> Goal of this chapter, arrive with your accumulated setup instead of rebuilding from zero. Every asset type gets a measured answer to "what happens to it in DSH", all verified against the `0.1.0-rc.6` source.

## TL;DR

1. Half the migration is free, project `CLAUDE.md` needs no move (DSH reads it natively) and `SKILL.md` loads unchanged
2. Half is mechanical, `.mcp.json` converts losslessly (tool names `mcp__server__tool` are identical on both sides) and hooks have a first party bridge
3. Automation, `npx dsh-movein --from <origin>` prints a dry-run moving estimate, `--apply` performs it; conversation history is `dsh-chat-import` territory
4. Budget before you move, the skill catalog costs about 28 tokens per skill on every request, move the skills you use, not the skills you have

## 16.1 Asset table (measured)

| Claude Code asset | DSH compatibility | What actually happens |
| --- | --- | --- |
| Project `CLAUDE.md` | Native, zero work | `instructionFileCandidates` includes it by default |
| Global `~/.claude/CLAUDE.md` | One symlink | The global slot is `$DSH_HOME/AGENTS.md` only |
| Skills (`SKILL.md`) | Format compatible as is | Unknown frontmatter keys ignored. `.claude/skills` is NOT a default root, land them in `~/.dsh/skills` |
| MCP (`.mcp.json`) | Lossless mechanical conversion | One `dsh-mcp-client` row per server, tool names identical |
| Hooks | First party bridge, partial | 7 of 30 events mapped, command hooks only. Known trap, matchers are case sensitive against DSH tool names (`Bash` does not select `bash`, upstream discussion #582), write them lowercase |
| Permission rules | Not native, bridgeable | `deny`/`ask` enforceable at `tools/pre-execute`, `allow` has no equivalent |
| Subagents | No direct import | Convert them to skills, the frontmatter is nearly identical |
| Sessions | Hardest, never hand-write | v0 format with no compatibility promise, use [dsh-chat-import](https://github.com/Nwflower/dsh-chat-import) |

### Codex and OpenCode

| Origin | Automated migration | Kept manual |
| --- | --- | --- |
| Codex | Global `AGENTS.md`, custom prompts, and stdio MCP from `config.toml` | Approval and sandbox policy |
| OpenCode | Instructions, skills, commands, agents, and local or remote MCP with V1 / V2 JSONC precedence | Sessions, permissions, plugins, and multiple or remote instructions |

DSH reads project `AGENTS.md` files natively. OpenCode `{env:VAR}` placeholders remain runtime environment references, and a JSONC parse failure blocks `--apply` before any write.

## 16.2 Automation

```sh
npx dsh-movein            # dry run, moving estimate, writes nothing
npx dsh-movein --apply    # move in
npx dsh-movein --from codex
npx dsh-movein --from opencode
npx dsh-movein --from opencode --apply
npx dsh-movein --reverse  # bring DSH-born skills back, dual boot
```

The plugin command `dsh plugin --profile web add dsh-movein` provides Claude Code and OpenCode migration tools. Codex migration uses the CLI. Permission rules get a migration diff report, unmapped rules are listed instead of silently dropped, and every move is recorded in `~/.dsh/movein-manifest.json`.

The project repository is now named [claude-to-opencode](https://github.com/sjh9714/claude-to-opencode) for its primary public route. The `dsh-movein` npm package and all DSH commands remain unchanged.

## 16.3 Boot traps the community actually hit

1. A patch row referencing a package the profile cannot resolve makes `dsh` boot fatally, install first, write config after.
2. Satellite npm dist-tags lag the core, pin installs to the host dsh version.
3. `@deepseek-ai/dsh-hook-protocol` is a peer the host does not ship, install it alongside the hooks bridge.

## 16.4 The token bill

The skill catalog is injected into every request, 143 tokens of framing plus about 28 tokens per skill. A 129-skill setup carries about 3.8k tokens per request, caching softens the money, not the context window. Reproducible measurement, [the dsh-movein token bill](https://github.com/sjh9714/claude-to-opencode/blob/main/docs/token-bill.md).
