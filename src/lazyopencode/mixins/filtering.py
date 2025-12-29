"""Filtering mixin for handling filter actions."""

from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    from lazyopencode.app import LazyOpenCode

from lazyopencode.models.customization import ConfigLevel


class FilteringMixin:
    """Mixin for filtering actions."""

    def action_filter_all(self) -> None:
        """Show all customizations."""
        app = cast("LazyOpenCode", self)
        app._level_filter = None
        app._update_status_panel()
        app._update_panels()

    def action_filter_global(self) -> None:
        """Show only global customizations."""
        app = cast("LazyOpenCode", self)
        app._level_filter = ConfigLevel.GLOBAL
        app._update_status_panel()
        app._update_panels()

    def action_filter_project(self) -> None:
        """Show only project customizations."""
        app = cast("LazyOpenCode", self)
        app._level_filter = ConfigLevel.PROJECT
        app._update_status_panel()
        app._update_panels()
