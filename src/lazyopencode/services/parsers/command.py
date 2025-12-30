"""Parser for Command customizations."""

import json
from pathlib import Path

from lazyopencode.models.customization import (
    ConfigLevel,
    Customization,
    CustomizationType,
)
from lazyopencode.services.parsers import (
    ICustomizationParser,
    build_synthetic_markdown,
    parse_frontmatter,
    read_file_safe,
    strip_jsonc_comments,
)


class CommandParser(ICustomizationParser):
    """Parses command customizations from files or inline config."""

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

    def parse_inline_commands(
        self, path: Path, level: ConfigLevel
    ) -> list[Customization]:
        """Parse inline commands from opencode.json."""
        content, error = read_file_safe(path)
        if error or not content:
            return []

        customizations = []
        try:
            clean_content = strip_jsonc_comments(content)
            config = json.loads(clean_content)

            commands = config.get("command", {})
            for cmd_name, cmd_config in commands.items():
                if not isinstance(cmd_config, dict):
                    continue

                # Create a copy to avoid mutating the original
                metadata = cmd_config.copy()
                template = metadata.pop("template", "")
                description = metadata.get("description")

                markdown_content = build_synthetic_markdown(metadata, template)

                customizations.append(
                    Customization(
                        name=cmd_name,
                        type=CustomizationType.COMMAND,
                        level=level,
                        path=path,
                        description=description or f"Command: {cmd_name}",
                        metadata=metadata,
                        content=markdown_content,
                    )
                )
        except (json.JSONDecodeError, Exception):
            pass

        return customizations
