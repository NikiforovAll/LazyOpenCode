# LazyOpenCode

A keyboard-driven TUI for visualizing and managing OpenCode customizations.

## Project Overview

- **Language**: Python 3.11+
- **Framework**: Textual (TUI), Rich (terminal formatting)
- **Package Manager**: uv
- **Architecture**: Mixin-based Textual app with service layer
- **Inspired by**: LazyClaude, Lazygit

## Quick Start

```bash
# Run the application
uv run lazyopencode

# Run tests
uv run pytest

# Lint and format
uv run ruff check .
uv run ruff format .
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
| Plugins | `~/.config/opencode/plugin/` | `.opencode/plugin/` |

## Key Components

### Models (`models/customization.py`)
- `Customization` - Core data object for any customization
- `ConfigLevel` - Enum: GLOBAL, PROJECT
- `CustomizationType` - Enum: COMMAND, AGENT, SKILL, RULES, MCP, PLUGIN

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
