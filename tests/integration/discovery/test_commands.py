"""Tests for command discovery."""

from pathlib import Path

from lazyopencode.models.customization import ConfigLevel, CustomizationType
from lazyopencode.services.discovery import ConfigDiscoveryService


class TestCommandDiscovery:
    """Tests for command discovery."""

    def test_discovers_global_commands(
        self,
        user_config_path: Path,  # noqa: ARG002
        fake_project_root: Path,
        fake_home: Path,
    ) -> None:
        """Test discovering commands from global config."""
        service = ConfigDiscoveryService(
            project_root=fake_project_root,
            global_config_path=fake_home / ".config" / "opencode",
        )

        commands = service.by_type(CustomizationType.COMMAND)
        global_commands = [c for c in commands if c.level == ConfigLevel.GLOBAL]

        assert len(global_commands) == 1
        assert global_commands[0].name == "greet"

    def test_discovers_project_commands(
        self,
        project_config_path: Path,  # noqa: ARG002
        fake_project_root: Path,
        fake_home: Path,
    ) -> None:
        """Test discovering commands from project config."""
        service = ConfigDiscoveryService(
            project_root=fake_project_root,
            global_config_path=fake_home / ".config" / "opencode",
        )

        commands = service.by_type(CustomizationType.COMMAND)
        project_commands = [c for c in commands if c.level == ConfigLevel.PROJECT]

        assert len(project_commands) == 1
        assert project_commands[0].name == "project-cmd"

    def test_command_metadata_parsed(
        self,
        user_config_path: Path,  # noqa: ARG002
        fake_project_root: Path,
        fake_home: Path,
    ) -> None:
        """Test command metadata is correctly parsed."""
        service = ConfigDiscoveryService(
            project_root=fake_project_root,
            global_config_path=fake_home / ".config" / "opencode",
        )

        commands = service.by_type(CustomizationType.COMMAND)
        greet = next(c for c in commands if c.name == "greet")

        assert greet.description == "Say hello to someone"
        assert "allowed-tools" in greet.metadata

    def test_command_content_available(
        self,
        user_config_path: Path,  # noqa: ARG002
        fake_project_root: Path,
        fake_home: Path,
    ) -> None:
        """Test command content is available."""
        service = ConfigDiscoveryService(
            project_root=fake_project_root,
            global_config_path=fake_home / ".config" / "opencode",
        )

        commands = service.by_type(CustomizationType.COMMAND)
        greet = next(c for c in commands if c.name == "greet")

        assert greet.content is not None
        assert "---" in greet.content  # Has frontmatter
        assert "Greet Command" in greet.content or "greet" in greet.content.lower()

    def test_all_commands_discovered(
        self,
        full_user_config: Path,  # noqa: ARG002
        project_config_path: Path,  # noqa: ARG002
        fake_project_root: Path,
        fake_home: Path,
    ) -> None:
        """Test all commands are discovered from both levels."""
        service = ConfigDiscoveryService(
            project_root=fake_project_root,
            global_config_path=fake_home / ".config" / "opencode",
        )

        commands = service.by_type(CustomizationType.COMMAND)

        assert len(commands) == 2
        names = {c.name for c in commands}
        assert "greet" in names
        assert "project-cmd" in names
