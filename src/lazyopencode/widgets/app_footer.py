"""AppFooter widget for displaying keybindings."""

from textual.app import ComposeResult
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Static


class AppFooter(Widget):
    """Footer displaying available keybindings."""

    DEFAULT_CSS = """
    AppFooter {
        dock: bottom;
        height: 1;
        background: $surface;
        color: $text-muted;
    }

    AppFooter .footer-content {
        height: 1;
        text-style: bold;
    }
    """

    search_active: reactive[bool] = reactive(False)

    def compose(self) -> ComposeResult:
        """Compose the footer content."""
        yield Static(self._get_footer_text(), classes="footer-content")

    def _get_footer_text(self) -> str:
        """Build the footer text with keybindings."""
        bindings = [
            ("q", "Quit"),
            ("?", "Help"),
            ("r", "Refresh"),
            ("e", "Edit"),
            ("a", "All"),
            ("g", "Global"),
            ("p", "Project"),
            ("/", "Search"),
            ("[", "["),
            ("]", "]"),
        ]

        parts = []
        for key, label in bindings:
            parts.append(f"[b]{key}[/b] {label}")

        return "  ".join(parts)

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

    def watch_search_active(self, active: bool) -> None:
        """React to search active changes."""
        self._update_content()
