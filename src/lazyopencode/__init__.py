"""LazyOpenCode - TUI for managing OpenCode customizations."""

try:
    from lazyopencode._version import __version__
except ImportError:
    __version__ = "0.0.0+dev"

import argparse
from pathlib import Path

from lazyopencode.app import create_app


def main() -> None:
    """Run the LazyOpenCode application."""
    parser = argparse.ArgumentParser(
        description="A lazygit-style TUI for visualizing OpenCode customizations",
        prog="lazyopencode",
    )

    parser.add_argument(
        "-V", "--version", action="version", version=f"%(prog)s {__version__}"
    )

    parser.add_argument(
        "-d",
        "--directory",
        type=Path,
        default=None,
        help="Project directory to scan for customizations (default: current directory)",
    )

    parser.add_argument(
        "-u",
        "--user-config",
        type=Path,
        default=None,
        help="Override user config path (default: ~/.config/opencode)",
    )

    args = parser.parse_args()

    # Handle directory argument - resolve to absolute path
    project_root = args.directory.resolve() if args.directory else None
    user_config = args.user_config.resolve() if args.user_config else None

    app = create_app(project_root=project_root, global_config_path=user_config)
    app.run()
