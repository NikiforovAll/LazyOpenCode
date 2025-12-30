"""Tests for rules (AGENTS.md) discovery."""

from pathlib import Path

from lazyopencode.models.customization import ConfigLevel, CustomizationType
from lazyopencode.services.discovery import ConfigDiscoveryService


class TestRulesDiscovery:
    """Tests for rules discovery."""

    def test_discovers_global_rules(
        self,
        user_config_path: Path,  # noqa: ARG002
        fake_project_root: Path,
        fake_home: Path,
    ) -> None:
        """Test discovering rules from global config."""
        service = ConfigDiscoveryService(
            project_root=fake_project_root,
            global_config_path=fake_home / ".config" / "opencode",
        )

        rules = service.by_type(CustomizationType.RULES)
        global_rules = [r for r in rules if r.level == ConfigLevel.GLOBAL]

        assert len(global_rules) == 1
        assert global_rules[0].name == "AGENTS.md"

    def test_discovers_project_rules(
        self,
        project_config_path: Path,  # noqa: ARG002
        fake_project_root: Path,
        fake_home: Path,
    ) -> None:
        """Test discovering rules from project root."""
        service = ConfigDiscoveryService(
            project_root=fake_project_root,
            global_config_path=fake_home / ".config" / "opencode",
        )

        rules = service.by_type(CustomizationType.RULES)
        project_rules = [r for r in rules if r.level == ConfigLevel.PROJECT]

        assert len(project_rules) == 1
        assert project_rules[0].name == "AGENTS.md"

    def test_rules_content_available(
        self,
        user_config_path: Path,  # noqa: ARG002
        fake_project_root: Path,
        fake_home: Path,
    ) -> None:
        """Test rules content is available."""
        service = ConfigDiscoveryService(
            project_root=fake_project_root,
            global_config_path=fake_home / ".config" / "opencode",
        )

        rules = service.by_type(CustomizationType.RULES)
        global_rules = [r for r in rules if r.level == ConfigLevel.GLOBAL]

        assert len(global_rules) > 0
        assert global_rules[0].content is not None
        assert len(global_rules[0].content) > 0

    def test_rules_level_separation(
        self,
        full_user_config: Path,  # noqa: ARG002
        project_config_path: Path,  # noqa: ARG002
        fake_project_root: Path,
        fake_home: Path,
    ) -> None:
        """Test both global and project rules are discovered."""
        service = ConfigDiscoveryService(
            project_root=fake_project_root,
            global_config_path=fake_home / ".config" / "opencode",
        )

        rules = service.by_type(CustomizationType.RULES)

        assert len(rules) == 2
        levels = {r.level for r in rules}
        assert ConfigLevel.GLOBAL in levels
        assert ConfigLevel.PROJECT in levels

    def test_rules_have_expected_properties(
        self,
        user_config_path: Path,  # noqa: ARG002
        fake_project_root: Path,
        fake_home: Path,
    ) -> None:
        """Test rules have expected properties."""
        service = ConfigDiscoveryService(
            project_root=fake_project_root,
            global_config_path=fake_home / ".config" / "opencode",
        )

        rules = service.by_type(CustomizationType.RULES)

        for rule in rules:
            assert rule.type == CustomizationType.RULES
            assert rule.name == "AGENTS.md"
            assert rule.path is not None
            assert rule.content is not None
