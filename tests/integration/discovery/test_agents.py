"""Tests for agent discovery."""

from pathlib import Path

from lazyopencode.models.customization import ConfigLevel, CustomizationType
from lazyopencode.services.discovery import ConfigDiscoveryService


class TestAgentDiscovery:
    """Tests for agent discovery."""

    def test_discovers_global_agents(
        self,
        user_config_path: Path,  # noqa: ARG002
        fake_project_root: Path,
        fake_home: Path,
    ) -> None:
        """Test discovering agents from global config."""
        service = ConfigDiscoveryService(
            project_root=fake_project_root,
            global_config_path=fake_home / ".config" / "opencode",
        )

        agents = service.by_type(CustomizationType.AGENT)
        global_agents = [a for a in agents if a.level == ConfigLevel.GLOBAL]

        assert len(global_agents) == 1
        assert global_agents[0].name == "explorer"

    def test_discovers_project_agents(
        self,
        project_config_path: Path,  # noqa: ARG002
        fake_project_root: Path,
        fake_home: Path,
    ) -> None:
        """Test discovering agents from project config."""
        service = ConfigDiscoveryService(
            project_root=fake_project_root,
            global_config_path=fake_home / ".config" / "opencode",
        )

        agents = service.by_type(CustomizationType.AGENT)
        project_agents = [a for a in agents if a.level == ConfigLevel.PROJECT]

        assert len(project_agents) == 1
        assert project_agents[0].name == "reviewer"

    def test_agent_metadata_parsed(
        self,
        user_config_path: Path,  # noqa: ARG002
        fake_project_root: Path,
        fake_home: Path,
    ) -> None:
        """Test agent metadata is correctly parsed."""
        service = ConfigDiscoveryService(
            project_root=fake_project_root,
            global_config_path=fake_home / ".config" / "opencode",
        )

        agents = service.by_type(CustomizationType.AGENT)
        explorer = next(a for a in agents if a.name == "explorer")

        assert explorer.description == "Explores the codebase structure"
        assert explorer.metadata.get("model") == "haiku"
        assert explorer.metadata.get("tools") is not None

    def test_agent_content_available(
        self,
        user_config_path: Path,  # noqa: ARG002
        fake_project_root: Path,
        fake_home: Path,
    ) -> None:
        """Test agent content is available."""
        service = ConfigDiscoveryService(
            project_root=fake_project_root,
            global_config_path=fake_home / ".config" / "opencode",
        )

        agents = service.by_type(CustomizationType.AGENT)
        explorer = next(a for a in agents if a.name == "explorer")

        assert explorer.content is not None
        assert "---" in explorer.content  # Has frontmatter
        assert (
            "Explorer Agent" in explorer.content
            or "explorer" in explorer.content.lower()
        )

    def test_all_agents_discovered(
        self,
        full_user_config: Path,  # noqa: ARG002
        project_config_path: Path,  # noqa: ARG002
        fake_project_root: Path,
        fake_home: Path,
    ) -> None:
        """Test all agents are discovered from both levels."""
        service = ConfigDiscoveryService(
            project_root=fake_project_root,
            global_config_path=fake_home / ".config" / "opencode",
        )

        agents = service.by_type(CustomizationType.AGENT)

        assert len(agents) == 2
        names = {a.name for a in agents}
        assert "explorer" in names
        assert "reviewer" in names

    def test_project_agent_description_parsed(
        self,
        project_config_path: Path,  # noqa: ARG002
        fake_project_root: Path,
        fake_home: Path,
    ) -> None:
        """Test project agent description is parsed correctly."""
        service = ConfigDiscoveryService(
            project_root=fake_project_root,
            global_config_path=fake_home / ".config" / "opencode",
        )

        agents = service.by_type(CustomizationType.AGENT)
        reviewer = next(a for a in agents if a.name == "reviewer")

        assert reviewer.description == "Code review agent"
        assert reviewer.metadata.get("tools") is not None
        assert reviewer.metadata.get("model") == "opus"
