"""Parser for Agent customizations."""

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


class AgentParser(ICustomizationParser):
    """Parses agent customizations from files or inline config."""

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

    def parse_inline_agents(
        self, path: Path, level: ConfigLevel
    ) -> list[Customization]:
        """Parse inline agents from opencode.json."""
        content, error = read_file_safe(path)
        if error or not content:
            return []

        customizations = []
        try:
            clean_content = strip_jsonc_comments(content)
            config = json.loads(clean_content)

            agents = config.get("agent", {})
            for agent_name, agent_config in agents.items():
                if not isinstance(agent_config, dict):
                    continue

                metadata = agent_config.copy()
                prompt = metadata.pop("prompt", "")
                description = metadata.get("description")

                markdown_content = build_synthetic_markdown(metadata, prompt)

                customizations.append(
                    Customization(
                        name=agent_name,
                        type=CustomizationType.AGENT,
                        level=level,
                        path=path,
                        description=description or f"Agent: {agent_name}",
                        metadata=metadata,
                        content=markdown_content,
                    )
                )
        except (json.JSONDecodeError, Exception):
            pass

        return customizations
