# LazyOpenCode

A keyboard-driven TUI for managing OpenCode customizations.

![LazyOpenCode Screenshot](artifacts/demo.png)

## Features

- Visual discovery of all OpenCode customizations
- Keyboard-driven navigation (lazygit-inspired)
- View commands, agents, skills, rules, MCPs, and plugins
- Filter by configuration level (global/project)
- Search within customizations

## Installation

```bash
uvx lazyopencode
```

Or install with pip:

```bash
pip install lazyopencode
```

## Keyboard Shortcuts

| Key        | Action           |
| ---------- | ---------------- |
| `j` / `↓`  | Move down        |
| `k` / `↑`  | Move up          |
| `Tab`      | Next panel       |
| `[` / `]`  | Prev/Next view   |
| `1`-`7`    | Jump to panel    |
| `a`        | All filter       |
| `g`        | Global filter    |
| `p`        | Project filter   |
| `/`        | Search           |
| `e`        | Edit selected    |
| `r`        | Refresh          |
| `ctrl+u`   | User Config      |
| `?`        | Help             |
| `q`        | Quit             |

## Configuration Paths

LazyOpenCode discovers customizations from:

| Type     | Global                             | Project              |
| -------- | ---------------------------------- | -------------------- |
| Commands | `~/.config/opencode/command/`      | `.opencode/command/` |
| Agents   | `~/.config/opencode/agent/`        | `.opencode/agent/`   |
| Skills   | `~/.config/opencode/skill/`        | `.opencode/skill/`   |
| Rules    | `~/.config/opencode/AGENTS.md`     | `AGENTS.md`          |
| MCPs     | `~/.config/opencode/opencode.json` | `opencode.json`      |
| Tools    | `~/.config/opencode/tool/`         | `.opencode/tool/`    |
| Plugins  | `~/.config/opencode/plugin/`       | `.opencode/plugin/`  |

## Inspired By

- [LazyClaude](https://github.com/NikiforovAll/lazyclaude) - Similar TUI for Claude Code
- [Lazygit](https://github.com/jesseduffield/lazygit) - Keyboard-driven Git TUI
- [OpenCode](https://opencode.ai) - AI coding agent


## Development

```bash
# Clone and install
git clone https://github.com/yourusername/lazyopencode
cd lazyopencode
uv sync

# Run
uv run lazyopencode

# Run tests
uv run pytest

# Lint and format
uv run ruff check .
uv run ruff format .
```

## License

MIT
