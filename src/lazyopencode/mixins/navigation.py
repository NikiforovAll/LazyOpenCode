"""Navigation mixin for handling panel focus and keyboard shortcuts."""

from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    from lazyopencode.app import LazyOpenCode
    from lazyopencode.widgets.combined_panel import CombinedPanel
    from lazyopencode.widgets.type_panel import TypePanel


class NavigationMixin:
    """Mixin for application navigation."""

    def _get_focused_panel(self) -> "TypePanel | CombinedPanel | None":
        """Get the currently focused panel (TypePanel or CombinedPanel)."""
        app = cast("LazyOpenCode", self)
        for panel in app._panels:
            if panel.has_focus:
                return panel
        return None

    def action_focus_next_panel(self) -> None:
        """Focus the next panel. Ensures combined panel starts at first tab."""
        app = cast("LazyOpenCode", self)
        all_panels = app._panels

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
        next_panel = all_panels[next_idx]
        if next_panel:
            # If entering combined panel from above, start at first tab
            from lazyopencode.widgets.combined_panel import CombinedPanel

            if isinstance(next_panel, CombinedPanel):
                next_panel.switch_to_tab(0)
            next_panel.focus()

    def action_focus_previous_panel(self) -> None:
        """Focus the previous panel. Ensures combined panel starts at last tab."""
        app = cast("LazyOpenCode", self)
        all_panels = app._panels

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
        prev_panel = all_panels[prev_idx]
        if prev_panel:
            # If entering combined panel from below (or wrap around), start at last tab
            from lazyopencode.widgets.combined_panel import CombinedPanel

            if isinstance(prev_panel, CombinedPanel):
                prev_panel.switch_to_tab(len(prev_panel.tabs) - 1)
            prev_panel.focus()

    def action_focus_panel_1(self) -> None:
        """Focus Commands tab in first combined panel."""
        app = cast("LazyOpenCode", self)
        from lazyopencode.widgets.combined_panel import CombinedPanel

        if len(app._panels) > 0:
            panel = app._panels[0]
            if isinstance(panel, CombinedPanel):
                panel.switch_to_tab(0)  # Commands tab
            panel.focus()

    def action_focus_panel_2(self) -> None:
        """Focus Agents tab in first combined panel."""
        app = cast("LazyOpenCode", self)
        from lazyopencode.widgets.combined_panel import CombinedPanel

        if len(app._panels) > 0:
            panel = app._panels[0]
            if isinstance(panel, CombinedPanel):
                panel.switch_to_tab(1)  # Agents tab
            panel.focus()

    def action_focus_panel_3(self) -> None:
        """Focus Skills panel."""
        app = cast("LazyOpenCode", self)
        if len(app._panels) > 1:
            app._panels[1].focus()

    def action_focus_panel_4(self) -> None:
        """Focus Agent Memory (Rules) panel."""
        app = cast("LazyOpenCode", self)
        if len(app._panels) > 2:
            app._panels[2].focus()

    def action_focus_panel_5(self) -> None:
        """Focus MCPs tab in second combined panel."""
        app = cast("LazyOpenCode", self)
        from lazyopencode.widgets.combined_panel import CombinedPanel

        if len(app._panels) > 3:
            panel = app._panels[3]
            if isinstance(panel, CombinedPanel):
                panel.switch_to_tab(0)  # MCPs tab
            panel.focus()

    def action_focus_panel_6(self) -> None:
        """Focus Tools tab in second combined panel."""
        app = cast("LazyOpenCode", self)
        from lazyopencode.widgets.combined_panel import CombinedPanel

        if len(app._panels) > 3:
            panel = app._panels[3]
            if isinstance(panel, CombinedPanel):
                panel.switch_to_tab(1)  # Tools tab
            panel.focus()

    def action_focus_panel_7(self) -> None:
        """Focus Plugins tab in second combined panel."""
        app = cast("LazyOpenCode", self)
        from lazyopencode.widgets.combined_panel import CombinedPanel

        if len(app._panels) > 3:
            panel = app._panels[3]
            if isinstance(panel, CombinedPanel):
                panel.switch_to_tab(2)  # Plugins tab
            panel.focus()

    def action_focus_main_pane(self) -> None:
        """Focus the main pane."""
        app = cast("LazyOpenCode", self)
        if app._main_pane:
            app._main_pane.focus()

    def action_prev_view(self) -> None:
        """Switch view based on focused widget."""
        app = cast("LazyOpenCode", self)
        from lazyopencode.widgets.combined_panel import CombinedPanel

        focused_panel = self._get_focused_panel()
        if focused_panel and isinstance(focused_panel, CombinedPanel):
            focused_panel.action_prev_tab()
        elif app._main_pane:
            app._main_pane.action_prev_view()

    def action_next_view(self) -> None:
        """Switch view based on focused widget."""
        app = cast("LazyOpenCode", self)
        from lazyopencode.widgets.combined_panel import CombinedPanel

        focused_panel = self._get_focused_panel()
        if focused_panel and isinstance(focused_panel, CombinedPanel):
            focused_panel.action_next_tab()
        elif app._main_pane:
            app._main_pane.action_next_view()

    def action_go_back_from_main_pane(self) -> None:
        """Return focus to the panel we drilled down from."""
        app = cast("LazyOpenCode", self)
        if app._last_focused_panel:
            app._last_focused_panel.focus()
        elif app._panels:
            # Fallback to first panel
            app._panels[0].focus()
