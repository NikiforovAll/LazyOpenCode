"""
Scenario-based specification tests for LazyOpenCode configuration parsing.

Each test class corresponds to a scenario in the scenarios/ directory.
See SPEC.md for documentation on how to add new scenarios.
"""

from collections.abc import Callable
from typing import Any

from lazyopencode.models.customization import ConfigLevel, CustomizationType

# ScenarioResult is provided by the load_scenario fixture in conftest.py
# We use Any here to avoid import complexity while keeping type hints useful
ScenarioResult = Any


class TestMinimal:
    """
    Scenario: Minimal Configuration

    Given: A project with only AGENTS.md at the root
    Then: Only rules are discovered
    """

    def test_discovers_only_rules(
        self, load_scenario: Callable[[str], ScenarioResult]
    ) -> None:
        """Only AGENTS.md is discovered as a RULES customization."""
        scenario = load_scenario("minimal")

        assert len(scenario) == 1
        assert len(scenario.rules) == 1
        assert scenario.rules[0].name == "AGENTS.md"

    def test_no_other_types(
        self, load_scenario: Callable[[str], ScenarioResult]
    ) -> None:
        """No commands, agents, skills, MCPs, tools, or plugins."""
        scenario = load_scenario("minimal")

        assert len(scenario.commands) == 0
        assert len(scenario.agents) == 0
        assert len(scenario.skills) == 0
        assert len(scenario.mcps) == 0
        assert len(scenario.tools) == 0
        assert len(scenario.plugins) == 0

    def test_all_project_level(
        self, load_scenario: Callable[[str], ScenarioResult]
    ) -> None:
        """All customizations are at PROJECT level."""
        scenario = load_scenario("minimal")

        for c in scenario:
            assert c.level == ConfigLevel.PROJECT

    def test_rules_content_available(
        self, load_scenario: Callable[[str], ScenarioResult]
    ) -> None:
        """AGENTS.md content is readable."""
        scenario = load_scenario("minimal")

        rules = scenario.rules[0]
        assert rules.content is not None
        assert "Project Rules" in rules.content


class TestInlineCommands:
    """
    Scenario: Inline Commands

    Given: opencode.json with command section containing 2 commands
    Then: Commands are extracted with correct structure
    """

    def test_discovers_two_commands(
        self, load_scenario: Callable[[str], ScenarioResult]
    ) -> None:
        """Two commands are discovered from opencode.json."""
        scenario = load_scenario("inline_commands")

        assert len(scenario.commands) == 2
        assert "lint" in scenario.names
        assert "test" in scenario.names

    def test_template_in_body_not_metadata(
        self, load_scenario: Callable[[str], ScenarioResult]
    ) -> None:
        """Template field becomes content body, not metadata."""
        scenario = load_scenario("inline_commands")

        lint = scenario.get_command("lint")
        assert lint is not None
        assert "template" not in lint.metadata
        assert "Run the linting tools" in (lint.content or "")

    def test_description_in_metadata(
        self, load_scenario: Callable[[str], ScenarioResult]
    ) -> None:
        """Description field is available in metadata."""
        scenario = load_scenario("inline_commands")

        lint = scenario.get_command("lint")
        assert lint is not None
        assert lint.description == "Run project linting"

    def test_agent_override_in_metadata(
        self, load_scenario: Callable[[str], ScenarioResult]
    ) -> None:
        """Agent override is preserved in metadata."""
        scenario = load_scenario("inline_commands")

        test_cmd = scenario.get_command("test")
        assert test_cmd is not None
        assert test_cmd.metadata.get("agent") == "plan"

    def test_content_has_frontmatter_format(
        self, load_scenario: Callable[[str], ScenarioResult]
    ) -> None:
        """Content matches frontmatter pattern."""
        import re

        scenario = load_scenario("inline_commands")

        lint = scenario.get_command("lint")
        assert lint is not None
        assert lint.content is not None

        pattern = r"^---\s*\n(.*?)\n---\s*\n(.*)$"
        match = re.match(pattern, lint.content, re.DOTALL)
        assert match is not None, "Content should match frontmatter pattern"

    def test_all_project_level(
        self, load_scenario: Callable[[str], ScenarioResult]
    ) -> None:
        """All commands are at PROJECT level."""
        scenario = load_scenario("inline_commands")

        for cmd in scenario.commands:
            assert cmd.level == ConfigLevel.PROJECT

    def test_all_command_type(
        self, load_scenario: Callable[[str], ScenarioResult]
    ) -> None:
        """All discovered items are COMMAND type."""
        scenario = load_scenario("inline_commands")

        for cmd in scenario.commands:
            assert cmd.type == CustomizationType.COMMAND


class TestFileCommands:
    """
    Scenario: File-Based Commands

    Given: .opencode/command/ directory with 2 markdown files
    Then: Commands are discovered with correct structure
    """

    def test_discovers_two_commands(
        self, load_scenario: Callable[[str], ScenarioResult]
    ) -> None:
        """Two commands are discovered from markdown files."""
        scenario = load_scenario("file_commands")

        assert len(scenario.commands) == 2
        assert "greet" in scenario.names
        assert "deploy" in scenario.names

    def test_name_from_filename(
        self, load_scenario: Callable[[str], ScenarioResult]
    ) -> None:
        """Command name is derived from filename (stem)."""
        scenario = load_scenario("file_commands")

        greet = scenario.get_command("greet")
        assert greet is not None
        assert greet.name == "greet"

    def test_frontmatter_in_metadata(
        self, load_scenario: Callable[[str], ScenarioResult]
    ) -> None:
        """Frontmatter fields are available in metadata."""
        scenario = load_scenario("file_commands")

        greet = scenario.get_command("greet")
        assert greet is not None
        assert greet.description == "Say hello to someone"
        assert greet.metadata.get("allowed-tools") == "Bash(*), Read(*)"
        assert greet.metadata.get("argument-hint") == "<name>"

    def test_full_content_available(
        self, load_scenario: Callable[[str], ScenarioResult]
    ) -> None:
        """Full file content is stored in content field."""
        scenario = load_scenario("file_commands")

        greet = scenario.get_command("greet")
        assert greet is not None
        assert greet.content is not None
        assert "# Greet Command" in greet.content
        assert "Hello $ARGUMENTS" in greet.content


class TestMixedConfig:
    """
    Scenario: Mixed Configuration

    Given: Both inline and file-based definitions
    Then: All are discovered without duplicates
    """

    def test_total_count(self, load_scenario: Callable[[str], ScenarioResult]) -> None:
        """Total of 6 customizations discovered."""
        scenario = load_scenario("mixed_config")

        # 2 commands + 2 agents + 1 MCP + 1 rules = 6
        assert len(scenario) == 6

    def test_discovers_both_command_sources(
        self, load_scenario: Callable[[str], ScenarioResult]
    ) -> None:
        """Both inline and file-based commands are discovered."""
        scenario = load_scenario("mixed_config")

        assert len(scenario.commands) == 2
        assert "inline-cmd" in scenario.names
        assert "file-cmd" in scenario.names

    def test_discovers_both_agent_sources(
        self, load_scenario: Callable[[str], ScenarioResult]
    ) -> None:
        """Both inline and file-based agents are discovered."""
        scenario = load_scenario("mixed_config")

        assert len(scenario.agents) == 2
        assert "inline-agent" in scenario.names
        assert "file-agent" in scenario.names

    def test_discovers_mcp(
        self, load_scenario: Callable[[str], ScenarioResult]
    ) -> None:
        """MCP server is discovered."""
        scenario = load_scenario("mixed_config")

        assert len(scenario.mcps) == 1
        sqlite = scenario.get("sqlite")
        assert sqlite is not None
        assert sqlite.type == CustomizationType.MCP

    def test_discovers_rules(
        self, load_scenario: Callable[[str], ScenarioResult]
    ) -> None:
        """AGENTS.md is discovered as rules."""
        scenario = load_scenario("mixed_config")

        assert len(scenario.rules) == 1

    def test_all_project_level(
        self, load_scenario: Callable[[str], ScenarioResult]
    ) -> None:
        """All customizations are at PROJECT level."""
        scenario = load_scenario("mixed_config")

        for c in scenario:
            assert c.level == ConfigLevel.PROJECT


class TestFileReferences:
    """
    Scenario: File References

    Given: opencode.json with {file:./path} patterns
    Then: Patterns are resolved to file contents
    """

    def test_discovers_agent_and_command(
        self, load_scenario: Callable[[str], ScenarioResult]
    ) -> None:
        """One agent and one command are discovered."""
        scenario = load_scenario("file_references")

        assert len(scenario.agents) == 1
        assert len(scenario.commands) == 1

    def test_agent_prompt_resolved(
        self, load_scenario: Callable[[str], ScenarioResult]
    ) -> None:
        """Agent prompt contains resolved file content."""
        scenario = load_scenario("file_references")

        agent = scenario.get_agent("custom-agent")
        assert agent is not None
        assert agent.content is not None

        # Content from prompts/agent.txt should be present
        assert "You are a custom agent" in agent.content
        assert "Help users with tasks" in agent.content

        # {file:...} pattern should NOT be present
        assert "{file:" not in agent.content

    def test_command_template_resolved(
        self, load_scenario: Callable[[str], ScenarioResult]
    ) -> None:
        """Command template contains resolved file content."""
        scenario = load_scenario("file_references")

        cmd = scenario.get_command("custom-cmd")
        assert cmd is not None
        assert cmd.content is not None

        # Content from templates/cmd.txt should be present
        assert "Execute the following steps" in cmd.content
        assert "Check the current status" in cmd.content

        # {file:...} pattern should NOT be present
        assert "{file:" not in cmd.content


class TestSkillsWithTree:
    """
    Scenario: Skills with File Tree

    Given: .opencode/skill/my-skill/ with nested files
    Then: Skill is discovered with file tree metadata
    """

    def test_discovers_one_skill(
        self, load_scenario: Callable[[str], ScenarioResult]
    ) -> None:
        """One skill is discovered."""
        scenario = load_scenario("skills_with_tree")

        assert len(scenario.skills) == 1
        assert "my-skill" in scenario.names

    def test_skill_name_from_frontmatter(
        self, load_scenario: Callable[[str], ScenarioResult]
    ) -> None:
        """Skill name comes from frontmatter."""
        scenario = load_scenario("skills_with_tree")

        skill = scenario.get_skill("my-skill")
        assert skill is not None
        assert skill.name == "my-skill"

    def test_skill_description(
        self, load_scenario: Callable[[str], ScenarioResult]
    ) -> None:
        """Skill description from frontmatter."""
        scenario = load_scenario("skills_with_tree")

        skill = scenario.get_skill("my-skill")
        assert skill is not None
        assert "nested file structure" in skill.description

    def test_skill_content_available(
        self, load_scenario: Callable[[str], ScenarioResult]
    ) -> None:
        """SKILL.md content is available."""
        scenario = load_scenario("skills_with_tree")

        skill = scenario.get_skill("my-skill")
        assert skill is not None
        assert skill.content is not None
        assert "# My Skill" in skill.content

    def test_skill_has_files_metadata(
        self, load_scenario: Callable[[str], ScenarioResult]
    ) -> None:
        """Skill metadata contains files tree."""
        scenario = load_scenario("skills_with_tree")

        skill = scenario.get_skill("my-skill")
        assert skill is not None
        assert "files" in skill.metadata

        files = skill.metadata["files"]
        assert isinstance(files, list)
        assert len(files) > 0

        # Verify files are SkillFile objects with expected attributes
        first_file = files[0]
        assert hasattr(first_file, "name")
        assert hasattr(first_file, "path")

    def test_skill_files_include_nested(
        self, load_scenario: Callable[[str], ScenarioResult]
    ) -> None:
        """Skill files include nested directories and files."""
        scenario = load_scenario("skills_with_tree")

        skill = scenario.get_skill("my-skill")
        assert skill is not None

        files = skill.metadata["files"]

        # Check for nested structure - find scripts and docs directories
        # files are SkillFile dataclass objects with is_directory attribute
        dir_names = [f.name for f in files if getattr(f, "is_directory", False)]
        assert "scripts" in dir_names or "docs" in dir_names


class TestRichOpencodeJson:
    """
    Scenario: Rich opencode.json Configuration

    Given: An opencode.json with advanced features:
           - Instructions glob pattern (docs/*.md)
           - Inline agents with {file:} references
           - Inline commands with agent overrides
           - Multiple MCP servers (local and remote)
    Then: All items are discovered with resolved content
    """

    def test_total_count(self, load_scenario: Callable[[str], ScenarioResult]) -> None:
        """Correct total count of customizations."""
        scenario = load_scenario("rich_opencode_json")

        # 1 rules (from instructions) + 1 agent + 2 commands + 3 MCPs = 7
        assert len(scenario) == 7

    def test_discovers_rules_from_instructions_glob(
        self, load_scenario: Callable[[str], ScenarioResult]
    ) -> None:
        """Instructions glob pattern discovers docs/*.md as rules."""
        scenario = load_scenario("rich_opencode_json")

        assert len(scenario.rules) == 1
        rules_names = {r.name for r in scenario.rules}
        # Name includes path from glob pattern
        assert "docs/api-standards.md" in rules_names

    def test_discovers_inline_agent(
        self, load_scenario: Callable[[str], ScenarioResult]
    ) -> None:
        """Inline agent is discovered with correct properties."""
        scenario = load_scenario("rich_opencode_json")

        assert len(scenario.agents) == 1
        agent = scenario.get_agent("inline-security-auditor")
        assert agent is not None
        assert agent.description == "Reviews code for security vulnerabilities"
        assert agent.metadata.get("mode") == "subagent"

    def test_agent_file_reference_resolved(
        self, load_scenario: Callable[[str], ScenarioResult]
    ) -> None:
        """Agent prompt {file:} reference is resolved to actual content."""
        scenario = load_scenario("rich_opencode_json")

        agent = scenario.get_agent("inline-security-auditor")
        assert agent is not None
        assert agent.content is not None

        # Should contain content from prompts/security-audit.txt
        assert "security auditor" in agent.content.lower()
        assert "Hardcoded secrets" in agent.content

        # {file:...} pattern should NOT be present
        assert "{file:" not in agent.content

    def test_discovers_two_commands(
        self, load_scenario: Callable[[str], ScenarioResult]
    ) -> None:
        """Two inline commands are discovered."""
        scenario = load_scenario("rich_opencode_json")

        assert len(scenario.commands) == 2
        assert "inline-lint" in scenario.names
        assert "inline-echo" in scenario.names

    def test_command_with_agent_override(
        self, load_scenario: Callable[[str], ScenarioResult]
    ) -> None:
        """Command with agent override has correct metadata."""
        scenario = load_scenario("rich_opencode_json")

        lint = scenario.get_command("inline-lint")
        assert lint is not None
        assert lint.metadata.get("agent") == "plan"

    def test_command_with_arguments(
        self, load_scenario: Callable[[str], ScenarioResult]
    ) -> None:
        """Command template contains $ARGUMENTS placeholder."""
        scenario = load_scenario("rich_opencode_json")

        echo = scenario.get_command("inline-echo")
        assert echo is not None
        assert echo.content is not None
        assert "$ARGUMENTS" in echo.content

    def test_discovers_three_mcps(
        self, load_scenario: Callable[[str], ScenarioResult]
    ) -> None:
        """Three MCP servers are discovered."""
        scenario = load_scenario("rich_opencode_json")

        assert len(scenario.mcps) == 3
        mcp_names = {m.name for m in scenario.mcps}
        assert mcp_names == {"sqlite", "github", "sentry"}

    def test_mcp_local_type(
        self, load_scenario: Callable[[str], ScenarioResult]
    ) -> None:
        """Local MCP has correct type and command."""
        scenario = load_scenario("rich_opencode_json")

        sqlite = scenario.get("sqlite")
        assert sqlite is not None
        assert sqlite.metadata.get("type") == "local"
        assert "uvx" in str(sqlite.metadata.get("command", []))

    def test_mcp_with_environment(
        self, load_scenario: Callable[[str], ScenarioResult]
    ) -> None:
        """MCP with environment config has env vars."""
        scenario = load_scenario("rich_opencode_json")

        github = scenario.get("github")
        assert github is not None
        assert "environment" in github.metadata

    def test_mcp_remote_type(
        self, load_scenario: Callable[[str], ScenarioResult]
    ) -> None:
        """Remote MCP has correct type and URL."""
        scenario = load_scenario("rich_opencode_json")

        sentry = scenario.get("sentry")
        assert sentry is not None
        assert sentry.metadata.get("type") == "remote"
        assert "url" in sentry.metadata


class TestComplex:
    """
    Scenario: Complex Configuration

    Given: A project with ALL customization types:
           - AGENTS.md rules
           - opencode.json with inline definitions + MCPs + instructions
           - File-based agents, commands, skills
           - TypeScript tools and plugins
    Then: All customizations discovered without duplicates
    """

    def test_total_count(self, load_scenario: Callable[[str], ScenarioResult]) -> None:
        """Total of 12 customizations discovered."""
        scenario = load_scenario("complex")

        # 2 rules + 2 agents + 3 commands + 1 skill + 2 MCPs + 1 tool + 1 plugin = 12
        assert len(scenario) == 12

    def test_all_types_present(
        self, load_scenario: Callable[[str], ScenarioResult]
    ) -> None:
        """All 7 customization types are present."""
        from lazyopencode.models.customization import CustomizationType

        scenario = load_scenario("complex")

        expected_types = {
            CustomizationType.RULES,
            CustomizationType.AGENT,
            CustomizationType.COMMAND,
            CustomizationType.SKILL,
            CustomizationType.MCP,
            CustomizationType.TOOL,
            CustomizationType.PLUGIN,
        }
        assert scenario.types == expected_types

    def test_discovers_rules(
        self, load_scenario: Callable[[str], ScenarioResult]
    ) -> None:
        """Discovers AGENTS.md and instructions glob as rules."""
        scenario = load_scenario("complex")

        assert len(scenario.rules) == 2
        rules_names = {r.name for r in scenario.rules}
        assert "AGENTS.md" in rules_names
        # Glob pattern rules include path prefix
        assert "docs/guidelines.md" in rules_names

    def test_discovers_agents_from_both_sources(
        self, load_scenario: Callable[[str], ScenarioResult]
    ) -> None:
        """Discovers both inline and file-based agents."""
        scenario = load_scenario("complex")

        assert len(scenario.agents) == 2
        agent_names = {a.name for a in scenario.agents}
        assert "inline-auditor" in agent_names
        assert "reviewer" in agent_names

    def test_discovers_commands_from_both_sources(
        self, load_scenario: Callable[[str], ScenarioResult]
    ) -> None:
        """Discovers both inline and file-based commands."""
        scenario = load_scenario("complex")

        assert len(scenario.commands) == 3
        cmd_names = {c.name for c in scenario.commands}
        assert "inline-echo" in cmd_names
        assert "inline-build" in cmd_names
        assert "verify" in cmd_names

    def test_discovers_skill_with_files(
        self, load_scenario: Callable[[str], ScenarioResult]
    ) -> None:
        """Discovers skill with nested file tree."""
        scenario = load_scenario("complex")

        assert len(scenario.skills) == 1
        skill = scenario.get_skill("deploy-helper")
        assert skill is not None
        assert skill.description == "Helps with deployment tasks and scripts"

        # Should have files metadata
        assert "files" in skill.metadata
        files = skill.metadata["files"]
        assert len(files) > 0

    def test_discovers_mcps(
        self, load_scenario: Callable[[str], ScenarioResult]
    ) -> None:
        """Discovers MCP servers from opencode.json."""
        scenario = load_scenario("complex")

        assert len(scenario.mcps) == 2
        mcp_names = {m.name for m in scenario.mcps}
        assert mcp_names == {"sqlite", "filesystem"}

    def test_discovers_tool(
        self, load_scenario: Callable[[str], ScenarioResult]
    ) -> None:
        """Discovers TypeScript tool with description."""
        scenario = load_scenario("complex")

        assert len(scenario.tools) == 1
        tool = scenario.get("search")
        assert tool is not None
        assert "Search for files" in tool.description

    def test_discovers_plugin(
        self, load_scenario: Callable[[str], ScenarioResult]
    ) -> None:
        """Discovers TypeScript plugin with exports."""
        scenario = load_scenario("complex")

        assert len(scenario.plugins) == 1
        plugin = scenario.get("metrics")
        assert plugin is not None
        assert "exports" in plugin.metadata
        assert "MetricsPlugin" in plugin.metadata["exports"]

    def test_plugin_has_hooks(
        self, load_scenario: Callable[[str], ScenarioResult]
    ) -> None:
        """Plugin metadata contains extracted hooks."""
        scenario = load_scenario("complex")

        plugin = scenario.get("metrics")
        assert plugin is not None
        assert "hooks" in plugin.metadata

        hooks = plugin.metadata["hooks"]
        assert len(hooks) > 0

    def test_inline_agent_file_reference_resolved(
        self, load_scenario: Callable[[str], ScenarioResult]
    ) -> None:
        """Inline agent prompt has resolved file content."""
        scenario = load_scenario("complex")

        agent = scenario.get_agent("inline-auditor")
        assert agent is not None
        assert agent.content is not None

        # Content from prompts/auditor.txt
        assert "code auditor" in agent.content.lower()
        assert "{file:" not in agent.content

    def test_file_based_agent_has_frontmatter(
        self, load_scenario: Callable[[str], ScenarioResult]
    ) -> None:
        """File-based agent has parsed frontmatter."""
        scenario = load_scenario("complex")

        reviewer = scenario.get_agent("reviewer")
        assert reviewer is not None
        assert reviewer.description == "Reviews pull requests and provides feedback"
        assert reviewer.metadata.get("mode") == "subagent"

    def test_no_duplicates(
        self, load_scenario: Callable[[str], ScenarioResult]
    ) -> None:
        """No duplicate customization names within same type."""
        scenario = load_scenario("complex")

        # Check each type has unique names
        for ctype in scenario.types:
            items = scenario.by_type(ctype)
            names = [item.name for item in items]
            assert len(names) == len(set(names)), f"Duplicates in {ctype}"
