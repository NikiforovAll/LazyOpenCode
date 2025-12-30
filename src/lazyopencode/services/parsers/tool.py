"""Parser for Tool customizations."""

import re
from pathlib import Path

from lazyopencode.models.customization import (
    ConfigLevel,
    Customization,
    CustomizationType,
)
from lazyopencode.services.parsers import (
    ICustomizationParser,
    read_file_safe,
)


class ToolParser(ICustomizationParser):
    """Parses tool customizations from TypeScript/JavaScript files."""

    VALID_EXTENSIONS = {".ts", ".js"}

    def can_parse(self, path: Path) -> bool:
        """Check if path is a tool file."""
        return (
            path.is_file()
            and path.suffix in self.VALID_EXTENSIONS
            and path.parent.name == "tool"
        )

    def parse(self, path: Path, level: ConfigLevel) -> Customization:
        """Parse tool file - shows source code as preview."""
        content, error = read_file_safe(path)

        description = None
        if content and not error:
            description = self._extract_description(content)

        return Customization(
            name=path.stem,
            type=CustomizationType.TOOL,
            level=level,
            path=path,
            description=description or f"Tool: {path.stem}",
            content=content,
            error=error,
        )

    def _extract_description(self, content: str) -> str | None:
        """
        Extract description from tool definition.

        Looks for patterns like:
        - description: "...",
        - description: '...',
        - description: `...`,
        """
        patterns = [
            r'description:\s*["\']([^"\']+)["\']',
            r"description:\s*`([^`]+)`",
        ]

        for pattern in patterns:
            match = re.search(pattern, content)
            if match:
                return match.group(1).strip()

        return None
