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


def build_synthetic_markdown(metadata: dict[str, Any], body: str) -> str:
    """
    Build a synthetic markdown string with YAML frontmatter.

    Args:
        metadata: Dictionary of metadata (without the body field)
        body: The body content

    Returns:
        Full markdown string with --- delimiters matching the pattern:
        ^---\\s*\n(.*?)\n---\\s*\n(.*)$
    """
    try:
        # Filter out empty or None values to keep it clean
        clean_meta = {k: v for k, v in metadata.items() if v is not None}
        if not clean_meta:
            # Even if empty, we provide the delimiters to ensure separation in UI
            return f"---\n---\n{body}"

        frontmatter = yaml.dump(clean_meta, sort_keys=False).strip()
        # Ensure it's not just "{}"
        if frontmatter == "{}":
            frontmatter = ""

        # Match pattern: ^---\s*\n(.*?)\n---\s*\n(.*)$
        # No extra newline after closing ---
        return f"---\n{frontmatter}\n---\n{body}"
    except Exception:
        return body


def strip_jsonc_comments(content: str) -> str:
    """
    Strip // comments from JSON content, preserving URLs.

    Args:
        content: JSON string potentially containing comments

    Returns:
        Cleaned JSON string
    """
    lines = []
    for line in content.splitlines():
        # Find // that is not part of a URL (not preceded by :)
        pos = 0
        while True:
            idx = line.find("//", pos)
            if idx == -1:
                lines.append(line)
                break
            # Check if preceded by :
            if idx > 0 and line[idx - 1] == ":":
                pos = idx + 2
                continue
            # Found a comment, strip it
            lines.append(line[:idx])
            break
    return "\n".join(lines)


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
