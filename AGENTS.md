# LazyOpenCode

A keyboard-driven TUI for visualizing and managing OpenCode customizations.

## Environment Rules
- **OS**: Windows (Git Bash). Use forward slashes `/` and `/c/` prefix for absolute paths.
- **Search**: `rg` and `fd` are installed. Use them for fast searching.
- **Quality Gates**: Always run quality gates before asking the user to commit changes. Use the `quality-gates` skill by calling the Skill tool. Do NOT run `uv run ruff`, `uv run mypy`, or other individual linting tools directly - always use the skill instead.
- **TUI Verification**: Do NOT run `uv run lazyopencode` to verify the application. It is a TUI and output cannot be captured effectively. Use unit tests or static analysis instead.

## Project Overview

- **Language**: Python 3.11+
- **Framework**: Textual (TUI), Rich (terminal formatting)
- **Package Manager**: uv
- **Architecture**: Mixin-based Textual app with service layer
- **Inspired by**: LazyClaude, Lazygit

## Implementation Status (Phases 0-5 Completed)

- [x] **Foundation**: Project structure, dependencies, CLI entry point
- [x] **Models**: Customization types, data classes
- [x] **Widgets**: Type panels, combined panel, detail pane, status bar, footer
- [x] **Parsers**: Full support for Commands, Agents, Skills, Rules, MCPs, Tools, Plugins
- [x] **Navigation**: Vim-like navigation (j/k), tab switching, number shortcuts
- [x] **Filtering**: Filter by Global/Project, Search overlay
- [x] **Theme**: Gruvbox theme (default) matching LazyClaude style
- [ ] **Polish**: Settings persistence, comprehensive tests (In Progress)

## Quick Start

```bash
# Run the application
uv run lazyopencode

# Run tests
uv run pytest

# Run quality gates (linting, formatting, type checking, tests)
bash scripts/check_quality.sh
```

## Directory Structure

```
src/lazyopencode/
├── app.py           # Main Textual application
├── bindings.py      # Keyboard bindings
├── themes.py        # Theme definitions
├── models/          # Data models (Customization, ConfigLevel, etc.)
├── services/        # Business logic
│   ├── discovery.py # Finds customizations on disk
│   ├── filter.py    # Filters by level/query
│   └── parsers/     # Type-specific parsers
├── widgets/         # Textual UI components
├── mixins/          # App functionality mixins
└── styles/          # TCSS stylesheets
```

## Code Standards

### Python Style
- Use type hints for all function parameters and return values
- Use `dataclasses` for data models
- Follow PEP 8 naming conventions
- Maximum line length: 88 characters (ruff default)

### Textual Patterns
- Use `reactive` for state that should trigger UI updates
- Use `Message` classes for widget communication
- Use mixins to organize app functionality
- Keep widgets focused and single-purpose

### Imports
- Group imports: stdlib, third-party, local
- Use absolute imports within the package
- Re-export public APIs from `__init__.py`

## OpenCode Configuration Paths

The application discovers customizations from these locations:

| Type | Global Path | Project Path |
|------|-------------|--------------|
| Commands | `~/.config/opencode/command/*.md` | `.opencode/command/*.md` |
| Agents | `~/.config/opencode/agent/*.md` | `.opencode/agent/*.md` |
| Skills | `~/.config/opencode/skill/*/SKILL.md` | `.opencode/skill/*/SKILL.md` |
| Rules | `~/.config/opencode/AGENTS.md` | `AGENTS.md` |
| MCPs | `~/.config/opencode/opencode.json` | `opencode.json` |
| Tools | `~/.config/opencode/tool/*.ts` | `.opencode/tool/*.ts` |
| Plugins | `~/.config/opencode/plugin/` | `.opencode/plugin/` |

## Key Components

### Models (`models/customization.py`)
- `Customization` - Core data object for any customization
- `ConfigLevel` - Enum: GLOBAL, PROJECT
- `CustomizationType` - Enum: COMMAND, AGENT, SKILL, RULES, MCP, TOOL, PLUGIN

### Services
- `ConfigDiscoveryService` - Scans filesystem, uses parsers
- `FilterService` - Filters by level and search query
- `ICustomizationParser` - Protocol for type-specific parsers

### Widgets
- `TypePanel` - List panel with selection
- `CombinedPanel` - Tabbed panel for multiple types
- `DetailPane` - Content display with syntax highlighting
- `StatusPanel` - Shows current path and filter
- `AppFooter` - Keyboard shortcuts

### Mixins
- `NavigationMixin` - Panel focus, cursor movement
- `FilterMixin` - Level filters, search
- `HelpMixin` - Help overlay

## Testing

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=lazyopencode

# Run specific test file
uv run pytest tests/unit/test_parsers.py
```

### Test Structure
- `tests/unit/` - Unit tests for models, services, parsers
- `tests/integration/` - App integration tests
- `tests/conftest.py` - Shared fixtures

## Dependencies

### Runtime
- `textual>=0.89.0` - TUI framework
- `rich>=13.0.0` - Terminal formatting
- `pyyaml>=6.0` - YAML/frontmatter parsing

### Development
- `pytest` - Testing
- `pytest-asyncio` - Async test support
- `ruff` - Linting and formatting

## Adding New Features

### Adding a new customization type
1. Add enum value to `CustomizationType`
2. Create parser in `services/parsers/`
3. Register parser in `ConfigDiscoveryService`
4. Add panel or tab in widgets

### Adding a new keybinding
1. Add binding to `bindings.py`
2. Implement `action_*` method in appropriate mixin
3. Update help text

### Adding a new widget
1. Create widget in `widgets/`
2. Add styles to `styles/app.tcss`
3. Compose in `app.py`

## Planning Documents

See `_plans/` directory for detailed specifications:
- `00-overview.md` - Project overview
- `01-architecture.md` - Architecture decisions
- `02-customization-types.md` - OpenCode customization mapping
- `03-implementation-phases.md` - Implementation plan
- `04-file-structure.md` - File structure
- `05-agents-md-template.md` - This template
