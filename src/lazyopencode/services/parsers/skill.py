"""Parser for Skill customizations."""

from pathlib import Path

from lazyopencode.models.customization import (
    ConfigLevel,
    Customization,
    CustomizationType,
)
from lazyopencode.services.parsers import (
    ICustomizationParser,
    parse_frontmatter,
    read_file_safe,
)


class SkillParser(ICustomizationParser):
    """Parses skill/*/SKILL.md files."""

    def can_parse(self, path: Path) -> bool:
        """Check if path is a SKILL.md file in a skill directory."""
        return (
            path.is_file()
            and path.name == "SKILL.md"
            and path.parent.parent.name == "skill"
        )

    def parse(self, path: Path, level: ConfigLevel) -> Customization:
        """Parse skill file."""
        content, error = read_file_safe(path)

        metadata = {}
        description = None

        if content and not error:
            frontmatter, _ = parse_frontmatter(content)
            metadata = frontmatter
            description = frontmatter.get("description")

        return Customization(
            name=path.parent.name,
            type=CustomizationType.SKILL,
            level=level,
            path=path,
            description=description or f"Skill: {path.parent.name}",
            metadata=metadata,
            content=content,
            error=error,
        )
