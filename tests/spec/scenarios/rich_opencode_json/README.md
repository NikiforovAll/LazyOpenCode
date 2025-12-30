# Rich opencode.json Scenario

Tests advanced features of opencode.json configuration.

## Given

An `opencode.json` file with:
- **Instructions array** with glob pattern (`docs/*.md`)
- **Inline agents** with `{file:./path}` prompt reference
- **Inline commands** with script references
- **Multiple MCP servers**: local (uvx, npx) and remote (with oauth)
- **Environment variable substitution** (`{env:VAR}`)
- **Complex permissions** block (not parsed by discovery, but present)

Supporting files:
- `prompts/security-audit.txt` - Agent prompt content
- `docs/api-standards.md` - Referenced by instructions glob
- `scripts/fake-lint.sh` - Referenced by command template

## Expected

| Type | Count | Names |
|------|-------|-------|
| RULES | 1 | `docs/api-standards.md` (from instructions glob) |
| AGENT | 1 | `inline-security-auditor` |
| COMMAND | 2 | `inline-lint`, `inline-echo` |
| MCP | 3 | `sqlite`, `github`, `sentry` |

### Detail Expectations

- Agent `inline-security-auditor`:
  - Has resolved prompt content (not `{file:...}` pattern)
  - Content includes "security auditor" text
  - Metadata has `mode: subagent`

- Command `inline-lint`:
  - Template contains script reference
  - Has `agent: plan` override

- Command `inline-echo`:
  - Template contains `$ARGUMENTS` placeholder

- MCPs:
  - `sqlite`: type=local, uses uvx
  - `github`: type=local, uses npx, has environment config
  - `sentry`: type=remote, has oauth block
