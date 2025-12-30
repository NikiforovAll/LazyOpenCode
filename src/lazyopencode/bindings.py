"""App keybindings configuration."""

from textual.binding import Binding, BindingType

APP_BINDINGS: list[BindingType] = [
    Binding("q", "quit", "Quit"),
    Binding("?", "toggle_help", "Help"),
    Binding("r", "refresh", "Refresh"),
    Binding("e", "open_in_editor", "Edit"),
    Binding("ctrl+u", "open_user_config", "User Config"),
    Binding("tab", "focus_next_panel", "Next Panel", show=False),
    Binding("shift+tab", "focus_previous_panel", "Prev Panel", show=False),
    Binding("a", "filter_all", "All"),
    Binding("g", "filter_global", "Global"),
    Binding("p", "filter_project", "Project"),
    Binding("/", "search", "Search"),
    Binding("[", "prev_view", "[", show=True),
    Binding("]", "next_view", "]", show=True),
    Binding("0", "focus_main_pane", "Panel 0", show=False),
    Binding("1", "focus_panel_1", "Panel 1", show=False),
    Binding("2", "focus_panel_2", "Panel 2", show=False),
    Binding("3", "focus_panel_3", "Panel 3", show=False),
    Binding("4", "focus_panel_4", "Panel 4", show=False),
    Binding("5", "focus_panel_5", "Panel 5", show=False),
    Binding("6", "focus_panel_6", "Panel 6", show=False),
    Binding("7", "focus_panel_7", "Panel 7", show=False),
]
