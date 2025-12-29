"""Configuration discovery service."""

from pathlib import Path

from lazyopencode.models.customization import (
    ConfigLevel,
    Customization,
    CustomizationType,
)


class ConfigDiscoveryService:
    """Discovers OpenCode customizations from filesystem."""

    def __init__(
        self,
        project_root: Path | None = None,
        global_config_path: Path | None = None,
    ) -> None:
        """
        Initialize discovery service.

        Args:
            project_root: Project root directory (defaults to cwd)
            global_config_path: Global config path (defaults to ~/.config/opencode)
        """
        self.project_root = project_root or Path.cwd()
        self.global_config_path = global_config_path or (
            Path.home() / ".config" / "opencode"
        )
        self._parsers: list = []  # Will be populated with parsers
        self._cache: list[Customization] | None = None

    @property
    def project_config_path(self) -> Path:
        """Path to project's .opencode directory."""
        return self.project_root / ".opencode"

    def discover_all(self) -> list[Customization]:
        """
        Discover all customizations from global and project levels.

        Returns:
            List of all discovered customizations
        """
        if self._cache is not None:
            return self._cache

        customizations: list[Customization] = []

        # Discover from global config
        customizations.extend(self._discover_level(ConfigLevel.GLOBAL))

        # Discover from project config
        customizations.extend(self._discover_level(ConfigLevel.PROJECT))

        self._cache = customizations
        return customizations

    def _discover_level(self, level: ConfigLevel) -> list[Customization]:
        """Discover customizations at a specific level."""
        base_path = (
            self.global_config_path
            if level == ConfigLevel.GLOBAL
            else self.project_config_path
        )
        customizations: list[Customization] = []

        # Discover commands
        customizations.extend(self._discover_commands(base_path, level))

        # Discover agents
        customizations.extend(self._discover_agents(base_path, level))

        # Discover skills
        customizations.extend(self._discover_skills(base_path, level))

        # Discover rules (AGENTS.md)
        customizations.extend(self._discover_rules(level))

        # Discover MCPs from opencode.json
        customizations.extend(self._discover_mcps(level))

        # Discover plugins
        customizations.extend(self._discover_plugins(base_path, level))

        return customizations

    def _discover_commands(
        self, base_path: Path, level: ConfigLevel
    ) -> list[Customization]:
        """Discover command customizations."""
        commands_path = base_path / "command"
        if not commands_path.exists():
            return []

        customizations = []
        for md_file in commands_path.glob("*.md"):
            customizations.append(
                Customization(
                    name=md_file.stem,
                    type=CustomizationType.COMMAND,
                    level=level,
                    path=md_file,
                    description=f"Command: {md_file.stem}",
                )
            )
        return customizations

    def _discover_agents(
        self, base_path: Path, level: ConfigLevel
    ) -> list[Customization]:
        """Discover agent customizations."""
        agents_path = base_path / "agent"
        if not agents_path.exists():
            return []

        customizations = []
        for md_file in agents_path.glob("*.md"):
            customizations.append(
                Customization(
                    name=md_file.stem,
                    type=CustomizationType.AGENT,
                    level=level,
                    path=md_file,
                    description=f"Agent: {md_file.stem}",
                )
            )
        return customizations

    def _discover_skills(
        self, base_path: Path, level: ConfigLevel
    ) -> list[Customization]:
        """Discover skill customizations."""
        skills_path = base_path / "skill"
        if not skills_path.exists():
            return []

        customizations = []
        for skill_dir in skills_path.iterdir():
            if skill_dir.is_dir():
                skill_file = skill_dir / "SKILL.md"
                if skill_file.exists():
                    customizations.append(
                        Customization(
                            name=skill_dir.name,
                            type=CustomizationType.SKILL,
                            level=level,
                            path=skill_file,
                            description=f"Skill: {skill_dir.name}",
                        )
                    )
        return customizations

    def _discover_rules(self, level: ConfigLevel) -> list[Customization]:
        """Discover AGENTS.md rules files."""
        customizations = []

        if level == ConfigLevel.GLOBAL:
            agents_md = self.global_config_path / "AGENTS.md"
        else:
            agents_md = self.project_root / "AGENTS.md"

        if agents_md.exists():
            customizations.append(
                Customization(
                    name="AGENTS.md",
                    type=CustomizationType.RULES,
                    level=level,
                    path=agents_md,
                    description="Project rules and instructions",
                )
            )

        return customizations

    def _discover_mcps(self, level: ConfigLevel) -> list[Customization]:
        """Discover MCP configurations from opencode.json."""
        import json

        if level == ConfigLevel.GLOBAL:
            config_path = self.global_config_path / "opencode.json"
        else:
            config_path = self.project_root / "opencode.json"

        if not config_path.exists():
            return []

        customizations = []
        try:
            with open(config_path) as f:
                # Handle JSONC (JSON with comments)
                content = f.read()
                # Simple comment stripping (not perfect but works for most cases)
                lines = []
                for line in content.split("\n"):
                    stripped = line.strip()
                    if not stripped.startswith("//"):
                        # Remove inline comments
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
                        path=config_path,
                        description=f"MCP ({mcp_type})",
                        metadata=mcp_config,
                    )
                )
        except (json.JSONDecodeError, OSError):
            pass

        return customizations

    def _discover_plugins(
        self, base_path: Path, level: ConfigLevel
    ) -> list[Customization]:
        """Discover plugin customizations."""
        plugins_path = base_path / "plugin"
        if not plugins_path.exists():
            return []

        customizations = []
        for plugin_file in plugins_path.glob("*.js"):
            customizations.append(
                Customization(
                    name=plugin_file.stem,
                    type=CustomizationType.PLUGIN,
                    level=level,
                    path=plugin_file,
                    description=f"Plugin: {plugin_file.stem}",
                )
            )
        for plugin_file in plugins_path.glob("*.ts"):
            customizations.append(
                Customization(
                    name=plugin_file.stem,
                    type=CustomizationType.PLUGIN,
                    level=level,
                    path=plugin_file,
                    description=f"Plugin: {plugin_file.stem}",
                )
            )
        return customizations

    def refresh(self) -> None:
        """Clear cache and force re-discovery."""
        self._cache = None

    def by_type(self, ctype: CustomizationType) -> list[Customization]:
        """Get customizations filtered by type."""
        return [c for c in self.discover_all() if c.type == ctype]

    def by_level(self, level: ConfigLevel) -> list[Customization]:
        """Get customizations filtered by level."""
        return [c for c in self.discover_all() if c.level == level]
