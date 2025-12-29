"""Parser for Rules customizations."""

from pathlib import Path

from lazyopencode.models.customization import (
    ConfigLevel,
    Customization,
    CustomizationType,
)
from lazyopencode.services.parsers import ICustomizationParser, read_file_safe


class RulesParser(ICustomizationParser):
    """Parses AGENTS.md files."""

    def can_parse(self, path: Path) -> bool:
        """Check if path is an AGENTS.md file."""
        return path.is_file() and path.name == "AGENTS.md"

    def parse(self, path: Path, level: ConfigLevel) -> Customization:
        """Parse rules file."""
        content, error = read_file_safe(path)

        return Customization(
            name="AGENTS.md",
            type=CustomizationType.RULES,
            level=level,
            path=path,
            description="Project rules and instructions",
            content=content,
            error=error,
        )
