# Specification Tests

This directory contains **scenario-based specification tests** for LazyOpenCode's configuration parsing.

## Philosophy

Each scenario represents a real-world configuration setup. Tests verify that the discovery service correctly parses and returns the expected customizations.

**Benefits:**
- Tests serve as living documentation
- Each scenario is self-contained and understandable
- Easy to add new scenarios for edge cases
- README.md in each scenario explains the "why"

## Directory Structure

```
tests/spec/
├── SPEC.md              # This file
├── conftest.py          # ScenarioResult wrapper and load_scenario fixture
├── scenarios/           # One folder per scenario
│   ├── minimal/
│   │   ├── README.md    # What this scenario tests
│   │   ├── AGENTS.md    # Fixture files...
│   │   └── opencode.json
│   ├── inline_commands/
│   │   └── ...
│   └── ...
└── test_scenarios.py    # All scenario tests
```

## Writing Tests

### Loading a Scenario

```python
def test_discovers_commands(load_scenario):
    scenario = load_scenario("inline_commands")
    
    # Use convenience properties
    assert len(scenario.commands) == 2
    assert len(scenario.agents) == 0
    
    # Use lookup methods
    lint_cmd = scenario.get_command("lint")
    assert lint_cmd is not None
    assert lint_cmd.description == "Run linting"
```

### ScenarioResult API

**Type accessors:**
- `scenario.commands` - All COMMAND customizations
- `scenario.agents` - All AGENT customizations
- `scenario.skills` - All SKILL customizations
- `scenario.rules` - All RULES customizations
- `scenario.mcps` - All MCP customizations
- `scenario.tools` - All TOOL customizations
- `scenario.plugins` - All PLUGIN customizations

**Filtering:**
- `scenario.by_type(CustomizationType.COMMAND)`
- `scenario.by_level(ConfigLevel.PROJECT)`
- `scenario.by_name("lint")`

**Lookups:**
- `scenario.get("name")` - Get any customization by name
- `scenario.get_command("name")` - Get command by name
- `scenario.get_agent("name")` - Get agent by name
- `scenario.get_skill("name")` - Get skill by name

**Properties:**
- `scenario.names` - Set of all names
- `scenario.types` - Set of all types present
- `scenario.has_errors` - True if any customization has error
- `scenario.errors` - List of customizations with errors
- `len(scenario)` - Total count
- `"name" in scenario` - Check if name exists

## Adding a New Scenario

1. Create a folder in `scenarios/`:
   ```
   scenarios/my_new_scenario/
   ```

2. Add a `README.md` explaining the scenario:
   ```markdown
   # Scenario: My New Scenario
   
   ## Given
   - Description of the configuration setup
   
   ## Expected
   - What should be discovered
   ```

3. Add the fixture files (opencode.json, .opencode/, AGENTS.md, etc.)

4. Add tests in `test_scenarios.py`:
   ```python
   class TestMyNewScenario:
       """Scenario: My New Scenario - description."""
       
       def test_expected_behavior(self, load_scenario):
           scenario = load_scenario("my_new_scenario")
           # assertions...
   ```

## Scenarios

| Scenario | Purpose |
|----------|---------|
| `minimal` | Bare minimum config - only AGENTS.md |
| `inline_commands` | Commands defined in opencode.json |
| `file_commands` | Commands in .opencode/command/*.md |
| `mixed_config` | Both inline and file-based definitions |
| `file_references` | `{file:./path}` pattern resolution |
| `skills_with_tree` | Skills with nested file trees |

## Running Tests

```bash
# Run all spec tests
uv run pytest tests/spec/ -v

# Run specific scenario
uv run pytest tests/spec/test_scenarios.py::TestInlineCommands -v
```
