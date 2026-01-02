"""Main LazyOpenCode TUI Application."""

import os
import shlex
import subprocess
import sys
from pathlib import Path

from textual.app import App, ComposeResult
from textual.containers import Container

from lazyopencode import __version__
from lazyopencode.bindings import APP_BINDINGS
from lazyopencode.mixins.filtering import FilteringMixin
from lazyopencode.mixins.help import HelpMixin
from lazyopencode.mixins.navigation import NavigationMixin
from lazyopencode.models.customization import (
    ConfigLevel,
    Customization,
    CustomizationType,
)
from lazyopencode.services.discovery import ConfigDiscoveryService
from lazyopencode.themes import CUSTOM_THEMES
from lazyopencode.widgets.app_footer import AppFooter
from lazyopencode.widgets.combined_panel import CombinedPanel
from lazyopencode.widgets.detail_pane import MainPane
from lazyopencode.widgets.filter_input import FilterInput
from lazyopencode.widgets.status_panel import StatusPanel
from lazyopencode.widgets.type_panel import TypePanel


class LazyOpenCode(App, NavigationMixin, FilteringMixin, HelpMixin):
    """A lazygit-style TUI for visualizing OpenCode customizations."""

    CSS_PATH = "styles/app.tcss"
    LAYERS = ["default", "overlay"]
    BINDINGS = APP_BINDINGS

    TITLE = f"LazyOpenCode v{__version__}"
    SUB_TITLE = ""

    def __init__(
        self,
        discovery_service: ConfigDiscoveryService | None = None,
        project_root: Path | None = None,
        global_config_path: Path | None = None,
    ) -> None:
        """Initialize LazyOpenCode application."""
        super().__init__()
        self.theme = "gruvbox"
        self._discovery_service = discovery_service or ConfigDiscoveryService(
            project_root=project_root,
            global_config_path=global_config_path,
        )
        self._customizations: list[Customization] = []
        self._level_filter: ConfigLevel | None = None
        self._search_query: str = ""
        self._panels: list[TypePanel | CombinedPanel] = []
        self._status_panel: StatusPanel | None = None
        self._main_pane: MainPane | None = None
        self._filter_input: FilterInput | None = None
        self._app_footer: AppFooter | None = None
        self._last_focused_panel: TypePanel | CombinedPanel | None = None

    def compose(self) -> ComposeResult:
        """Compose the application layout."""
        with Container(id="sidebar"):
            self._status_panel = StatusPanel(id="status-panel")
            yield self._status_panel

            # [1]+[2] Combined Panel: Commands, Agents
            cp1 = CombinedPanel(
                tabs=[
                    (CustomizationType.COMMAND, 1, "Commands"),
                    (CustomizationType.AGENT, 2, "Agents"),
                ],
                id="panel-combined-1",
            )
            self._panels.append(cp1)
            yield cp1

            # [3] Type Panel: Skills
            tp_skills = TypePanel(CustomizationType.SKILL, id="panel-skill")
            tp_skills.panel_number = 3
            self._panels.append(tp_skills)
            yield tp_skills

            # [4] Type Panel: Agent Memory (Rules)
            tp_rules = TypePanel(CustomizationType.RULES, id="panel-rules")
            tp_rules.panel_number = 4
            self._panels.append(tp_rules)
            yield tp_rules

            # [5]+[6]+[7] Combined Panel: MCPs, Tools, Plugins
            cp2 = CombinedPanel(
                tabs=[
                    (CustomizationType.MCP, 5, "MCPs"),
                    (CustomizationType.TOOL, 6, "Tools"),
                    (CustomizationType.PLUGIN, 7, "Plugins"),
                ],
                id="panel-combined-2",
            )
            self._panels.append(cp2)
            yield cp2

        self._main_pane = MainPane(id="main-pane")
        yield self._main_pane

        self._filter_input = FilterInput(id="filter-input")
        yield self._filter_input

        self._app_footer = AppFooter(id="app-footer")
        yield self._app_footer

    def on_mount(self) -> None:
        """Handle mount event - load customizations."""
        for theme in CUSTOM_THEMES:
            self.register_theme(theme)

        self._load_customizations()
        self._update_status_panel()
        project_name = self._discovery_service.project_root.name
        self.title = f"{project_name} - LazyOpenCode"
        self.console.set_window_title(self.title)
        if os.name == "nt":
            os.system(f"title {self.title}")
        # Focus first non-empty panel or first panel
        if self._panels:
            self._panels[0].focus()

    def _update_status_panel(self) -> None:
        """Update status panel with current config path and filter level."""
        filter_label = self._level_filter.label if self._level_filter else "All"

        if self._status_panel:
            project_name = self._discovery_service.project_root.name
            self._status_panel.config_path = project_name
            self._status_panel.filter_level = filter_label

        if self._app_footer:
            self._app_footer.filter_level = filter_label
            # Also update search active status
            self._app_footer.search_active = bool(self._search_query)

    def _load_customizations(self) -> None:
        """Load customizations from discovery service."""
        self._customizations = self._discovery_service.discover_all()
        self._update_panels()

    def _update_panels(self) -> None:
        """Update all panels with filtered customizations."""
        customizations = self._get_filtered_customizations()
        for panel in self._panels:
            panel.set_customizations(customizations)

    def _get_filtered_customizations(self) -> list[Customization]:
        """Get customizations filtered by current level and search query."""
        result = self._customizations
        if self._level_filter:
            result = [c for c in result if c.level == self._level_filter]
        if self._search_query:
            query = self._search_query.lower()
            result = [c for c in result if query in c.name.lower()]
        return result

    # Panel selection message handlers

    def on_type_panel_selection_changed(
        self, message: TypePanel.SelectionChanged
    ) -> None:
        """Handle selection change in a type panel."""
        if self._main_pane:
            self._main_pane.customization = message.customization

    def on_type_panel_drill_down(self, message: TypePanel.DrillDown) -> None:
        """Handle drill down into a customization."""
        if self._main_pane:
            self._last_focused_panel = self._get_focused_panel()
            self._main_pane.customization = message.customization
            self._main_pane.focus()

    def on_type_panel_skill_file_selected(
        self, message: TypePanel.SkillFileSelected
    ) -> None:
        """Handle skill file selection in the skills tree."""
        if self._main_pane:
            self._main_pane.selected_file = message.file_path

    def on_combined_panel_selection_changed(
        self, message: CombinedPanel.SelectionChanged
    ) -> None:
        """Handle selection change in the combined panel."""
        if self._main_pane:
            self._main_pane.customization = message.customization

    def on_combined_panel_drill_down(self, message: CombinedPanel.DrillDown) -> None:
        """Handle drill down from the combined panel."""
        if self._main_pane:
            self._last_focused_panel = self._get_focused_panel()
            self._main_pane.customization = message.customization
            self._main_pane.focus()

    # Filter input message handlers

    def on_filter_input_filter_changed(
        self, message: FilterInput.FilterChanged
    ) -> None:
        """Handle filter query changes (real-time filtering)."""
        self._search_query = message.query
        self._last_focused_panel = None
        if self._main_pane:
            self._main_pane.customization = None
        self._update_status_panel()  # Updates footer search active state
        self._update_panels()

    def on_filter_input_filter_cancelled(
        self,
        message: FilterInput.FilterCancelled,  # noqa: ARG002
    ) -> None:
        """Handle filter cancellation."""
        self._search_query = ""
        self._last_focused_panel = None
        if self._main_pane:
            self._main_pane.customization = None
        self._update_status_panel()
        self._update_panels()
        # Restore focus
        if self._panels:
            self._panels[0].focus()

    def on_filter_input_filter_applied(
        self,
        message: FilterInput.FilterApplied,  # noqa: ARG002
    ) -> None:
        """Handle filter application (Enter key)."""
        if self._filter_input:
            self._filter_input.hide()
        # Restore focus
        if self._panels:
            self._panels[0].focus()

    # Navigation actions (handled by NavigationMixin)

    # Filter actions (handled by FilteringMixin)

    def action_search(self) -> None:
        """Activate search."""
        if self._filter_input:
            if self._filter_input.is_visible:
                self._filter_input.hide()
            else:
                self._filter_input.show()

    # Other actions

    def action_refresh(self) -> None:
        """Refresh customizations from disk."""
        self._discovery_service.refresh()
        self._load_customizations()
        self.notify("Refreshed", severity="information")

    # action_toggle_help handled by HelpMixin

    def action_open_in_editor(self) -> None:
        """Open currently selected customization in editor."""
        panel = self._get_focused_panel()
        customization = None

        if panel:
            customization = panel.selected_customization

        if not customization:
            self.notify("No customization selected", severity="warning")
            return

        file_path = customization.path
        if customization.type == CustomizationType.SKILL:
            file_path = customization.path.parent

        if file_path and file_path.exists():
            self._open_path_in_editor(file_path)
        else:
            self.notify("File does not exist", severity="error")

    def action_open_user_config(self) -> None:
        """Open user configuration in editor."""
        config_path = self._discovery_service.global_config_path / "opencode.json"
        if not config_path.exists():
            # Fallback to the directory if file doesn't exist
            config_path = self._discovery_service.global_config_path

        self._open_path_in_editor(config_path)

    def _open_path_in_editor(self, path: Path) -> None:
        """Helper to open a path in the system editor."""
        editor = os.environ.get("EDITOR", "vi")
        try:
            cmd = shlex.split(editor) + [str(path)]
            subprocess.Popen(cmd, shell=(sys.platform == "win32"))
        except Exception as e:
            self.notify(f"Error opening editor: {e}", severity="error")


def create_app(
    project_root: Path | None = None,
    global_config_path: Path | None = None,
) -> LazyOpenCode:
    """Create application with all dependencies wired."""
    discovery_service = ConfigDiscoveryService(
        project_root=project_root,
        global_config_path=global_config_path,
    )
    return LazyOpenCode(discovery_service=discovery_service)
