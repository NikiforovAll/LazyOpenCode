"""Parser for Rules customizations."""

from pathlib import Path

from lazyopencode.models.customization import (
    ConfigLevel,
    Customization,
    CustomizationType,
)
from lazyopencode.services.parsers import ICustomizationParser, read_file_safe


class RulesParser(ICustomizationParser):
    """Parses AGENTS.md files and instruction files."""

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

    def parse_instruction(
        self, path: Path, base_dir: Path, level: ConfigLevel
    ) -> Customization:
        """Parse an instruction file referenced from opencode.json instructions field.

        Args:
            path: Path to the instruction file
            base_dir: Base directory for computing relative path
            level: Configuration level (GLOBAL or PROJECT)

        Returns:
            Customization object for the instruction file
        """
        content, error = read_file_safe(path)

        # Compute relative path for display name
        try:
            # Use forward slashes for consistency across platforms
            relative_name = str(path.relative_to(base_dir)).replace("\\", "/")
        except ValueError:
            # If path is not relative to base_dir, use the filename
            relative_name = path.name

        return Customization(
            name=relative_name,
            type=CustomizationType.RULES,
            level=level,
            path=path,
            description="Instruction file",
            content=content,
            error=error,
        )
