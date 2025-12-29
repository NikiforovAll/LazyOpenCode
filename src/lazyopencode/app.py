"""Main LazyOpenCode TUI Application."""

from pathlib import Path

from textual.app import App, ComposeResult
from textual.containers import Container

from lazyopencode import __version__
from lazyopencode.bindings import APP_BINDINGS
from lazyopencode.models.customization import (
    ConfigLevel,
    Customization,
    CustomizationType,
)
from lazyopencode.services.discovery import ConfigDiscoveryService
from lazyopencode.widgets.app_footer import AppFooter
from lazyopencode.widgets.combined_panel import CombinedPanel
from lazyopencode.widgets.detail_pane import MainPane
from lazyopencode.widgets.status_panel import StatusPanel
from lazyopencode.widgets.type_panel import TypePanel


class LazyOpenCode(App):
    """A lazygit-style TUI for visualizing OpenCode customizations."""

    CSS_PATH = "styles/app.tcss"
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
        self._discovery_service = discovery_service or ConfigDiscoveryService(
            project_root=project_root,
            global_config_path=global_config_path,
        )
        self._customizations: list[Customization] = []
        self._level_filter: ConfigLevel | None = None
        self._search_query: str = ""
        self._panels: list[TypePanel] = []
        self._combined_panel: CombinedPanel | None = None
        self._status_panel: StatusPanel | None = None
        self._main_pane: MainPane | None = None
        self._app_footer: AppFooter | None = None
        self._last_focused_panel: TypePanel | None = None
        self._last_focused_combined: bool = False

    def compose(self) -> ComposeResult:
        """Compose the application layout."""
        with Container(id="sidebar"):
            self._status_panel = StatusPanel(id="status-panel")
            yield self._status_panel

            # Create panels for Commands, Agents, Skills
            separate_types = [
                CustomizationType.COMMAND,
                CustomizationType.AGENT,
                CustomizationType.SKILL,
            ]
            for i, ctype in enumerate(separate_types, start=1):
                panel = TypePanel(ctype, id=f"panel-{ctype.value}")
                panel.panel_number = i
                self._panels.append(panel)
                yield panel

            # Combined panel for Rules, MCPs, Plugins
            self._combined_panel = CombinedPanel(id="panel-combined")
            yield self._combined_panel

        self._main_pane = MainPane(id="main-pane")
        yield self._main_pane

        self._app_footer = AppFooter(id="app-footer")
        yield self._app_footer

    def on_mount(self) -> None:
        """Handle mount event - load customizations."""
        self._load_customizations()
        self._update_status_panel()
        project_name = self._discovery_service.project_root.name
        self.title = f"{project_name} - LazyOpenCode"
        # Focus first non-empty panel or first panel
        if self._panels:
            self._panels[0].focus()

    def _update_status_panel(self) -> None:
        """Update status panel with current config path and filter level."""
        if self._status_panel:
            project_name = self._discovery_service.project_root.name
            self._status_panel.config_path = project_name
            self._status_panel.filter_level = (
                self._level_filter.label if self._level_filter else "All"
            )

    def _load_customizations(self) -> None:
        """Load customizations from discovery service."""
        self._customizations = self._discovery_service.discover_all()
        self._update_panels()

    def _update_panels(self) -> None:
        """Update all panels with filtered customizations."""
        customizations = self._get_filtered_customizations()
        for panel in self._panels:
            panel.set_customizations(customizations)
        if self._combined_panel:
            self._combined_panel.set_customizations(customizations)

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
            self._last_focused_combined = False
            self._main_pane.customization = message.customization
            self._main_pane.focus()

    def on_combined_panel_selection_changed(
        self, message: CombinedPanel.SelectionChanged
    ) -> None:
        """Handle selection change in the combined panel."""
        if self._main_pane:
            self._main_pane.customization = message.customization

    def on_combined_panel_drill_down(self, message: CombinedPanel.DrillDown) -> None:
        """Handle drill down from the combined panel."""
        if self._main_pane:
            self._last_focused_panel = None
            self._last_focused_combined = True
            self._main_pane.customization = message.customization
            self._main_pane.focus()

    # Navigation actions

    def _get_focused_panel(self) -> TypePanel | None:
        """Get the currently focused TypePanel."""
        for panel in self._panels:
            if panel.has_focus:
                return panel
        return None

    def action_focus_next_panel(self) -> None:
        """Focus the next panel."""
        all_panels = self._panels + (
            [self._combined_panel] if self._combined_panel else []
        )
        current_idx = -1
        for i, panel in enumerate(all_panels):
            if panel and panel.has_focus:
                current_idx = i
                break
        next_idx = (current_idx + 1) % len(all_panels)
        if all_panels[next_idx]:
            all_panels[next_idx].focus()

    def action_focus_previous_panel(self) -> None:
        """Focus the previous panel."""
        all_panels = self._panels + (
            [self._combined_panel] if self._combined_panel else []
        )
        current_idx = 0
        for i, panel in enumerate(all_panels):
            if panel and panel.has_focus:
                current_idx = i
                break
        prev_idx = (current_idx - 1) % len(all_panels)
        if all_panels[prev_idx]:
            all_panels[prev_idx].focus()

    def action_focus_panel_1(self) -> None:
        """Focus Commands panel."""
        if len(self._panels) > 0:
            self._panels[0].focus()

    def action_focus_panel_2(self) -> None:
        """Focus Agents panel."""
        if len(self._panels) > 1:
            self._panels[1].focus()

    def action_focus_panel_3(self) -> None:
        """Focus Skills panel."""
        if len(self._panels) > 2:
            self._panels[2].focus()

    def action_focus_panel_4(self) -> None:
        """Focus Rules tab in combined panel."""
        if self._combined_panel:
            self._combined_panel.switch_to_tab(0)
            self._combined_panel.focus()

    def action_focus_panel_5(self) -> None:
        """Focus MCPs tab in combined panel."""
        if self._combined_panel:
            self._combined_panel.switch_to_tab(1)
            self._combined_panel.focus()

    def action_focus_panel_6(self) -> None:
        """Focus Plugins tab in combined panel."""
        if self._combined_panel:
            self._combined_panel.switch_to_tab(2)
            self._combined_panel.focus()

    def action_focus_main_pane(self) -> None:
        """Focus the main pane."""
        if self._main_pane:
            self._main_pane.focus()

    # Filter actions

    def action_filter_all(self) -> None:
        """Show all customizations."""
        self._level_filter = None
        self._update_status_panel()
        self._update_panels()

    def action_filter_global(self) -> None:
        """Show only global customizations."""
        self._level_filter = ConfigLevel.GLOBAL
        self._update_status_panel()
        self._update_panels()

    def action_filter_project(self) -> None:
        """Show only project customizations."""
        self._level_filter = ConfigLevel.PROJECT
        self._update_status_panel()
        self._update_panels()

    # Other actions

    def action_refresh(self) -> None:
        """Refresh customizations from disk."""
        self._discovery_service.refresh()
        self._load_customizations()
        self.notify("Refreshed", severity="information")

    def action_toggle_help(self) -> None:
        """Show help."""
        self.notify(
            "Keys: q=quit, ?=help, 1-6=panels, j/k=nav, Tab=next, a/g/p=filter",
            timeout=5.0,
        )

    def action_search(self) -> None:
        """Activate search (not implemented)."""
        self.notify("Search not implemented yet", severity="warning")

    def action_open_in_editor(self) -> None:
        """Open in editor (not implemented)."""
        self.notify("Edit not implemented yet", severity="warning")

    def action_prev_view(self) -> None:
        """Switch to previous view in main pane."""
        if self._main_pane:
            self._main_pane.action_prev_view()

    def action_next_view(self) -> None:
        """Switch to next view in main pane."""
        if self._main_pane:
            self._main_pane.action_next_view()


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
