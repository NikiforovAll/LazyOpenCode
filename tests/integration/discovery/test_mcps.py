"""Tests for MCP discovery."""

from pathlib import Path

from lazyopencode.models.customization import ConfigLevel, CustomizationType
from lazyopencode.services.discovery import ConfigDiscoveryService


class TestMCPDiscovery:
    """Tests for MCP discovery."""

    def test_discovers_global_mcps(
        self,
        user_mcp_config: Path,  # noqa: ARG002
        fake_project_root: Path,
        fake_home: Path,
    ) -> None:
        """Test discovering MCPs from global config."""
        service = ConfigDiscoveryService(
            project_root=fake_project_root,
            global_config_path=fake_home / ".config" / "opencode",
        )

        mcps = service.by_type(CustomizationType.MCP)
        global_mcps = [m for m in mcps if m.level == ConfigLevel.GLOBAL]

        assert len(global_mcps) == 1
        assert global_mcps[0].name == "test-server"

    def test_discovers_project_mcps(
        self,
        project_mcp_config: Path,  # noqa: ARG002
        fake_project_root: Path,
        fake_home: Path,
    ) -> None:
        """Test discovering MCPs from project config."""
        service = ConfigDiscoveryService(
            project_root=fake_project_root,
            global_config_path=fake_home / ".config" / "opencode",
        )

        mcps = service.by_type(CustomizationType.MCP)
        project_mcps = [m for m in mcps if m.level == ConfigLevel.PROJECT]

        assert len(project_mcps) == 1
        assert project_mcps[0].name == "project-server"

    def test_mcp_metadata_parsed(
        self,
        user_mcp_config: Path,  # noqa: ARG002
        fake_project_root: Path,
        fake_home: Path,
    ) -> None:
        """Test MCP metadata is correctly parsed."""
        service = ConfigDiscoveryService(
            project_root=fake_project_root,
            global_config_path=fake_home / ".config" / "opencode",
        )

        mcps = service.by_type(CustomizationType.MCP)
        test_server = next(m for m in mcps if m.name == "test-server")

        assert test_server.metadata.get("command") == "node"
        assert test_server.metadata.get("args") is not None

    def test_mcp_content_available(
        self,
        user_mcp_config: Path,  # noqa: ARG002
        fake_project_root: Path,
        fake_home: Path,
    ) -> None:
        """Test MCP content is available."""
        service = ConfigDiscoveryService(
            project_root=fake_project_root,
            global_config_path=fake_home / ".config" / "opencode",
        )

        mcps = service.by_type(CustomizationType.MCP)
        test_server = next(m for m in mcps if m.name == "test-server")

        assert test_server.content is not None
        assert len(test_server.content) > 0

    def test_all_mcps_discovered(
        self,
        user_mcp_config: Path,  # noqa: ARG002
        project_mcp_config: Path,  # noqa: ARG002
        fake_project_root: Path,
        fake_home: Path,
    ) -> None:
        """Test all MCPs are discovered from both levels."""
        service = ConfigDiscoveryService(
            project_root=fake_project_root,
            global_config_path=fake_home / ".config" / "opencode",
        )

        mcps = service.by_type(CustomizationType.MCP)

        assert len(mcps) == 2
        names = {m.name for m in mcps}
        assert "test-server" in names
        assert "project-server" in names

    def test_project_mcp_metadata(
        self,
        project_mcp_config: Path,  # noqa: ARG002
        fake_project_root: Path,
        fake_home: Path,
    ) -> None:
        """Test project MCP metadata is parsed correctly."""
        service = ConfigDiscoveryService(
            project_root=fake_project_root,
            global_config_path=fake_home / ".config" / "opencode",
        )

        mcps = service.by_type(CustomizationType.MCP)
        project_server = next(m for m in mcps if m.name == "project-server")

        assert project_server.metadata.get("command") == "python"
        assert project_server.metadata.get("args") == ["-m", "server"]
        assert project_server.level == ConfigLevel.PROJECT
