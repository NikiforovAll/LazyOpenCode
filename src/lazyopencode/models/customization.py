"""Core data models for LazyOpenCode."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any


@dataclass
class SkillFile:
    """A file or directory within a skill folder."""

    name: str
    path: Path
    content: str | None = None
    is_directory: bool = False
    children: list[SkillFile] = field(default_factory=list)


@dataclass
class SkillMetadata:
    """Metadata specific to skills."""

    files: list[SkillFile] = field(default_factory=list)


class ConfigLevel(Enum):
    """Configuration level for customizations."""

    GLOBAL = "global"
    PROJECT = "project"

    @property
    def label(self) -> str:
        """Human-readable label."""
        return self.value.capitalize()

    @property
    def icon(self) -> str:
        """Icon for display."""
        return "G" if self == ConfigLevel.GLOBAL else "P"


class ConfigSource(Enum):
    """Source of customization configuration."""

    OPENCODE = "opencode"  # Native OpenCode customizations
    CLAUDE_CODE = "claude"  # Imported from Claude Code paths


class CustomizationType(Enum):
    """Type of OpenCode customization."""

    COMMAND = "command"
    AGENT = "agent"
    SKILL = "skill"
    RULES = "rules"
    MCP = "mcp"
    TOOL = "tool"
    PLUGIN = "plugin"

    @property
    def label(self) -> str:
        """Human-readable label."""
        return self.value.capitalize()

    @property
    def plural_label(self) -> str:
        """Plural form for panel titles."""
        if self == CustomizationType.RULES:
            return "Rules"
        return f"{self.label}s"

    @property
    def panel_key(self) -> str:
        """Keyboard shortcut for this type's panel."""
        mapping = {
            CustomizationType.COMMAND: "1",
            CustomizationType.AGENT: "2",
            CustomizationType.SKILL: "3",
            CustomizationType.RULES: "4",
            CustomizationType.MCP: "5",
            CustomizationType.TOOL: "6",
            CustomizationType.PLUGIN: "7",
        }
        return mapping[self]


@dataclass
class Customization:
    """Represents a single OpenCode customization."""

    name: str
    type: CustomizationType
    level: ConfigLevel
    path: Path
    description: str | None = None
    content: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    error: str | None = None
    source: ConfigSource = ConfigSource.OPENCODE
    source_level: str | None = None  # "user", "project", "plugin" for Claude Code

    @property
    def type_label(self) -> str:
        """Type label for display."""
        return self.type.label

    @property
    def level_label(self) -> str:
        """Level label for display."""
        return self.level.label

    @property
    def level_icon(self) -> str | None:
        """Level icon for compact display. Returns None for OpenCode items."""
        if self.source == ConfigSource.CLAUDE_CODE:
            return "👾"
        return None

    @property
    def display_name(self) -> str:
        """Formatted name for display with level indicator."""
        icon = self.level_icon
        parts = []
        if icon:
            parts.append(f"[{icon}]")
        parts.append(self.name)

        # Add dimmed plugin name for plugin-sourced items
        if self.source_level and self.source_level.startswith("plugin:"):
            plugin_name = self.source_level.replace("plugin:", "")
            parts.append(f"[dim]{plugin_name}[/dim]")

        return " ".join(parts)

    @property
    def has_error(self) -> bool:
        """Check if this customization has a parse error."""
        return self.error is not None

    def get_copy_targets(self) -> list[ConfigLevel]:
        """Get valid copy target levels for this item."""
        if self.source == ConfigSource.CLAUDE_CODE:
            return [ConfigLevel.GLOBAL, ConfigLevel.PROJECT]
        elif self.level == ConfigLevel.GLOBAL:
            return [ConfigLevel.PROJECT]
        else:
            return [ConfigLevel.GLOBAL]
