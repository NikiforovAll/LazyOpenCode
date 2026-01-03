"""Service for discovering Claude Code customizations."""

from pathlib import Path

from lazyopencode.models.customization import (
    ConfigLevel,
    Customization,
)
from lazyopencode.services.claude_code.parsers.agent import AgentParser
from lazyopencode.services.claude_code.parsers.command import CommandParser
from lazyopencode.services.claude_code.parsers.skill import SkillParser
from lazyopencode.services.claude_code.plugin_loader import PluginLoader
from lazyopencode.services.gitignore_filter import GitignoreFilter


class ClaudeCodeDiscoveryService:
    """Discovers Claude Code customizations from standard Claude Code paths.

    This is a separate layer responsible for Claude Code integration.

    Discovery paths:
    - User: ~/.claude/
    - Project: ./.claude/
    - Plugins: ~/.claude/plugins/ (via plugin registry)
    """

    def __init__(self, project_root: Path) -> None:
        self.project_root = project_root
        self.user_path = Path.home() / ".claude"
        self.plugins_path = self.user_path / "plugins"
        self._gitignore_filter = GitignoreFilter(project_root=project_root)
        self._plugin_loader = PluginLoader(
            user_config_path=self.user_path,
            project_root=project_root,
        )

    def discover_all(self) -> list[Customization]:
        """Discover all Claude Code customizations."""
        customizations: list[Customization] = []

        # User-level
        customizations.extend(self._discover_from_path(self.user_path, "user"))

        # Project-level
        project_claude = self.project_root / ".claude"
        customizations.extend(self._discover_from_path(project_claude, "project"))

        # Plugin-level (using plugin registry)
        customizations.extend(self._discover_from_plugins())

        return customizations

    def _discover_from_path(self, base: Path, source_level: str) -> list[Customization]:
        """Discover commands, agents, skills from a Claude Code path."""
        if not base.exists():
            return []

        customizations: list[Customization] = []
        level = ConfigLevel.GLOBAL if source_level == "user" else ConfigLevel.PROJECT

        # Commands: base/commands/**/*.md
        commands_path = base / "commands"
        customizations.extend(
            self._discover_commands(commands_path, level, source_level)
        )

        # Agents: base/agents/*.md
        agents_path = base / "agents"
        customizations.extend(self._discover_agents(agents_path, level, source_level))

        # Skills: base/skills/*/SKILL.md
        skills_path = base / "skills"
        customizations.extend(self._discover_skills(skills_path, level, source_level))

        return customizations

    def _discover_commands(
        self, commands_path: Path, level: ConfigLevel, source_level: str
    ) -> list[Customization]:
        """Discover command customizations from commands directory."""
        if not commands_path.exists():
            return []

        customizations: list[Customization] = []
        parser = CommandParser(commands_path)

        # Use rglob for nested commands (commands/**/*.md)
        for md_file in commands_path.rglob("*.md"):
            if parser.can_parse(md_file):
                customizations.append(parser.parse(md_file, level, source_level))

        return customizations

    def _discover_agents(
        self, agents_path: Path, level: ConfigLevel, source_level: str
    ) -> list[Customization]:
        """Discover agent customizations from agents directory."""
        if not agents_path.exists():
            return []

        customizations: list[Customization] = []
        parser = AgentParser(agents_path)

        for md_file in agents_path.glob("*.md"):
            if parser.can_parse(md_file):
                customizations.append(parser.parse(md_file, level, source_level))

        return customizations

    def _discover_skills(
        self, skills_path: Path, level: ConfigLevel, source_level: str
    ) -> list[Customization]:
        """Discover skill customizations from skills directory."""
        if not skills_path.exists():
            return []

        customizations: list[Customization] = []
        parser = SkillParser(skills_path, gitignore_filter=self._gitignore_filter)

        for skill_dir in skills_path.iterdir():
            if skill_dir.is_dir():
                skill_file = skill_dir / "SKILL.md"
                if skill_file.exists() and parser.can_parse(skill_file):
                    customizations.append(parser.parse(skill_file, level, source_level))

        return customizations

    def _discover_from_plugins(self) -> list[Customization]:
        """Discover customizations from installed Claude Code plugins."""
        customizations: list[Customization] = []

        for plugin_info in self._plugin_loader.get_all_plugins():
            install_path = plugin_info.install_path
            source_level = f"plugin:{plugin_info.short_name}"

            # Commands
            commands_path = install_path / "commands"
            customizations.extend(
                self._discover_commands(commands_path, ConfigLevel.GLOBAL, source_level)
            )

            # Agents
            agents_path = install_path / "agents"
            customizations.extend(
                self._discover_agents(agents_path, ConfigLevel.GLOBAL, source_level)
            )

            # Skills
            skills_path = install_path / "skills"
            customizations.extend(
                self._discover_skills(skills_path, ConfigLevel.GLOBAL, source_level)
            )

        return customizations

    def refresh(self) -> None:
        """Clear cached plugin registry to force reload."""
        self._plugin_loader.refresh()
