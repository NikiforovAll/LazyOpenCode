"""Parser for Claude Code subagent customizations."""

from pathlib import Path

from lazyopencode.models.customization import (
    ConfigLevel,
    ConfigSource,
    Customization,
    CustomizationType,
)
from lazyopencode.services.parsers import parse_frontmatter


class AgentParser:
    """Parser for subagent markdown files.

    File pattern: agents/*.md
    """

    def __init__(self, agents_dir: Path) -> None:
        """Initialize with the agents directory path."""
        self.agents_dir = agents_dir

    def can_parse(self, path: Path) -> bool:
        """Check if path is a markdown file in agents directory."""
        return path.suffix == ".md" and path.parent == self.agents_dir

    def parse(self, path: Path, level: ConfigLevel, source_level: str) -> Customization:
        """Parse a subagent markdown file."""
        try:
            content = path.read_text(encoding="utf-8")
        except OSError as e:
            return Customization(
                name=path.stem,
                type=CustomizationType.AGENT,
                level=level,
                path=path,
                error=f"Failed to read file: {e}",
                source=ConfigSource.CLAUDE_CODE,
                source_level=source_level,
            )

        frontmatter, _ = parse_frontmatter(content)

        name = frontmatter.get("name", path.stem)
        description = frontmatter.get("description")

        return Customization(
            name=name,
            type=CustomizationType.AGENT,
            level=level,
            path=path,
            description=description,
            content=content,
            metadata=frontmatter,
            source=ConfigSource.CLAUDE_CODE,
            source_level=source_level,
        )
