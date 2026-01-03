"""Parser for Claude Code slash command customizations."""

from pathlib import Path

from lazyopencode.models.customization import (
    ConfigLevel,
    ConfigSource,
    Customization,
    CustomizationType,
)
from lazyopencode.services.parsers import parse_frontmatter


class CommandParser:
    """Parser for slash command markdown files.

    File pattern: commands/**/*.md
    """

    def __init__(self, commands_dir: Path) -> None:
        """Initialize with the commands directory path."""
        self.commands_dir = commands_dir

    def can_parse(self, path: Path) -> bool:
        """Check if path is a markdown file in commands directory."""
        return path.suffix == ".md" and self.commands_dir in path.parents

    def parse(self, path: Path, level: ConfigLevel, source_level: str) -> Customization:
        """Parse a slash command markdown file."""
        try:
            content = path.read_text(encoding="utf-8")
        except OSError as e:
            return Customization(
                name=self._derive_name(path),
                type=CustomizationType.COMMAND,
                level=level,
                path=path,
                error=f"Failed to read file: {e}",
                source=ConfigSource.CLAUDE_CODE,
                source_level=source_level,
            )

        frontmatter, body = parse_frontmatter(content)

        description = frontmatter.get("description")
        if not description and body.strip():
            first_line = body.strip().split("\n")[0]
            if not first_line.startswith("#"):
                description = first_line[:100]

        return Customization(
            name=self._derive_name(path),
            type=CustomizationType.COMMAND,
            level=level,
            path=path,
            description=description,
            content=content,
            metadata=frontmatter,
            source=ConfigSource.CLAUDE_CODE,
            source_level=source_level,
        )

    def _derive_name(self, path: Path) -> str:
        """Derive command name from file path.

        For nested paths: dir/file.md -> dir:file
        For simple paths: file.md -> file
        """
        try:
            relative = path.relative_to(self.commands_dir)
            parts = list(relative.parts)
            parts[-1] = parts[-1].removesuffix(".md")
            return ":".join(parts)
        except ValueError:
            return path.stem
