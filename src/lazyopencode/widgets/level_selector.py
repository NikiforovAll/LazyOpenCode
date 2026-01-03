"""Level selector bar for copy operations."""

from textual.app import ComposeResult
from textual.binding import Binding
from textual.message import Message
from textual.widget import Widget
from textual.widgets import Static

from lazyopencode.models.customization import ConfigLevel


class LevelSelector(Widget):
    """Bottom bar for selecting target configuration level."""

    BINDINGS = [
        Binding("1", "select_global", "Global", show=False),
        Binding("2", "select_project", "Project", show=False),
        Binding("escape", "cancel", "Cancel", show=False),
    ]

    DEFAULT_CSS = """
    LevelSelector {
        dock: bottom;
        height: 3;
        border: solid $accent;
        padding: 0 1;
        margin-bottom: 1;
        display: none;
        background: $surface;
    }

    LevelSelector.visible {
        display: block;
    }

    LevelSelector:focus {
        border: double $accent;
    }

    LevelSelector #prompt {
        width: 100%;
        text-align: center;
    }

    LevelSelector .key {
        color: $accent;
        text-style: bold;
    }
    """

    can_focus = True

    class LevelSelected(Message):
        """Emitted when a level is selected."""

        def __init__(self, level: ConfigLevel) -> None:
            self.level = level
            super().__init__()

    class SelectionCancelled(Message):
        """Emitted when selection is cancelled."""

        pass

    def __init__(
        self,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        """Initialize LevelSelector."""
        super().__init__(name=name, id=id, classes=classes)
        self._available_levels: list[ConfigLevel] = []
        self._customization_name: str = ""

    def compose(self) -> ComposeResult:
        """Compose the level selector bar."""
        yield Static("", id="prompt")

    def show(
        self,
        available_levels: list[ConfigLevel],
        customization_name: str = "",
    ) -> None:
        """Show the level selector and focus it."""
        self._available_levels = available_levels
        self._customization_name = customization_name
        self._update_prompt()
        self.add_class("visible")
        self.focus()

    def hide(self) -> None:
        """Hide the level selector."""
        self.remove_class("visible")

    def _update_prompt(self) -> None:
        """Update the prompt text based on available levels."""
        name_part = f'"{self._customization_name}" ' if self._customization_name else ""

        options = []
        if ConfigLevel.GLOBAL in self._available_levels:
            options.append("\\[1] Global")
        if ConfigLevel.PROJECT in self._available_levels:
            options.append("\\[2] Project")

        options_text = "  ".join(options)
        prompt_widget = self.query_one("#prompt", Static)
        prompt_widget.update(f"Copy {name_part}to: {options_text}  \\[Esc] Cancel")

    def action_select_global(self) -> None:
        """Select global level."""
        if ConfigLevel.GLOBAL in self._available_levels:
            self.hide()
            self.post_message(self.LevelSelected(ConfigLevel.GLOBAL))

    def action_select_project(self) -> None:
        """Select project level."""
        if ConfigLevel.PROJECT in self._available_levels:
            self.hide()
            self.post_message(self.LevelSelected(ConfigLevel.PROJECT))

    def action_cancel(self) -> None:
        """Cancel selection."""
        self.hide()
        self.post_message(self.SelectionCancelled())

    @property
    def is_visible(self) -> bool:
        """Check if the level selector is visible."""
        return self.has_class("visible")
