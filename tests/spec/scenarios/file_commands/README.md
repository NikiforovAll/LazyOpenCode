# Scenario: File-Based Commands

## Given
- `.opencode/command/` directory with 2 markdown files:
  - `greet.md`: Command with frontmatter (description, allowed-tools)
  - `deploy.md`: Command with minimal frontmatter
- No inline commands in `opencode.json`

## Expected
- 2 COMMAND customizations discovered
- Names derived from filenames (greet, deploy)
- Frontmatter fields available in metadata
- Full file content available in `content` field
