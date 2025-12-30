# Scenario: Minimal Configuration

## Given
- A project with only `AGENTS.md` at the root
- No `opencode.json`
- No `.opencode/` directory

## Expected
- 1 RULES customization discovered (AGENTS.md)
- No commands, agents, skills, MCPs, tools, or plugins
- All customizations are at PROJECT level
