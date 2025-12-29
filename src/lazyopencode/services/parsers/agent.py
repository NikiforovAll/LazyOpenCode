"""Parser for Agent customizations."""

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


class AgentParser(ICustomizationParser):
    """Parses agent/*.md files."""

    def can_parse(self, path: Path) -> bool:
        """Check if path is an agent markdown file."""
        return path.is_file() and path.suffix == ".md" and path.parent.name == "agent"

    def parse(self, path: Path, level: ConfigLevel) -> Customization:
        """Parse agent file."""
        content, error = read_file_safe(path)

        metadata = {}
        description = None

        if content and not error:
            frontmatter, _ = parse_frontmatter(content)
            metadata = frontmatter
            description = frontmatter.get("description")

        return Customization(
            name=path.stem,
            type=CustomizationType.AGENT,
            level=level,
            path=path,
            description=description or f"Agent: {path.stem}",
            metadata=metadata,
            content=content,
            error=error,
        )
