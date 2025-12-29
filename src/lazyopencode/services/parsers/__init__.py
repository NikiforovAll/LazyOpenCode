"""Parser utilities and interface for customization files."""

import re
from pathlib import Path
from typing import Any, Protocol

import yaml

from lazyopencode.models.customization import ConfigLevel, Customization


class ICustomizationParser(Protocol):
    """Interface for customization parsers."""

    def can_parse(self, path: Path) -> bool:
        """Check if this parser can handle the given path."""
        ...

    def parse(self, path: Path, level: ConfigLevel) -> Customization:
        """Parse a file into a Customization object."""
        ...


def parse_frontmatter(content: str) -> tuple[dict[str, Any], str]:
    """
    Parse YAML frontmatter from markdown content.

    Frontmatter is delimited by --- at the start and end.

    Args:
        content: Full file content

    Returns:
        Tuple of (frontmatter_dict, body_content)
    """
    pattern = r"^---\s*\n(.*?)\n---\s*\n?(.*)$"
    match = re.match(pattern, content, re.DOTALL)

    if not match:
        return {}, content

    try:
        frontmatter = yaml.safe_load(match.group(1)) or {}
    except yaml.YAMLError:
        frontmatter = {}

    return frontmatter, match.group(2)


def read_file_safe(path: Path) -> tuple[str | None, str | None]:
    """
    Safely read a file, returning content or error.

    Args:
        path: Path to file

    Returns:
        Tuple of (content, error) - one will be None
    """
    try:
        content = path.read_text(encoding="utf-8")
        return content, None
    except OSError as e:
        return None, f"Failed to read file: {e}"
    except UnicodeDecodeError as e:
        return None, f"Encoding error: {e}"
