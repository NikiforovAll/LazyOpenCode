"""Fixtures for scenario-based specification tests."""

from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from unittest.mock import patch

import pytest
from pyfakefs.fake_filesystem import FakeFilesystem

from lazyopencode.models.customization import (
    ConfigLevel,
    Customization,
    CustomizationType,
)
from lazyopencode.services.discovery import ConfigDiscoveryService

SCENARIOS_DIR = Path(__file__).parent / "scenarios"
FAKE_PROJECT = Path("/fake/project")
FAKE_HOME = Path("/fake/home")


@dataclass
class ScenarioResult:
    """Result of loading a test scenario with helper methods for assertions."""

    customizations: list[Customization]
    service: ConfigDiscoveryService
    scenario_name: str
    project_root: Path = field(default=FAKE_PROJECT)

    # --- Type-based accessors ---

    @property
    def commands(self) -> list[Customization]:
        """All COMMAND customizations."""
        return self.by_type(CustomizationType.COMMAND)

    @property
    def agents(self) -> list[Customization]:
        """All AGENT customizations."""
        return self.by_type(CustomizationType.AGENT)

    @property
    def skills(self) -> list[Customization]:
        """All SKILL customizations."""
        return self.by_type(CustomizationType.SKILL)

    @property
    def rules(self) -> list[Customization]:
        """All RULES customizations (AGENTS.md + instructions)."""
        return self.by_type(CustomizationType.RULES)

    @property
    def mcps(self) -> list[Customization]:
        """All MCP customizations."""
        return self.by_type(CustomizationType.MCP)

    @property
    def tools(self) -> list[Customization]:
        """All TOOL customizations."""
        return self.by_type(CustomizationType.TOOL)

    @property
    def plugins(self) -> list[Customization]:
        """All PLUGIN customizations."""
        return self.by_type(CustomizationType.PLUGIN)

    # --- Filtering methods ---

    def by_type(self, ctype: CustomizationType) -> list[Customization]:
        """Filter customizations by type."""
        return [c for c in self.customizations if c.type == ctype]

    def by_level(self, level: ConfigLevel) -> list[Customization]:
        """Filter customizations by level (GLOBAL or PROJECT)."""
        return [c for c in self.customizations if c.level == level]

    def by_name(self, name: str) -> list[Customization]:
        """Filter customizations by name (may return multiple)."""
        return [c for c in self.customizations if c.name == name]

    # --- Lookup methods ---

    def get(self, name: str) -> Customization | None:
        """Get a single customization by name, or None if not found."""
        return next((c for c in self.customizations if c.name == name), None)

    def get_command(self, name: str) -> Customization | None:
        """Get a command by name."""
        return next((c for c in self.commands if c.name == name), None)

    def get_agent(self, name: str) -> Customization | None:
        """Get an agent by name."""
        return next((c for c in self.agents if c.name == name), None)

    def get_skill(self, name: str) -> Customization | None:
        """Get a skill by name."""
        return next((c for c in self.skills if c.name == name), None)

    # --- Convenience properties ---

    @property
    def names(self) -> set[str]:
        """Set of all customization names."""
        return {c.name for c in self.customizations}

    @property
    def types(self) -> set[CustomizationType]:
        """Set of all customization types present."""
        return {c.type for c in self.customizations}

    @property
    def has_errors(self) -> bool:
        """Check if any customization has an error."""
        return any(c.has_error for c in self.customizations)

    @property
    def errors(self) -> list[Customization]:
        """Get all customizations with errors."""
        return [c for c in self.customizations if c.has_error]

    # --- Dunder methods ---

    def __len__(self) -> int:
        """Total number of customizations."""
        return len(self.customizations)

    def __iter__(self):
        """Iterate over customizations."""
        return iter(self.customizations)

    def __contains__(self, name: str) -> bool:
        """Check if a customization with given name exists."""
        return name in self.names


def _copy_scenario_to_fake_fs(
    fs: FakeFilesystem,
    scenario_name: str,
    target_root: Path,
) -> None:
    """Copy a scenario directory into the fake filesystem."""
    scenario_path = SCENARIOS_DIR / scenario_name

    # Add the real scenarios directory to pyfakefs so we can read from it
    if not fs.exists(SCENARIOS_DIR):
        fs.add_real_directory(SCENARIOS_DIR, read_only=True)

    if not scenario_path.exists():
        raise ValueError(f"Scenario '{scenario_name}' not found at {scenario_path}")

    # Walk through the scenario directory and copy files
    for item in scenario_path.rglob("*"):
        if item.name == "README.md":
            continue  # Skip README files (documentation only)

        relative = item.relative_to(scenario_path)
        target = target_root / relative

        if item.is_dir():
            if not fs.exists(target):
                fs.create_dir(target)
        elif item.is_file():
            content = item.read_text(encoding="utf-8")
            # Ensure parent directory exists
            if not fs.exists(target.parent):
                fs.create_dir(target.parent)
            fs.create_file(target, contents=content)


@pytest.fixture
def load_scenario(fs: FakeFilesystem) -> Callable[[str], ScenarioResult]:
    """
    Fixture that returns a function to load scenarios.

    Usage:
        def test_something(load_scenario):
            scenario = load_scenario("inline_commands")
            assert len(scenario.commands) == 2
    """

    def _load(scenario_name: str) -> ScenarioResult:
        # Create fake directories
        fs.create_dir(FAKE_PROJECT)
        fs.create_dir(FAKE_HOME)
        global_config = FAKE_HOME / ".config" / "opencode"
        fs.create_dir(global_config)

        # Copy scenario files to fake project
        _copy_scenario_to_fake_fs(fs, scenario_name, FAKE_PROJECT)

        # Patch Path.home() to return fake home
        with patch.object(Path, "home", return_value=FAKE_HOME):
            service = ConfigDiscoveryService(
                project_root=FAKE_PROJECT,
                global_config_path=global_config,
            )
            customizations = service.discover_all()

            return ScenarioResult(
                customizations=customizations,
                service=service,
                scenario_name=scenario_name,
                project_root=FAKE_PROJECT,
            )

    return _load
