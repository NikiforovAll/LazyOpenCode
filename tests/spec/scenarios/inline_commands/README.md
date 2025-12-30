# Scenario: Inline Commands

## Given
- `opencode.json` with `command` section containing 2 commands:
  - `lint`: Run linting with description
  - `test`: Run tests with agent override
- No file-based commands in `.opencode/command/`

## Expected
- 2 COMMAND customizations discovered
- Both have `type=COMMAND`, `level=PROJECT`
- `template` field is in content body, NOT in metadata
- Other fields (description, agent) are in metadata
- Content matches frontmatter pattern: `^---\n...\n---\n...`
