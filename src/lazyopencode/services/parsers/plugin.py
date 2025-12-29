"""Parser for Plugin customizations."""

from pathlib import Path

from lazyopencode.models.customization import (
    ConfigLevel,
    Customization,
    CustomizationType,
)
from lazyopencode.services.parsers import ICustomizationParser, read_file_safe


class PluginParser(ICustomizationParser):
    """Parses plugin files."""

    def can_parse(self, path: Path) -> bool:
        """Check if path is a plugin file."""
        return (
            path.is_file()
            and path.suffix in (".js", ".ts")
            and path.parent.name == "plugin"
        )

    def parse(self, path: Path, level: ConfigLevel) -> Customization:
        """Parse plugin file."""
        content, error = read_file_safe(path)

        return Customization(
            name=path.stem,
            type=CustomizationType.PLUGIN,
            level=level,
            path=path,
            description=f"Plugin: {path.stem}",
            content=content,
            error=error,
        )
