"""Parser for MCP customizations."""

import json
from pathlib import Path

from lazyopencode.models.customization import (
    ConfigLevel,
    Customization,
    CustomizationType,
)
from lazyopencode.services.parsers import ICustomizationParser, read_file_safe


class MCPParser(ICustomizationParser):
    """Parses MCP configurations from opencode.json."""

    def can_parse(self, path: Path) -> bool:
        """Check if path is opencode.json file."""
        return path.is_file() and path.name == "opencode.json"

    def parse(self, path: Path, level: ConfigLevel) -> Customization:
        """
        Parse MCP file.
        Note: This returns a 'container' customization for the file itself.
        Real logic for individual MCPs is in parse_mcps.
        """
        return Customization(
            name="opencode.json",
            type=CustomizationType.MCP,
            level=level,
            path=path,
            description="MCP Configuration File",
        )

    def parse_mcps(self, path: Path, level: ConfigLevel) -> list[Customization]:
        """Parse opencode.json and return list of MCP customizations."""
        content, error = read_file_safe(path)
        if error or not content:
            return []

        customizations = []
        try:
            # Handle JSONC (simple comment stripping)
            lines = []
            for line in content.split("\n"):
                stripped = line.strip()
                if not stripped.startswith("//"):
                    # Remove inline comments (naive)
                    if "//" in line and '"' not in line.split("//")[0]:
                        line = line.split("//")[0]
                    lines.append(line)
            clean_content = "\n".join(lines)
            config = json.loads(clean_content)

            mcps = config.get("mcp", {})
            for mcp_name, mcp_config in mcps.items():
                mcp_type = mcp_config.get("type", "unknown")
                customizations.append(
                    Customization(
                        name=mcp_name,
                        type=CustomizationType.MCP,
                        level=level,
                        path=path,
                        description=f"MCP ({mcp_type})",
                        metadata=mcp_config,
                        content=json.dumps(mcp_config, indent=2),
                    )
                )
        except (json.JSONDecodeError, Exception):
            pass

        return customizations
