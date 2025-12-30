# Scenario: Skills with File Tree

## Given
- `.opencode/skill/my-skill/` directory with:
  - `SKILL.md` - skill definition with frontmatter
  - `scripts/run.sh` - nested script file
  - `docs/guide.md` - nested documentation

## Expected
- 1 SKILL customization discovered
- Name from frontmatter or directory name
- metadata.files contains the file tree structure
- Nested files are included in the tree
- SKILL.md content is available in `content` field
