"""Claude Code integration layer for LazyOpenCode.

This module provides discovery of Claude Code customizations from standard
Claude Code paths (~/.claude/, ./.claude/, plugins).
"""

from lazyopencode.services.claude_code.discovery import ClaudeCodeDiscoveryService

__all__ = ["ClaudeCodeDiscoveryService"]
