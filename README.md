# LazyOpenCode

A keyboard-driven TUI for managing OpenCode customizations.

![LazyOpenCode Screenshot](docs/screenshot.png)

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

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `q` | Quit |
| `1` | Commands panel |
| `2` | Agents panel |
| `3` | Skills panel |
| `4` | Rules panel |
| `5` | MCPs panel |
| `6` | Plugins panel |
| `j` / `↓` | Move down |
| `k` / `↑` | Move up |
| `Tab` | Next panel |
| `?` | Help |

## Configuration Paths

LazyOpenCode discovers customizations from:

| Type | Global | Project |
|------|--------|---------|
| Commands | `~/.config/opencode/command/` | `.opencode/command/` |
| Agents | `~/.config/opencode/agent/` | `.opencode/agent/` |
| Skills | `~/.config/opencode/skill/` | `.opencode/skill/` |
| Rules | `~/.config/opencode/AGENTS.md` | `AGENTS.md` |
| MCPs | `opencode.json` | `opencode.json` |
| Plugins | `~/.config/opencode/plugin/` | `.opencode/plugin/` |

## Inspired By

- [LazyClaude](https://github.com/NikiforovAll/lazyclaude) - Similar TUI for Claude Code
- [Lazygit](https://github.com/jesseduffield/lazygit) - Keyboard-driven Git TUI
- [OpenCode](https://opencode.ai) - AI coding agent

## License

MIT
