"""Rendering helpers for widget items."""


def format_keybinding(key: str, label: str, *, active: bool = False) -> str:
    """Format a keybinding with optional highlight for active state.

    Args:
        key: The keyboard key (e.g., "a", "P", "/").
        label: The action label (e.g., "All", "Search").
        active: Whether the action is currently active.

    Returns:
        Formatted string like "[bold]a[/] All" or "[bold]a[/] [$primary]All[/]".
    """
    if active:
        return f"[bold]{key}[/] [$primary]{label}[/]"
    return f"[bold]{key}[/] {label}"
