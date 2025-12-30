"""Tests for full discovery service functionality."""

from pathlib import Path

from lazyopencode.models.customization import ConfigLevel, CustomizationType
from lazyopencode.services.discovery import ConfigDiscoveryService


class TestFullDiscovery:
    """Tests for complete discovery service functionality."""

    def test_discover_all_returns_all_types(
        self,
        full_user_config: Path,  # noqa: ARG002
        full_project_config: Path,  # noqa: ARG002
        fake_project_root: Path,
        fake_home: Path,
    ) -> None:
        """Test discover_all returns all customization types."""
        service = ConfigDiscoveryService(
            project_root=fake_project_root,
            global_config_path=fake_home / ".config" / "opencode",
        )

        all_customizations = service.discover_all()

        # Check all types are present
        types_found = {c.type for c in all_customizations}
        expected_types = {
            CustomizationType.COMMAND,
            CustomizationType.AGENT,
            CustomizationType.SKILL,
            CustomizationType.RULES,
            CustomizationType.MCP,
        }
        assert expected_types.issubset(types_found)

    def test_discover_all_has_correct_count(
        self,
        full_user_config: Path,  # noqa: ARG002
        full_project_config: Path,  # noqa: ARG002
        fake_project_root: Path,
        fake_home: Path,
    ) -> None:
        """Test discover_all returns expected number of customizations."""
        service = ConfigDiscoveryService(
            project_root=fake_project_root,
            global_config_path=fake_home / ".config" / "opencode",
        )

        all_customizations = service.discover_all()

        # Expected:
        # Commands: 2 (1 global + 1 project)
        # Agents: 2 (1 global + 1 project)
        # Skills: 2 (1 global + 1 project)
        # Rules: 3 (1 global + 1 project AGENTS.md + 1 project instruction file)
        # MCPs: 2 (1 global + 1 project)
        # Total: 11
        assert len(all_customizations) == 11

    def test_by_type_filters_correctly(
        self,
        full_user_config: Path,  # noqa: ARG002
        full_project_config: Path,  # noqa: ARG002
        fake_project_root: Path,
        fake_home: Path,
    ) -> None:
        """Test by_type filtering works correctly."""
        service = ConfigDiscoveryService(
            project_root=fake_project_root,
            global_config_path=fake_home / ".config" / "opencode",
        )

        # Test each type
        commands = service.by_type(CustomizationType.COMMAND)
        assert all(c.type == CustomizationType.COMMAND for c in commands)
        assert len(commands) == 2

        agents = service.by_type(CustomizationType.AGENT)
        assert all(a.type == CustomizationType.AGENT for a in agents)
        assert len(agents) == 2

        skills = service.by_type(CustomizationType.SKILL)
        assert all(s.type == CustomizationType.SKILL for s in skills)
        assert len(skills) == 2

        rules = service.by_type(CustomizationType.RULES)
        assert all(r.type == CustomizationType.RULES for r in rules)
        assert (
            len(rules) == 3
        )  # 1 global + 1 project AGENTS.md + 1 project instruction file

        mcps = service.by_type(CustomizationType.MCP)
        assert all(m.type == CustomizationType.MCP for m in mcps)
        assert len(mcps) == 2

    def test_by_level_filters_correctly(
        self,
        full_user_config: Path,  # noqa: ARG002
        full_project_config: Path,  # noqa: ARG002
        fake_project_root: Path,
        fake_home: Path,
    ) -> None:
        """Test by_level filtering works correctly."""
        service = ConfigDiscoveryService(
            project_root=fake_project_root,
            global_config_path=fake_home / ".config" / "opencode",
        )

        global_customizations = service.by_level(ConfigLevel.GLOBAL)
        assert all(c.level == ConfigLevel.GLOBAL for c in global_customizations)
        assert len(global_customizations) == 5  # 1 of each type

        project_customizations = service.by_level(ConfigLevel.PROJECT)
        assert all(c.level == ConfigLevel.PROJECT for c in project_customizations)
        assert len(project_customizations) == 6  # 1 of each type + 1 instruction file

    def test_caching_works(
        self,
        full_user_config: Path,  # noqa: ARG002
        full_project_config: Path,  # noqa: ARG002
        fake_project_root: Path,
        fake_home: Path,
    ) -> None:
        """Test that caching works correctly."""
        service = ConfigDiscoveryService(
            project_root=fake_project_root,
            global_config_path=fake_home / ".config" / "opencode",
        )

        # First call should populate cache
        first_call = service.discover_all()
        assert len(first_call) == 11

        # Second call should return same list (from cache)
        second_call = service.discover_all()
        assert first_call is second_call  # Same object (cached)

    def test_refresh_clears_cache(
        self,
        full_user_config: Path,  # noqa: ARG002
        full_project_config: Path,  # noqa: ARG002
        fake_project_root: Path,
        fake_home: Path,
    ) -> None:
        """Test that refresh() clears the cache."""
        service = ConfigDiscoveryService(
            project_root=fake_project_root,
            global_config_path=fake_home / ".config" / "opencode",
        )

        # First discovery
        first_call = service.discover_all()
        assert len(first_call) == 11

        # Refresh cache
        service.refresh()

        # Second discovery should be a new list
        second_call = service.discover_all()
        assert len(second_call) == 11
        assert first_call is not second_call  # Different objects

    def test_customization_properties(
        self,
        full_user_config: Path,  # noqa: ARG002
        full_project_config: Path,  # noqa: ARG002
        fake_project_root: Path,
        fake_home: Path,
    ) -> None:
        """Test customization objects have expected properties."""
        service = ConfigDiscoveryService(
            project_root=fake_project_root,
            global_config_path=fake_home / ".config" / "opencode",
        )

        customizations = service.discover_all()

        # All customizations should have required properties
        for c in customizations:
            assert c.name is not None
            assert c.type is not None
            assert c.level is not None
            assert c.path is not None
            assert not c.has_error

    def test_mixed_level_discovery(
        self,
        user_config_path: Path,  # noqa: ARG002
        project_config_path: Path,  # noqa: ARG002
        fake_project_root: Path,
        fake_home: Path,
    ) -> None:
        """Test discovering from both global and project levels."""
        service = ConfigDiscoveryService(
            project_root=fake_project_root,
            global_config_path=fake_home / ".config" / "opencode",
        )

        all_customizations = service.discover_all()
        global_count = len(service.by_level(ConfigLevel.GLOBAL))
        project_count = len(service.by_level(ConfigLevel.PROJECT))

        # Both should have items
        assert global_count > 0
        assert project_count > 0
        # Total should equal sum
        assert len(all_customizations) == global_count + project_count
