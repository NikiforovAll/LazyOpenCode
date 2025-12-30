"""Shared pytest fixtures for LazyOpenCode tests."""

import os
from collections.abc import Generator
from pathlib import Path
from unittest.mock import patch

import pytest
from pyfakefs.fake_filesystem import FakeFilesystem

FIXTURES_DIR = Path(__file__).parent / "integration" / "fixtures"
FAKE_HOME = Path("/fake/home")


@pytest.fixture
def _fs(fs: FakeFilesystem) -> FakeFilesystem:
    """Alias for fs fixture when pyfakefs is needed but not explicitly used."""
    return fs


@pytest.fixture
def fake_home(fs: FakeFilesystem) -> Generator[Path, None, None]:
    """Create a fake home directory and patch Path.home() to return it."""
    fs.create_dir(FAKE_HOME)
    os.environ["HOME"] = str(FAKE_HOME)
    os.environ["USERPROFILE"] = str(FAKE_HOME)

    with patch.object(Path, "home", return_value=FAKE_HOME):
        yield FAKE_HOME


@pytest.fixture
def fake_project_root(fs: FakeFilesystem) -> Path:
    """Create a fake project root directory."""
    project = Path("/fake/project")
    fs.create_dir(project)
    return project


@pytest.fixture
def user_config_path(fake_home: Path, fs: FakeFilesystem) -> Path:
    """Create user config directory (~/.config/opencode) with fixtures."""
    user_opencode = fake_home / ".config" / "opencode"
    if not fs.exists(user_opencode):
        fs.create_dir(user_opencode)

    # Add command fixtures
    fs.add_real_directory(
        FIXTURES_DIR / "command",
        target_path=user_opencode / "command",
        read_only=False,
    )

    # Add agent fixtures
    fs.add_real_directory(
        FIXTURES_DIR / "agent",
        target_path=user_opencode / "agent",
        read_only=False,
    )

    # Add skill fixtures
    fs.add_real_directory(
        FIXTURES_DIR / "skill",
        target_path=user_opencode / "skill",
        read_only=False,
    )

    # Add AGENTS.md to global config
    fs.add_real_file(
        FIXTURES_DIR / "memory" / "AGENTS.md",
        target_path=user_opencode / "AGENTS.md",
        read_only=False,
    )

    return user_opencode


@pytest.fixture
def user_mcp_config(fake_home: Path, fs: FakeFilesystem) -> Path:
    """Create user-level MCP config (~/.config/opencode/opencode.json)."""
    config_dir = fake_home / ".config" / "opencode"
    if not fs.exists(config_dir):
        fs.create_dir(config_dir)
    mcp_path = config_dir / "opencode.json"
    fs.add_real_file(
        FIXTURES_DIR / "mcp" / "user-opencode.json",
        target_path=mcp_path,
        read_only=False,
    )
    return mcp_path


@pytest.fixture
def project_mcp_config(fake_project_root: Path, fs: FakeFilesystem) -> Path:
    """Create project-level MCP config (opencode.json at project root)."""
    mcp_path = fake_project_root / "opencode.json"
    fs.add_real_file(
        FIXTURES_DIR / "mcp" / "project-opencode.json",
        target_path=mcp_path,
        read_only=False,
    )
    return mcp_path


@pytest.fixture
def project_config_path(fake_project_root: Path, fs: FakeFilesystem) -> Path:
    """Create project config directory (./.opencode) with fixtures."""
    project_opencode = fake_project_root / ".opencode"
    fs.create_dir(project_opencode)

    # Add command fixtures
    fs.add_real_directory(
        FIXTURES_DIR / "project" / "command",
        target_path=project_opencode / "command",
        read_only=False,
    )

    # Add agent fixtures
    fs.add_real_directory(
        FIXTURES_DIR / "project" / "agent",
        target_path=project_opencode / "agent",
        read_only=False,
    )

    # Add skill fixtures
    fs.add_real_directory(
        FIXTURES_DIR / "project" / "skill",
        target_path=project_opencode / "skill",
        read_only=False,
    )

    # Add AGENTS.md at project root (not in .opencode)
    fs.add_real_file(
        FIXTURES_DIR / "project" / "AGENTS.md",
        target_path=fake_project_root / "AGENTS.md",
        read_only=False,
    )

    # Add docs directory with instruction files
    fs.add_real_directory(
        FIXTURES_DIR / "project" / "docs",
        target_path=fake_project_root / "docs",
        read_only=False,
    )

    return project_opencode


@pytest.fixture
def full_user_config(
    user_config_path: Path,
    user_mcp_config: Path,  # noqa: ARG001
) -> Path:
    """Complete user configuration with all customization types."""
    return user_config_path


@pytest.fixture
def full_project_config(
    project_config_path: Path,
    project_mcp_config: Path,  # noqa: ARG001
) -> Path:
    """Complete project configuration."""
    return project_config_path
