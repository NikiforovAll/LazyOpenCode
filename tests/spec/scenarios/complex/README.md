# Complex Scenario

Tests discovery of ALL customization types in a single project.

## Given

A project with every type of customization:

### Rules
- `AGENTS.md` - Project rules at root

### opencode.json
- `instructions` array with glob pattern (`docs/*.md`)
- Inline `agent` definition with `{file:./prompts/auditor.txt}` reference
- Inline `command` definitions (2 commands)
- `mcp` servers (2 servers)

### File-based Definitions
- `.opencode/agent/reviewer.md` - File-based agent
- `.opencode/command/verify.md` - File-based command
- `.opencode/skill/deploy-helper/SKILL.md` - Skill with nested files
- `.opencode/tool/search.ts` - TypeScript tool
- `.opencode/plugin/metrics.ts` - TypeScript plugin

### Supporting Files
- `docs/guidelines.md` - Referenced by instructions
- `prompts/auditor.txt` - Referenced by inline agent
- `.opencode/skill/deploy-helper/scripts/deploy.sh` - Nested skill file

## Expected

| Type | Count | Names |
|------|-------|-------|
| RULES | 2 | `AGENTS.md`, `docs/guidelines.md` (from instructions) |
| AGENT | 2 | `inline-auditor`, `reviewer` |
| COMMAND | 3 | `inline-echo`, `inline-build`, `verify` |
| SKILL | 1 | `deploy-helper` |
| MCP | 2 | `sqlite`, `filesystem` |
| TOOL | 1 | `search` |
| PLUGIN | 1 | `metrics` |

**Total: 12 customizations**

### Key Assertions

1. **No duplicates** - Each customization discovered exactly once
2. **All types present** - All 7 customization types discovered
3. **File references resolved** - `{file:...}` patterns replaced with content
4. **Skill has file tree** - `deploy-helper` includes nested scripts
5. **Plugin has metadata** - Exports and hooks extracted
6. **Tool has description** - Description extracted from source
