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


class CustomizationType(Enum):
    """Type of OpenCode customization."""

    COMMAND = "command"
    AGENT = "agent"
    SKILL = "skill"
    RULES = "rules"
    MCP = "mcp"
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

    @property
    def type_label(self) -> str:
        """Type label for display."""
        return self.type.label

    @property
    def level_label(self) -> str:
        """Level label for display."""
        return self.level.label

    @property
    def level_icon(self) -> str:
        """Level icon for compact display."""
        return self.level.icon

    @property
    def display_name(self) -> str:
        """Formatted name for display with level indicator."""
        return f"[{self.level_icon}] {self.name}"

    @property
    def has_error(self) -> bool:
        """Check if this customization has a parse error."""
        return self.error is not None
