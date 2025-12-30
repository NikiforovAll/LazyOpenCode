"""Parser for Plugin customizations."""

import re
from pathlib import Path

from lazyopencode.models.customization import (
    ConfigLevel,
    Customization,
    CustomizationType,
)
from lazyopencode.services.parsers import (
    ICustomizationParser,
    read_file_safe,
)


class PluginParser(ICustomizationParser):
    """Parses plugin customizations from TypeScript/JavaScript files.

    Plugins are JS/TS modules that export plugin functions. Each function
    receives a context object and returns a hooks object to extend OpenCode.

    Paths:
        - Global: ~/.config/opencode/plugin/*.ts or *.js
        - Project: .opencode/plugin/*.ts or *.js
    """

    VALID_EXTENSIONS = {".ts", ".js"}

    def can_parse(self, path: Path) -> bool:
        """Check if path is a plugin file."""
        return (
            path.is_file()
            and path.suffix in self.VALID_EXTENSIONS
            and path.parent.name == "plugin"
        )

    def parse(self, path: Path, level: ConfigLevel) -> Customization:
        """Parse plugin file - shows source code as preview."""
        content, error = read_file_safe(path)

        description = None
        exports: list[str] = []
        hooks: list[str] = []

        if content and not error:
            exports = self._extract_exports(content)
            hooks = self._extract_hooks(content)
            description = self._build_description(exports, hooks)

        return Customization(
            name=path.stem,
            type=CustomizationType.PLUGIN,
            level=level,
            path=path,
            description=description or f"Plugin: {path.stem}",
            content=content,
            metadata={
                "exports": exports,
                "hooks": hooks,
            },
            error=error,
        )

    def _extract_exports(self, content: str) -> list[str]:
        """
        Extract exported plugin names from the file.

        Looks for patterns like:
        - export const MyPlugin = ...
        - export function MyPlugin ...
        - export { MyPlugin }
        """
        exports: list[str] = []

        # Match: export const/let/var Name =
        const_pattern = r"export\s+(?:const|let|var)\s+(\w+)\s*[=:]"
        exports.extend(re.findall(const_pattern, content))

        # Match: export function Name
        func_pattern = r"export\s+function\s+(\w+)"
        exports.extend(re.findall(func_pattern, content))

        # Match: export { Name, Name2 }
        named_pattern = r"export\s*\{\s*([^}]+)\s*\}"
        for match in re.findall(named_pattern, content):
            names = [n.strip().split(" as ")[0].strip() for n in match.split(",")]
            exports.extend(n for n in names if n)

        return list(set(exports))

    def _extract_hooks(self, content: str) -> list[str]:
        """
        Extract hook names that the plugin subscribes to.

        Looks for patterns like:
        - "session.idle": async (...)
        - 'tool.execute.before': (...)
        - event: async ({ event }) => { ... }
        """
        hooks: list[str] = []

        # Match quoted hook names like "session.idle" or 'tool.execute.before'
        quoted_pattern = r'["\']([a-z]+(?:\.[a-z]+)+)["\']:\s*(?:async\s*)?\('
        hooks.extend(re.findall(quoted_pattern, content))

        # Match 'event' handler
        if re.search(r"\bevent\s*:\s*(?:async\s*)?\(", content):
            hooks.append("event")

        # Match 'tool' object for custom tools
        if re.search(r"\btool\s*:\s*\{", content):
            hooks.append("tool (custom tools)")

        return list(set(hooks))

    def _build_description(self, exports: list[str], hooks: list[str]) -> str | None:
        """Build a description from extracted info."""
        parts: list[str] = []

        if exports:
            parts.append(f"Exports: {', '.join(sorted(exports))}")

        if hooks:
            parts.append(f"Hooks: {', '.join(sorted(hooks))}")

        return " | ".join(parts) if parts else None
