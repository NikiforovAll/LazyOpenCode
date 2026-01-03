"""AppFooter widget for displaying keybindings."""

from textual.app import ComposeResult
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Static

from lazyopencode.widgets.helpers.rendering import format_keybinding


class AppFooter(Widget):
    """Footer displaying available keybindings."""

    DEFAULT_CSS = """
    AppFooter {
        dock: bottom;
        height: 1;
        background: $panel;
    }

    AppFooter .footer-content {
        width: 100%;
        text-align: center;
    }
    """

    filter_level: reactive[str] = reactive("All")
    search_active: reactive[bool] = reactive(False)

    def compose(self) -> ComposeResult:
        """Compose the footer content."""
        yield Static(self._get_footer_text(), classes="footer-content")

    def _get_footer_text(self) -> str:
        """Build the footer text with keybindings."""
        all_key = format_keybinding("a", "All", active=self.filter_level == "All")
        user_key = format_keybinding(
            "g", "Global", active=self.filter_level == "Global"
        )
        project_key = format_keybinding(
            "p", "Project", active=self.filter_level == "Project"
        )
        search_key = format_keybinding("/", "Search", active=self.search_active)

        return (
            f"[bold]q[/] Quit  [bold]?[/] Help  [bold]r[/] Refresh  "
            f"[bold]e[/] Edit  [bold]c[/] Copy  "
            f"{all_key}  {user_key}  {project_key}  "
            f"{search_key}  │  [bold][$accent]^p[/][/] Palette"
        )

    def on_mount(self) -> None:
        """Handle mount event."""
        pass

    def _update_content(self) -> None:
        """Update the footer content."""
        if self.is_mounted:
            try:
                content = self.query_one(".footer-content", Static)
                content.update(self._get_footer_text())
            except Exception:
                pass

    def watch_filter_level(self, _level: str) -> None:
        """React to filter level changes."""
        self._update_content()

    def watch_search_active(self, _active: bool) -> None:
        """React to search active changes."""
        self._update_content()
