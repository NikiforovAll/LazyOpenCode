"""Parser for Command customizations."""

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


class CommandParser(ICustomizationParser):
    """Parses command/*.md files."""

    def can_parse(self, path: Path) -> bool:
        """Check if path is a command markdown file."""
        return path.is_file() and path.suffix == ".md" and path.parent.name == "command"

    def parse(self, path: Path, level: ConfigLevel) -> Customization:
        """Parse command file."""
        content, error = read_file_safe(path)

        metadata = {}
        description = None

        if content and not error:
            frontmatter, _ = parse_frontmatter(content)
            metadata = frontmatter
            description = frontmatter.get("description")

        return Customization(
            name=path.stem,
            type=CustomizationType.COMMAND,
            level=level,
            path=path,
            description=description or f"Command: {path.stem}",
            metadata=metadata,
            content=content,
            error=error,
        )
