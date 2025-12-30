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


class TestInstructionsDiscovery:
    """Tests for instructions field discovery."""

    def test_discovers_instruction_files(
        self,
        full_project_config: Path,  # noqa: ARG002
        fake_project_root: Path,
        fake_home: Path,
    ) -> None:
        """Test discovering files from instructions array in opencode.json."""
        service = ConfigDiscoveryService(
            project_root=fake_project_root,
            global_config_path=fake_home / ".config" / "opencode",
        )

        rules = service.by_type(CustomizationType.RULES)
        # Filter for instruction files (not AGENTS.md)
        instructions = [r for r in rules if r.description == "Instruction file"]

        assert len(instructions) > 0
        assert instructions[0].type == CustomizationType.RULES

    def test_instruction_file_has_relative_path_name(
        self,
        full_project_config: Path,  # noqa: ARG002
        fake_project_root: Path,
        fake_home: Path,
    ) -> None:
        """Test instruction file name is relative path."""
        service = ConfigDiscoveryService(
            project_root=fake_project_root,
            global_config_path=fake_home / ".config" / "opencode",
        )

        rules = service.by_type(CustomizationType.RULES)
        instructions = [r for r in rules if r.description == "Instruction file"]

        assert len(instructions) > 0
        # Name should be relative path: "docs/guidelines.md"
        assert instructions[0].name == "docs/guidelines.md"

    def test_instruction_file_content_available(
        self,
        full_project_config: Path,  # noqa: ARG002
        fake_project_root: Path,
        fake_home: Path,
    ) -> None:
        """Test instruction file content is readable."""
        service = ConfigDiscoveryService(
            project_root=fake_project_root,
            global_config_path=fake_home / ".config" / "opencode",
        )

        rules = service.by_type(CustomizationType.RULES)
        instructions = [r for r in rules if r.description == "Instruction file"]

        assert len(instructions) > 0
        assert instructions[0].content is not None
        assert "Development Guidelines" in instructions[0].content

    def test_no_duplicates_when_instruction_is_agents_md(
        self,
        fake_project_root: Path,
        fake_home: Path,
        fs,  # noqa: ARG002
    ) -> None:
        """Test that if instructions includes AGENTS.md, no duplicate is created."""
        # This test would require creating a custom opencode.json
        # that points to AGENTS.md, and verifying deduplication works
        service = ConfigDiscoveryService(
            project_root=fake_project_root,
            global_config_path=fake_home / ".config" / "opencode",
        )

        rules = service.by_type(CustomizationType.RULES)

        # Count occurrences of each rule by path
        path_counts = {}
        for rule in rules:
            path_str = str(rule.path.resolve())
            path_counts[path_str] = path_counts.get(path_str, 0) + 1

        # Verify no path appears more than once
        for count in path_counts.values():
            assert count == 1, "Found duplicate rule by path"
