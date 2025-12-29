"""Help mixin for LazyOpenCode application."""

from typing import TYPE_CHECKING, cast

from textual.app import App
from textual.widgets import Static

from lazyopencode import __version__

if TYPE_CHECKING:
    pass


class HelpMixin:
    """Mixin providing help overlay functionality."""

    _help_visible: bool = False

    def action_toggle_help(self) -> None:
        """Toggle help overlay visibility."""
        if self._help_visible:
            self._hide_help()
        else:
            self._show_help()

    def _show_help(self) -> None:
        """Show help overlay."""
        app = cast("App", self)
        help_content = f"""[bold]LazyOpenCode v{__version__}[/]

[bold]Navigation[/]
  j/k or Up/Down     Move up/down in list
  d/u            Page down/up (detail pane)
  g/G            Go to top/bottom
  0              Focus main pane
  1-3            Focus panel by number
  4-6            Focus combined panel tab
  Tab            Switch between panels
  Enter          Drill down
  Esc            Go back

[bold]Filtering[/]
  /              Search by name/description
  a              Show all levels
  g              Show global-level only
  p              Show project-level only

[bold]Views[/]
  [ / ]         Main: content/metadata
                 Combined: switch tabs

[bold]Actions[/]
  e              Open in $EDITOR (Not Implemented)
  r              Refresh from disk
  ?              Toggle this help
  q              Quit

[dim]Press ? or Esc to close[/]"""

        if not app.query("#help-overlay"):
            help_widget = Static(help_content, id="help-overlay")
            app.mount(help_widget)
            self._help_visible = True

    def _hide_help(self) -> None:
        """Hide help overlay."""
        app = cast("App", self)
        try:
            help_widget = app.query_one("#help-overlay")
            help_widget.remove()
            self._help_visible = False
        except Exception:
            pass
