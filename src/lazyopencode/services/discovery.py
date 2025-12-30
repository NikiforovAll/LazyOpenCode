"""Configuration discovery service."""

from pathlib import Path

from lazyopencode.models.customization import (
    ConfigLevel,
    Customization,
    CustomizationType,
)
from lazyopencode.services.parsers.agent import AgentParser
from lazyopencode.services.parsers.command import CommandParser
from lazyopencode.services.parsers.mcp import MCPParser
from lazyopencode.services.parsers.rules import RulesParser
from lazyopencode.services.parsers.skill import SkillParser


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
        self._parsers = {
            CustomizationType.COMMAND: CommandParser(),
            CustomizationType.AGENT: AgentParser(),
            CustomizationType.SKILL: SkillParser(),
            CustomizationType.RULES: RulesParser(),
            CustomizationType.MCP: MCPParser(),
        }
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
        customizations.extend(self._discover_inline_commands(level))

        # Discover agents
        customizations.extend(self._discover_agents(base_path, level))
        customizations.extend(self._discover_inline_agents(level))

        # Discover skills
        customizations.extend(self._discover_skills(base_path, level))

        # Discover rules (AGENTS.md)
        customizations.extend(self._discover_rules(level))

        # Discover MCPs from opencode.json
        customizations.extend(self._discover_mcps(level))

        return customizations

    def _discover_commands(
        self, base_path: Path, level: ConfigLevel
    ) -> list[Customization]:
        """Discover command customizations."""
        commands_path = base_path / "command"
        if not commands_path.exists():
            return []

        customizations = []
        parser = self._parsers[CustomizationType.COMMAND]

        for md_file in commands_path.glob("*.md"):
            if parser.can_parse(md_file):
                customizations.append(parser.parse(md_file, level))

        return customizations

    def _discover_inline_commands(self, level: ConfigLevel) -> list[Customization]:
        """Discover inline commands from opencode.json."""
        if level == ConfigLevel.GLOBAL:
            config_path = self.global_config_path / "opencode.json"
        else:
            config_path = self.project_root / "opencode.json"

        parser = self._parsers[CustomizationType.COMMAND]
        if isinstance(parser, CommandParser) and config_path.exists():
            return parser.parse_inline_commands(config_path, level)

        return []

    def _discover_agents(
        self, base_path: Path, level: ConfigLevel
    ) -> list[Customization]:
        """Discover agent customizations."""
        agents_path = base_path / "agent"
        if not agents_path.exists():
            return []

        customizations = []
        parser = self._parsers[CustomizationType.AGENT]

        for md_file in agents_path.glob("*.md"):
            if parser.can_parse(md_file):
                customizations.append(parser.parse(md_file, level))

        return customizations

    def _discover_inline_agents(self, level: ConfigLevel) -> list[Customization]:
        """Discover inline agents from opencode.json."""
        if level == ConfigLevel.GLOBAL:
            config_path = self.global_config_path / "opencode.json"
        else:
            config_path = self.project_root / "opencode.json"

        parser = self._parsers[CustomizationType.AGENT]
        if isinstance(parser, AgentParser) and config_path.exists():
            return parser.parse_inline_agents(config_path, level)

        return []

    def _discover_skills(
        self, base_path: Path, level: ConfigLevel
    ) -> list[Customization]:
        """Discover skill customizations."""
        skills_path = base_path / "skill"
        if not skills_path.exists():
            return []

        customizations = []
        parser = self._parsers[CustomizationType.SKILL]

        for skill_dir in skills_path.iterdir():
            if skill_dir.is_dir():
                skill_file = skill_dir / "SKILL.md"
                if parser.can_parse(skill_file):
                    customizations.append(parser.parse(skill_file, level))

        return customizations

    def _discover_rules(self, level: ConfigLevel) -> list[Customization]:
        """Discover AGENTS.md rules files."""
        customizations = []
        parser = self._parsers[CustomizationType.RULES]

        if level == ConfigLevel.GLOBAL:
            agents_md = self.global_config_path / "AGENTS.md"
        else:
            agents_md = self.project_root / "AGENTS.md"

        if parser.can_parse(agents_md):
            customizations.append(parser.parse(agents_md, level))

        return customizations

    def _discover_mcps(self, level: ConfigLevel) -> list[Customization]:
        """Discover MCP configurations from opencode.json."""
        if level == ConfigLevel.GLOBAL:
            config_path = self.global_config_path / "opencode.json"
        else:
            config_path = self.project_root / "opencode.json"

        parser = self._parsers[CustomizationType.MCP]
        # Cast to MCPParser to access parse_mcps
        if isinstance(parser, MCPParser) and parser.can_parse(config_path):
            return parser.parse_mcps(config_path, level)

        return []

    def refresh(self) -> None:
        """Clear cache and force re-discovery."""
        self._cache = None

    def by_type(self, ctype: CustomizationType) -> list[Customization]:
        """Get customizations filtered by type."""
        return [c for c in self.discover_all() if c.type == ctype]

    def by_level(self, level: ConfigLevel) -> list[Customization]:
        """Get customizations filtered by level."""
        return [c for c in self.discover_all() if c.level == level]
