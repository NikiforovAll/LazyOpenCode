"""Tests for skill discovery."""

from pathlib import Path

from lazyopencode.models.customization import ConfigLevel, CustomizationType
from lazyopencode.services.discovery import ConfigDiscoveryService


class TestSkillDiscovery:
    """Tests for skill discovery."""

    def test_discovers_global_skills(
        self,
        user_config_path: Path,  # noqa: ARG002
        fake_project_root: Path,
        fake_home: Path,
    ) -> None:
        """Test discovering skills from global config."""
        service = ConfigDiscoveryService(
            project_root=fake_project_root,
            global_config_path=fake_home / ".config" / "opencode",
        )

        skills = service.by_type(CustomizationType.SKILL)
        global_skills = [s for s in skills if s.level == ConfigLevel.GLOBAL]

        assert len(global_skills) == 1
        assert global_skills[0].name == "task-tracker"

    def test_discovers_project_skills(
        self,
        project_config_path: Path,  # noqa: ARG002
        fake_project_root: Path,
        fake_home: Path,
    ) -> None:
        """Test discovering skills from project config."""
        service = ConfigDiscoveryService(
            project_root=fake_project_root,
            global_config_path=fake_home / ".config" / "opencode",
        )

        skills = service.by_type(CustomizationType.SKILL)
        project_skills = [s for s in skills if s.level == ConfigLevel.PROJECT]

        assert len(project_skills) == 1
        assert project_skills[0].name == "project-skill"

    def test_skill_uses_directory_name(
        self,
        user_config_path: Path,  # noqa: ARG002
        fake_project_root: Path,
        fake_home: Path,
    ) -> None:
        """Test skill name comes from directory name, not filename."""
        service = ConfigDiscoveryService(
            project_root=fake_project_root,
            global_config_path=fake_home / ".config" / "opencode",
        )

        skills = service.by_type(CustomizationType.SKILL)
        task_tracker = next(s for s in skills if s.name == "task-tracker")

        # Name should be "task-tracker" (from directory), not "SKILL"
        assert task_tracker.name == "task-tracker"
        assert task_tracker.description == "Track and manage development tasks"

    def test_skill_content_available(
        self,
        user_config_path: Path,  # noqa: ARG002
        fake_project_root: Path,
        fake_home: Path,
    ) -> None:
        """Test skill content is available."""
        service = ConfigDiscoveryService(
            project_root=fake_project_root,
            global_config_path=fake_home / ".config" / "opencode",
        )

        skills = service.by_type(CustomizationType.SKILL)
        task_tracker = next(s for s in skills if s.name == "task-tracker")

        assert task_tracker.content is not None
        assert "---" in task_tracker.content  # Has frontmatter
        assert (
            "Task Tracker Skill" in task_tracker.content
            or "task" in task_tracker.content.lower()
        )

    def test_all_skills_discovered(
        self,
        full_user_config: Path,  # noqa: ARG002
        project_config_path: Path,  # noqa: ARG002
        fake_project_root: Path,
        fake_home: Path,
    ) -> None:
        """Test all skills are discovered from both levels."""
        service = ConfigDiscoveryService(
            project_root=fake_project_root,
            global_config_path=fake_home / ".config" / "opencode",
        )

        skills = service.by_type(CustomizationType.SKILL)

        assert len(skills) == 2
        names = {s.name for s in skills}
        assert "task-tracker" in names
        assert "project-skill" in names

    def test_project_skill_metadata_parsed(
        self,
        project_config_path: Path,  # noqa: ARG002
        fake_project_root: Path,
        fake_home: Path,
    ) -> None:
        """Test project skill metadata is parsed correctly."""
        service = ConfigDiscoveryService(
            project_root=fake_project_root,
            global_config_path=fake_home / ".config" / "opencode",
        )

        skills = service.by_type(CustomizationType.SKILL)
        project_skill = next(s for s in skills if s.name == "project-skill")

        assert project_skill.description == "Project-specific skill"
        assert project_skill.level == ConfigLevel.PROJECT

    def test_skill_files_parsed(
        self,
        user_config_path: Path,  # noqa: ARG002
        fake_project_root: Path,
        fake_home: Path,
    ) -> None:
        """Test skill files list is populated with SkillFile objects."""
        service = ConfigDiscoveryService(
            project_root=fake_project_root,
            global_config_path=fake_home / ".config" / "opencode",
        )

        skills = service.by_type(CustomizationType.SKILL)
        task_tracker = next(s for s in skills if s.name == "task-tracker")

        files = task_tracker.metadata.get("files", [])
        assert len(files) > 0
        # Check that we have reference.md and scripts directory
        file_names = {f.name for f in files}
        assert "reference.md" in file_names
        assert "scripts" in file_names

    def test_skill_nested_directory_structure(
        self,
        project_config_path: Path,  # noqa: ARG002
        fake_project_root: Path,
        fake_home: Path,
    ) -> None:
        """Test nested directories and their children are parsed."""
        service = ConfigDiscoveryService(
            project_root=fake_project_root,
            global_config_path=fake_home / ".config" / "opencode",
        )

        skills = service.by_type(CustomizationType.SKILL)
        project_skill = next(s for s in skills if s.name == "project-skill")

        files = project_skill.metadata.get("files", [])
        # Find the src directory
        src_dir = next((f for f in files if f.name == "src"), None)
        assert src_dir is not None
        assert src_dir.is_directory
        # Check children
        assert len(src_dir.children) > 0
        child_names = {c.name for c in src_dir.children}
        assert "helper.py" in child_names
