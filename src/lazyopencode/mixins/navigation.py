"""Navigation mixin for handling panel focus and keyboard shortcuts."""

from typing import TYPE_CHECKING, cast

from textual.widget import Widget

if TYPE_CHECKING:
    from lazyopencode.app import LazyOpenCode
    from lazyopencode.widgets.type_panel import TypePanel


class NavigationMixin:
    """Mixin for application navigation."""

    def _get_focused_panel(self) -> "TypePanel | None":
        """Get the currently focused TypePanel."""
        app = cast("LazyOpenCode", self)
        for panel in app._panels:
            if panel.has_focus:
                return panel
        return None

    def action_focus_next_panel(self) -> None:
        """Focus the next panel."""
        app = cast("LazyOpenCode", self)
        all_panels: list[Widget] = []
        all_panels.extend(app._panels)
        if app._combined_panel:
            all_panels.append(app._combined_panel)

        current_idx = -1
        for i, panel in enumerate(all_panels):
            if panel.has_focus:
                current_idx = i
                break

        # If main pane is focused, current_idx stays -1, next will be 0
        if current_idx == -1 and app._main_pane and app._main_pane.has_focus:
            # If main pane has focus, go back to last focused panel or first
            if app._last_focused_panel:
                app._last_focused_panel.focus()
                return
            else:
                current_idx = -1  # Will become 0

        next_idx = (current_idx + 1) % len(all_panels)
        if all_panels[next_idx]:
            all_panels[next_idx].focus()

    def action_focus_previous_panel(self) -> None:
        """Focus the previous panel."""
        app = cast("LazyOpenCode", self)
        all_panels: list[Widget] = []
        all_panels.extend(app._panels)
        if app._combined_panel:
            all_panels.append(app._combined_panel)

        current_idx = 0
        for i, panel in enumerate(all_panels):
            if panel.has_focus:
                current_idx = i
                break

        # If main pane is focused
        if app._main_pane and app._main_pane.has_focus:
            # If main pane has focus, go back to last focused panel or last panel
            if app._last_focused_panel:
                app._last_focused_panel.focus()
                return
            else:
                current_idx = 0  # Will become -1 -> last

        prev_idx = (current_idx - 1) % len(all_panels)
        if all_panels[prev_idx]:
            all_panels[prev_idx].focus()

    def action_focus_panel_1(self) -> None:
        """Focus Commands panel."""
        app = cast("LazyOpenCode", self)
        if len(app._panels) > 0:
            app._panels[0].focus()

    def action_focus_panel_2(self) -> None:
        """Focus Agents panel."""
        app = cast("LazyOpenCode", self)
        if len(app._panels) > 1:
            app._panels[1].focus()

    def action_focus_panel_3(self) -> None:
        """Focus Skills panel."""
        app = cast("LazyOpenCode", self)
        if len(app._panels) > 2:
            app._panels[2].focus()

    def action_focus_panel_4(self) -> None:
        """Focus Rules tab in combined panel."""
        app = cast("LazyOpenCode", self)
        if app._combined_panel:
            app._combined_panel.switch_to_tab(0)
            app._combined_panel.focus()

    def action_focus_panel_5(self) -> None:
        """Focus MCPs tab in combined panel."""
        app = cast("LazyOpenCode", self)
        if app._combined_panel:
            app._combined_panel.switch_to_tab(1)
            app._combined_panel.focus()

    def action_focus_main_pane(self) -> None:
        """Focus the main pane."""
        app = cast("LazyOpenCode", self)
        if app._main_pane:
            app._main_pane.focus()
