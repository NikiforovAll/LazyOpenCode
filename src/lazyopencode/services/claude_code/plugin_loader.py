"""Plugin loading and registry management for Claude Code plugins."""

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass
class PluginInstallation:
    """Single installation of a plugin (user or project-scoped)."""

    scope: str
    install_path: str
    version: str
    is_local: bool = False
    project_path: str | None = None


@dataclass
class PluginInfo:
    """Information about an installed Claude Code plugin."""

    plugin_id: str
    short_name: str
    version: str
    install_path: Path
    is_local: bool = False
    scope: str = "user"
    project_path: Path | None = None


@dataclass
class PluginRegistry:
    """Container for installed plugin information."""

    installed: dict[str, list[PluginInstallation]]


class PluginLoader:
    """Loads plugin configuration from the Claude Code filesystem."""

    def __init__(
        self,
        user_config_path: Path,
        project_root: Path | None = None,
    ) -> None:
        self.user_config_path = user_config_path
        self.project_root = project_root
        self._registry: PluginRegistry | None = None

    def load_registry(self) -> PluginRegistry:
        """Load installed plugins from configuration files."""
        if self._registry is not None:
            return self._registry

        v2_file = self.user_config_path / "plugins" / "installed_plugins.json"
        installed = self._load_v2_plugins(v2_file) if v2_file.is_file() else {}

        self._registry = PluginRegistry(installed=installed)
        return self._registry

    def _load_v2_plugins(self, path: Path) -> dict[str, list[PluginInstallation]]:
        """Parse V2 format where plugins value is a list."""
        if not path.is_file():
            return {}
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            plugins_data = data.get("plugins", {})
            result: dict[str, list[PluginInstallation]] = {}

            for plugin_id, installations in plugins_data.items():
                result[plugin_id] = [
                    PluginInstallation(
                        scope=inst.get("scope", "user"),
                        install_path=inst.get("installPath", ""),
                        version=inst.get("version", "unknown"),
                        is_local=inst.get("isLocal", False),
                        project_path=inst.get("projectPath"),
                    )
                    for inst in installations
                ]
            return result
        except (json.JSONDecodeError, OSError):
            return {}

    def get_all_plugins(self) -> list[PluginInfo]:
        """Get list of ALL plugin infos with resolved install paths."""
        registry = self.load_registry()
        plugins: list[PluginInfo] = []

        for plugin_id, installations in registry.installed.items():
            for installation in installations:
                if (
                    installation.scope == "user"
                    or installation.scope == "project"
                    and self._matches_current_project(installation.project_path)
                ):
                    plugin_info = self._create_plugin_info(plugin_id, installation)
                    if plugin_info and plugin_info.install_path.is_dir():
                        plugins.append(plugin_info)

        return plugins

    def _matches_current_project(self, project_path: str | None) -> bool:
        """Check if project_path matches current project root."""
        if not project_path or not self.project_root:
            return False
        try:
            return Path(project_path).resolve() == self.project_root.resolve()
        except OSError:
            return False

    def refresh(self) -> None:
        """Clear cached registry to force reload."""
        self._registry = None

    def _create_plugin_info(
        self,
        plugin_id: str,
        installation: PluginInstallation,
    ) -> PluginInfo | None:
        """Create PluginInfo from installation data."""
        if not installation.install_path:
            return None

        short_name = plugin_id.split("@")[0] if "@" in plugin_id else plugin_id
        install_path = Path(installation.install_path)
        version = installation.version

        if not install_path.is_dir() and install_path.parent.is_dir():
            install_path = self._find_latest_version_dir(install_path.parent)
            version = install_path.name

        project_path = (
            Path(installation.project_path) if installation.project_path else None
        )

        return PluginInfo(
            plugin_id=plugin_id,
            short_name=short_name,
            version=version,
            install_path=install_path,
            is_local=installation.is_local,
            scope=installation.scope,
            project_path=project_path,
        )

    def _find_latest_version_dir(self, parent_dir: Path) -> Path:
        """Find the latest version directory in a plugin parent directory."""
        try:
            subdirs = [d for d in parent_dir.iterdir() if d.is_dir()]
            if subdirs:
                return max(subdirs, key=lambda d: self._parse_version(d.name))
        except OSError:
            pass
        return parent_dir

    @staticmethod
    def _parse_version(version_str: str) -> tuple[int, ...] | tuple[str]:
        """Parse version string into comparable tuple."""
        try:
            return tuple(int(part) for part in version_str.split("."))
        except ValueError:
            return (version_str,)
