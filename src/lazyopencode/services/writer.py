"""Service for writing customizations to OpenCode directories."""

import shutil
from pathlib import Path

from lazyopencode.models.customization import (
    ConfigLevel,
    Customization,
    CustomizationType,
)


class CustomizationWriter:
    """Writes customizations to OpenCode configuration directories."""

    def __init__(
        self,
        global_config_path: Path,
        project_config_path: Path,
    ) -> None:
        """Initialize writer with config paths."""
        self.global_config_path = global_config_path
        self.project_config_path = project_config_path

    def copy_customization(
        self,
        customization: Customization,
        target_level: ConfigLevel,
    ) -> tuple[bool, str]:
        """
        Copy customization to target level.

        Args:
            customization: The customization to copy
            target_level: Target configuration level (GLOBAL or PROJECT)

        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            base_path = self._get_target_base_path(target_level)
            target_path = self._build_target_path(customization, base_path)

            if self._check_conflict(customization, target_path):
                return (
                    False,
                    f"{customization.type_label} '{customization.name}' already exists at {target_level.label} level",
                )

            self._ensure_parent_dirs(target_path)

            if customization.type == CustomizationType.SKILL:
                self._copy_skill_directory(customization.path.parent, target_path)
            else:
                self._write_file(customization.path, target_path)

            return (
                True,
                f"Copied '{customization.name}' to {target_level.label} level",
            )

        except PermissionError as e:
            return (False, f"Permission denied writing to {e.filename}")
        except OSError as e:
            return (False, f"Failed to copy '{customization.name}': {e}")

    def _get_target_base_path(self, level: ConfigLevel) -> Path:
        """Get base path for target configuration level."""
        if level == ConfigLevel.GLOBAL:
            return self.global_config_path
        elif level == ConfigLevel.PROJECT:
            return self.project_config_path
        else:
            raise ValueError(f"Unsupported target level: {level}")

    def _build_target_path(self, customization: Customization, base_path: Path) -> Path:
        """Construct target file path based on customization type."""
        if customization.type == CustomizationType.COMMAND:
            # Handle nested commands (name:subname -> command/name/subname.md)
            parts = customization.name.split(":")
            if len(parts) > 1:
                nested_path = Path(*parts[:-1])
                filename = f"{parts[-1]}.md"
                return base_path / "command" / nested_path / filename
            else:
                return base_path / "command" / f"{customization.name}.md"

        elif customization.type == CustomizationType.AGENT:
            return base_path / "agent" / f"{customization.name}.md"

        elif customization.type == CustomizationType.SKILL:
            return base_path / "skill" / customization.name

        else:
            raise ValueError(f"Unsupported customization type: {customization.type}")

    def _check_conflict(self, customization: Customization, target_path: Path) -> bool:
        """Check if target file or directory already exists."""
        if customization.type == CustomizationType.SKILL:
            return target_path.exists() and target_path.is_dir()
        else:
            return target_path.exists() and target_path.is_file()

    def _ensure_parent_dirs(self, target_path: Path) -> None:
        """Create parent directories if they don't exist."""
        target_path.parent.mkdir(parents=True, exist_ok=True)

    def _write_file(self, source_path: Path, target_path: Path) -> None:
        """Copy file from source to target."""
        content = source_path.read_text(encoding="utf-8")
        target_path.write_text(content, encoding="utf-8")

    def _copy_skill_directory(self, source_dir: Path, target_dir: Path) -> None:
        """Copy entire skill directory tree."""
        shutil.copytree(
            source_dir,
            target_dir,
            dirs_exist_ok=False,
        )
