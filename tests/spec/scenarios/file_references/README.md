# Scenario: File References

## Given
- `opencode.json` with:
  - 1 agent using `{file:./prompts/agent.txt}` for prompt
  - 1 command using `{file:./templates/cmd.txt}` for template
- `prompts/agent.txt` - external prompt file
- `templates/cmd.txt` - external template file

## Expected
- 1 AGENT customization with resolved prompt content
- 1 COMMAND customization with resolved template content
- `{file:...}` patterns are replaced with actual file contents
- No `{file:...}` strings in final content
