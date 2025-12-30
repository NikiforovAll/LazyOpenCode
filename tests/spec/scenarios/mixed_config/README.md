# Scenario: Mixed Configuration

## Given
- `opencode.json` with:
  - 1 inline command (`inline-cmd`)
  - 1 inline agent (`inline-agent`)
  - 1 MCP server (`sqlite`)
- `.opencode/command/file-cmd.md` - file-based command
- `.opencode/agent/file-agent.md` - file-based agent
- `AGENTS.md` - project rules

## Expected
- 2 COMMAND customizations (1 inline, 1 file)
- 2 AGENT customizations (1 inline, 1 file)
- 1 MCP customization
- 1 RULES customization
- Total: 6 customizations
- All at PROJECT level
