"""CombinedPanel widget for Rules/MCPs/Plugins tabs."""

from typing import TYPE_CHECKING, cast

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import VerticalScroll
from textual.message import Message
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Static

if TYPE_CHECKING:
    from lazyopencode.app import LazyOpenCode

from lazyopencode.models.customization import (
    Customization,
    CustomizationType,
)


class CombinedPanel(Widget):
    """Panel with tabs for Rules, MCPs, and Plugins."""

    BINDINGS = [
        Binding("tab", "focus_next_panel", "Next Panel", show=False),
        Binding("shift+tab", "focus_previous_panel", "Prev Panel", show=False),
        Binding("j", "cursor_down", "Down", show=False),
        Binding("k", "cursor_up", "Up", show=False),
        Binding("down", "cursor_down", "Down", show=False),
        Binding("up", "cursor_up", "Up", show=False),
        Binding("g", "cursor_top", "Top", show=False),
        Binding("G", "cursor_bottom", "Bottom", show=False, key_display="shift+g"),
        Binding("enter", "select", "Select", show=False),
        Binding("left", "prev_tab", "Prev Tab", show=False),
        Binding("right", "next_tab", "Next Tab", show=False),
        Binding("h", "prev_tab", "Prev Tab", show=False),
        Binding("l", "next_tab", "Next Tab", show=False),
    ]

    DEFAULT_CSS = """
    CombinedPanel {
        height: 1fr;
        min-height: 3;
        border: solid $primary;
        padding: 0 1;
        border-title-align: left;
        border-subtitle-align: right;
    }

    CombinedPanel:focus {
        border: double $accent;
    }

    CombinedPanel .items-container {
        height: auto;
    }

    CombinedPanel .item {
        height: 1;
        width: 100%;
        text-wrap: nowrap;
        text-overflow: ellipsis;
    }

    CombinedPanel .item-selected {
        background: $accent;
        text-style: bold;
    }

    CombinedPanel .empty-message {
        color: $text-muted;
        text-style: italic;
    }

    CombinedPanel.empty {
        height: 3;
        min-height: 3;
        max-height: 3;
    }
    """

    # Tab configuration: (type, panel_number, label)
    TABS = [
        (CustomizationType.RULES, 4, "Memory"),
        (CustomizationType.MCP, 5, "MCPs"),
        (CustomizationType.PLUGIN, 6, "Plugins"),
    ]

    current_tab: reactive[int] = reactive(0)
    selected_index: reactive[int] = reactive(0)
    is_active: reactive[bool] = reactive(False)

    class SelectionChanged(Message):
        """Emitted when selected customization changes."""

        def __init__(self, customization: Customization | None) -> None:
            self.customization = customization
            super().__init__()

    class DrillDown(Message):
        """Emitted when user drills into a customization."""

        def __init__(self, customization: Customization) -> None:
            self.customization = customization
            super().__init__()

    def __init__(
        self,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        """Initialize CombinedPanel."""
        super().__init__(name=name, id=id, classes=classes)
        self.can_focus = True
        self._customizations_by_type: dict[CustomizationType, list[Customization]] = {
            t: [] for t, _, _ in self.TABS
        }

    @property
    def current_type(self) -> CustomizationType:
        """Get the current tab's customization type."""
        return self.TABS[self.current_tab][0]

    @property
    def current_items(self) -> list[Customization]:
        """Get items for the current tab."""
        return self._customizations_by_type.get(self.current_type, [])

    @property
    def selected_customization(self) -> Customization | None:
        """Get the currently selected customization."""
        items = self.current_items
        if items and 0 <= self.selected_index < len(items):
            return items[self.selected_index]
        return None

    def compose(self) -> ComposeResult:
        """Compose the panel content."""
        with VerticalScroll(classes="items-container"):
            items = self.current_items
            if not items:
                yield Static("[dim italic]No items[/]", classes="empty-message")
            else:
                for i, item in enumerate(items):
                    yield Static(
                        self._render_item(i, item), classes="item", id=f"item-{i}"
                    )

    def _render_header(self) -> str:
        """Render the panel header with tabs."""
        parts = []
        for i, (_, num, label) in enumerate(self.TABS):
            if i == self.current_tab:
                parts.append(f"[b][{num}]-{label}[/b]")
            else:
                parts.append(f"[{num}]-{label}")
        return " | ".join(parts) + "-"

    def _render_footer(self) -> str:
        """Render the panel footer with selection position."""
        count = len(self.current_items)
        if count == 0:
            return "0 of 0"
        return f"{self.selected_index + 1} of {count}"

    def _render_item(self, index: int, item: Customization) -> str:
        """Render a single item."""
        is_selected = index == self.selected_index and self.is_active
        prefix = ">" if is_selected else " "
        error_marker = " [red]![/]" if item.has_error else ""
        return f"{prefix} {item.display_name}{error_marker}"

    def on_mount(self) -> None:
        """Handle mount event."""
        self.border_title = self._render_header()
        self.border_subtitle = self._render_footer()

    def watch_current_tab(self, tab: int) -> None:
        """React to tab changes."""
        self.selected_index = 0
        if self.is_mounted:
            self.border_title = self._render_header()
            self.border_subtitle = self._render_footer()
            self.call_later(self._rebuild_items)
            if self.is_active:
                self._emit_selection_message()

    def watch_selected_index(self, index: int) -> None:
        """React to selected index changes."""
        if self.is_mounted:
            self.border_subtitle = self._render_footer()
        self._refresh_display()
        self._scroll_to_selection()
        self._emit_selection_message()

    async def _rebuild_items(self) -> None:
        """Rebuild item widgets."""
        if not self.is_mounted:
            return
        container = self.query_one(".items-container", VerticalScroll)
        await container.remove_children()

        items = self.current_items
        if not items:
            await container.mount(
                Static("[dim italic]No items[/]", classes="empty-message")
            )
        else:
            for i, item in enumerate(items):
                is_selected = i == self.selected_index and self.is_active
                classes = "item item-selected" if is_selected else "item"
                await container.mount(
                    Static(self._render_item(i, item), classes=classes, id=f"item-{i}")
                )
        container.scroll_home(animate=False)

    def _refresh_display(self) -> None:
        """Refresh the panel display."""
        try:
            items_widgets = list(self.query("Static.item"))
            items = self.current_items
            for i, (item_widget, item) in enumerate(
                zip(items_widgets, items, strict=False)
            ):
                if isinstance(item_widget, Static):
                    item_widget.update(self._render_item(i, item))
                is_selected = i == self.selected_index and self.is_active
                item_widget.set_class(is_selected, "item-selected")
        except Exception:
            pass

    def _scroll_to_selection(self) -> None:
        """Scroll to keep the selected item visible."""
        if len(self.current_items) == 0:
            return
        try:
            items = list(self.query(".item"))
            if 0 <= self.selected_index < len(items):
                items[self.selected_index].scroll_visible(animate=False)
        except Exception:
            pass

    def on_focus(self) -> None:
        """Handle focus event."""
        self.is_active = True
        self._refresh_display()
        self._emit_selection_message()

    def on_blur(self) -> None:
        """Handle blur event."""
        self.is_active = False
        self._refresh_display()

    def action_cursor_down(self) -> None:
        """Move selection down."""
        count = len(self.current_items)
        if count > 0 and self.selected_index < count - 1:
            self.selected_index += 1

    def action_cursor_up(self) -> None:
        """Move selection up."""
        if len(self.current_items) > 0 and self.selected_index > 0:
            self.selected_index -= 1

    def action_cursor_top(self) -> None:
        """Move selection to top."""
        if len(self.current_items) > 0:
            self.selected_index = 0

    def action_cursor_bottom(self) -> None:
        """Move selection to bottom."""
        count = len(self.current_items)
        if count > 0:
            self.selected_index = count - 1

    def action_next_tab(self) -> None:
        """Switch to next tab."""
        self.current_tab = (self.current_tab + 1) % len(self.TABS)

    def action_prev_tab(self) -> None:
        """Switch to previous tab."""
        self.current_tab = (self.current_tab - 1) % len(self.TABS)

    def action_select(self) -> None:
        """Drill down into selected customization."""
        if self.selected_customization:
            self.post_message(self.DrillDown(self.selected_customization))

    def action_focus_next_panel(self) -> None:
        """Delegate to app's focus_next_panel action."""
        cast("LazyOpenCode", self.app).action_focus_next_panel()

    def action_focus_previous_panel(self) -> None:
        """Delegate to app's focus_previous_panel action."""
        cast("LazyOpenCode", self.app).action_focus_previous_panel()

    def set_customizations(self, customizations: list[Customization]) -> None:
        """Set the customizations for all tabs."""
        for ctype, _, _ in self.TABS:
            self._customizations_by_type[ctype] = [
                c for c in customizations if c.type == ctype
            ]
        if self.selected_index >= len(self.current_items):
            self.selected_index = max(0, len(self.current_items) - 1)
        if self.is_mounted:
            self.border_subtitle = self._render_footer()
            self.call_later(self._rebuild_items)
        self._update_empty_state()

    def _update_empty_state(self) -> None:
        """Toggle empty class based on total item count."""
        total = sum(len(items) for items in self._customizations_by_type.values())
        if total == 0:
            self.add_class("empty")
        else:
            self.remove_class("empty")

    def _emit_selection_message(self) -> None:
        """Emit selection message."""
        self.post_message(self.SelectionChanged(self.selected_customization))

    def switch_to_tab(self, tab_index: int) -> None:
        """Switch to a specific tab by index."""
        if 0 <= tab_index < len(self.TABS):
            self.current_tab = tab_index
