# Testing Guidelines for LazyOpenCode

This document provides guidelines for running tests and understanding the test infrastructure.

## Quick Start

```bash
# Run all tests
uv run pytest

# Run specific test file
uv run pytest tests/unit/test_example.py

# Run with verbose output
uv run pytest -v

# Run with coverage
uv run pytest --cov=lazyopencode
```

## Test Structure

Tests are organized into two categories:

### Unit Tests (`tests/unit/`)
- Fast, isolated tests for individual components
- Use `pyfakefs` for filesystem mocking
- No external dependencies or I/O

### Integration Tests (`tests/integration/`)
- Test interactions between components
- Use fixtures from `integration/fixtures/`
- Verify discovery, parsing, and filtering

## Filesystem Mocking with pyfakefs

We use `pyfakefs` to mock the filesystem without actually creating files. This keeps tests fast and isolated.

### Basic Pattern

```python
import pytest
from pathlib import Path

def test_discovery(fs):
    """fs is the pyfakefs fixture provided by pytest-pyfakefs."""
    # Create directories
    fs.create_dir("/fake/home/.config/opencode/command")
    
    # Write files
    fs.create_file(
        "/fake/home/.config/opencode/command/test.md",
        contents="---\ndescription: Test\n---\n"
    )
    
    # Patch Path.home()
    from unittest.mock import patch
    with patch.object(Path, "home", return_value=Path("/fake/home")):
        # Your test code here
        pass
```

### Common Fixtures

The `conftest.py` provides pre-built fixtures for common scenarios:

#### User Configuration Fixtures

```python
def test_user_config(user_config_path):
    """user_config_path creates ~/.config/opencode/ with fixture files."""
    # Automatically includes:
    # - command/greet.md
    # - agent/explorer.md
    # - skill/task-tracker/SKILL.md
    assert (user_config_path / "command" / "greet.md").exists()
```

#### Project Configuration Fixtures

```python
def test_project_config(project_config_path, fake_project_root):
    """project_config_path creates .opencode/ with fixture files."""
    # Automatically includes:
    # - command/project-cmd.md
    # - agent/reviewer.md
    # - skill/project-skill/SKILL.md
    assert (project_config_path / "command" / "project-cmd.md").exists()
```

#### MCP Configuration Fixtures

```python
def test_user_mcps(user_mcp_config):
    """user_mcp_config creates ~/.config/opencode/opencode.json"""
    assert user_mcp_config.exists()

def test_project_mcps(project_mcp_config):
    """project_mcp_config creates opencode.json at project root"""
    assert project_mcp_config.exists()
```

#### Full Configuration Fixtures

```python
def test_full_discovery(full_user_config, full_project_config, fake_project_root):
    """Combines all user and project fixtures."""
    # Both user and project configs are available
    pass
```

## Key Fixture Constants

```python
# From conftest.py:
FIXTURES_DIR = Path(__file__).parent / "integration" / "fixtures"
FAKE_HOME = Path("/fake/home")
```

### Fixture Locations

| Fixture | Location |
|---------|----------|
| Global Commands | `tests/integration/fixtures/command/` |
| Global Agents | `tests/integration/fixtures/agent/` |
| Global Skills | `tests/integration/fixtures/skill/*/SKILL.md` |
| Global Rules | `tests/integration/fixtures/memory/AGENTS.md` |
| Global MCP | `tests/integration/fixtures/mcp/user-opencode.json` |
| Project Commands | `tests/integration/fixtures/project/command/` |
| Project Agents | `tests/integration/fixtures/project/agent/` |
| Project Skills | `tests/integration/fixtures/project/skill/*/SKILL.md` |
| Project Rules | `tests/integration/fixtures/project/AGENTS.md` |
| Project MCP | `tests/integration/fixtures/mcp/project-opencode.json` |

## Adding New Fixtures

### 1. Add Fixture Files

Create files in `tests/integration/fixtures/`:

```
tests/integration/fixtures/
├── command/
│   ├── greet.md
│   └── my-new-command.md           # NEW
├── agent/
│   ├── explorer.md
│   └── my-new-agent.md             # NEW
└── skill/
    ├── task-tracker/
    │   └── SKILL.md
    └── my-new-skill/               # NEW
        └── SKILL.md
```

### 2. Update conftest.py

Fixtures are automatically loaded via `fs.add_real_directory()` and `fs.add_real_file()` in the fixture functions. If you add files to the standard locations, they'll be automatically included.

For custom fixture directories, create a new fixture:

```python
@pytest.fixture
def custom_config(fake_home: Path, fs: FakeFilesystem) -> Path:
    """Custom configuration with specialized fixtures."""
    custom_dir = fake_home / ".config" / "opencode"
    fs.create_dir(custom_dir)
    
    fs.add_real_file(
        FIXTURES_DIR / "custom" / "my-file.md",
        target_path=custom_dir / "my-file.md",
        read_only=False,
    )
    
    return custom_dir
```

## Fixture File Format

### Command Files

```markdown
---
description: Brief description
allowed-tools: Bash(*), Read(*)
argument-hint: <arg1> <arg2>
---
# Command Name
Description of what the command does.
```

### Agent Files

```markdown
---
name: agent-name
description: Brief description
tools: Glob, Grep, Read
model: haiku
---
# Agent Name
Description of the agent's purpose.
```

### Skill Files

```markdown
---
name: skill-name
description: Brief description
---
# Skill Name
Description of the skill.
```

### MCP Config Files

```json
{
  "mcp": {
    "server-name": {
      "command": "node",
      "args": ["path/to/server.js"]
    }
  }
}
```

### Rules Files (AGENTS.md)

Standard markdown with YAML frontmatter:

```markdown
---
version: 1
---
# Rules

Content describing rules and guidelines.
```

## Environment Rules

- **OS**: Windows (Git Bash). Use forward slashes `/` and `/c/` prefix for absolute paths.
- **Search**: `rg` and `fd` are installed. Use them for fast searching.
- **Quality Gates**: Always run quality gates before committing. Use `uv run pytest` and `scripts/check_quality.sh`.

## Example: Writing a Complete Test

```python
"""Test discovery service with mocked filesystem."""

from pathlib import Path
from lazyopencode.models.customization import ConfigLevel
from lazyopencode.services.discovery import ConfigDiscoveryService


def test_discover_all_customizations(full_user_config, full_project_config, fake_project_root, fake_home):
    """Test discovering all customization types."""
    from unittest.mock import patch
    
    with patch.object(Path, "home", return_value=fake_home):
        service = ConfigDiscoveryService(
            project_root=fake_project_root,
            global_config_path=fake_home / ".config" / "opencode"
        )
        
        all_customizations = service.discover_all()
        
        # Verify we found customizations at both levels
        global_customs = service.by_level(ConfigLevel.GLOBAL)
        project_customs = service.by_level(ConfigLevel.PROJECT)
        
        assert len(global_customs) > 0
        assert len(project_customs) > 0
        assert len(all_customizations) == len(global_customs) + len(project_customs)
```

## Common Issues and Solutions

### pyfakefs Not Mocking Correctly

Ensure you patch `Path.home()` in the same test scope:

```python
from unittest.mock import patch

def test_something(fake_home, fs):
    with patch.object(Path, "home", return_value=fake_home):
        # Now Path.home() returns fake_home
        pass
```

### File Not Found in Fixture

Check that:
1. File exists in `tests/integration/fixtures/`
2. `conftest.py` adds the real directory with correct path
3. Target path in fixture matches expected location

### Test Passes Locally But Fails in CI

Common causes:
- Path separators (use `/` not `\`)
- Fixture dependencies not declared
- Async fixtures not awaited

Always declare all fixture dependencies as function parameters.
