"""LazyOpenCode - TUI for managing OpenCode customizations."""

__version__ = "0.1.0"

from lazyopencode.app import LazyOpenCode


def main() -> None:
    """Run the LazyOpenCode application."""
    app = LazyOpenCode()
    app.run()
