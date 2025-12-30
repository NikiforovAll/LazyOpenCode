import json
from pathlib import Path

import pytest

from lazyopencode.models.customization import ConfigLevel, CustomizationType
from lazyopencode.services.discovery import ConfigDiscoveryService
from lazyopencode.services.parsers.agent import AgentParser
from lazyopencode.services.parsers.command import CommandParser
from lazyopencode.services.parsers.mcp import MCPParser


def test_parse_inline_commands(tmp_path):
    # Create a dummy opencode.json
    config_path = tmp_path / "opencode.json"
    config = {
        "command": {
            "test-cmd": {
                "template": "Hello $ARGUMENTS",
                "description": "Test command",
                "agent": "test-agent",
            }
        }
    }
    config_path.write_text(json.dumps(config))

    parser = CommandParser()
    customizations = parser.parse_inline_commands(config_path, ConfigLevel.PROJECT)

    assert len(customizations) == 1
    cmd = customizations[0]
    assert cmd.name == "test-cmd"
    assert cmd.type == CustomizationType.COMMAND
    assert cmd.description == "Test command"
    assert cmd.content is not None
    assert "description: Test command" in cmd.content
    assert "agent: test-agent" in cmd.content
    assert "Hello $ARGUMENTS" in cmd.content
    assert cmd.content.startswith("---")

    # Verify the pattern matches what detail_pane.py expects
    # Pattern: ^---\s*\n(.*?)\n---\s*\n(.*)$
    import re

    pattern = r"^---\s*\n(.*?)\n---\s*\n(.*)$"
    match = re.match(pattern, cmd.content, re.DOTALL)
    assert match is not None, "Content should match frontmatter pattern"
    assert "Hello $ARGUMENTS" in match.group(2)  # Body
    assert "agent: test-agent" in match.group(1)  # Frontmatter

    # Verify metadata DOES NOT contain template
    assert "template" not in cmd.metadata
    assert cmd.metadata["agent"] == "test-agent"


def test_parse_inline_agents(tmp_path):
    config_path = tmp_path / "opencode.json"
    config = {
        "agent": {"test-agent": {"prompt": "You are a test agent", "mode": "subagent"}}
    }
    config_path.write_text(json.dumps(config))

    parser = AgentParser()
    customizations = parser.parse_inline_agents(config_path, ConfigLevel.PROJECT)

    assert len(customizations) == 1
    agent = customizations[0]
    assert agent.name == "test-agent"
    assert agent.content is not None
    assert "mode: subagent" in agent.content
    assert "You are a test agent" in agent.content

    # Verify metadata DOES NOT contain prompt
    assert "prompt" not in agent.metadata
    assert agent.metadata["mode"] == "subagent"


def test_jsonc_stripping_with_urls(tmp_path):
    config_path = tmp_path / "opencode.json"
    content = """
    {
        "mcp": {
            "github": {
                "type": "remote",
                "url": "https://mcp.sentry.dev/mcp" // This should NOT be stripped
            }
        },
        "command": {
            "test": {
                "template": "foo" // This SHOULD be stripped
            }
        }
    }
    """
    config_path.write_text(content)

    # Test CommandParser
    parser = CommandParser()
    customizations = parser.parse_inline_commands(config_path, ConfigLevel.PROJECT)
    assert len(customizations) == 1

    # Test MCPParser
    mcp_parser = MCPParser()
    mcps = mcp_parser.parse_mcps(config_path, ConfigLevel.PROJECT)
    assert len(mcps) == 1
    assert mcps[0].name == "github"
    assert mcps[0].metadata.get("url") == "https://mcp.sentry.dev/mcp"


def test_discovery_integration(tmp_path):
    project_root = tmp_path / "project"
    global_root = tmp_path / "global"
    project_root.mkdir()
    global_root.mkdir()

    config = {
        "command": {"inline-cmd": {"template": "cmd"}},
        "agent": {"inline-agent": {"prompt": "agent"}},
    }
    (project_root / "opencode.json").write_text(json.dumps(config))
    (global_root / "opencode.json").write_text(json.dumps(config))

    discovery = ConfigDiscoveryService(
        project_root=project_root, global_config_path=global_root
    )
    customizations = discovery.discover_all()

    commands = [c for c in customizations if c.type == CustomizationType.COMMAND]
    agents = [c for c in customizations if c.type == CustomizationType.AGENT]

    assert len(commands) == 2
    assert len(agents) == 2


def test_parse_reference_config():
    ref_path = Path("reference-customizations/opencode.json")
    if not ref_path.exists():
        pytest.skip("Reference config not found")

    parser = CommandParser()
    commands = parser.parse_inline_commands(ref_path, ConfigLevel.PROJECT)
    assert any(c.name == "inline-lint" for c in commands)
    lint_cmd = next(c for c in commands if c.name == "inline-lint")
    assert "template" not in lint_cmd.metadata

    agent_parser = AgentParser()
    agents = agent_parser.parse_inline_agents(ref_path, ConfigLevel.PROJECT)
    assert any(a.name == "inline-security-auditor" for a in agents)
    security_agent = next(a for a in agents if a.name == "inline-security-auditor")
    assert "prompt" not in security_agent.metadata
