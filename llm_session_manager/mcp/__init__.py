"""MCP (Model Context Protocol) integration for LLM Session Manager.

This module implements MCP server functionality to expose session data
and operations to MCP-compatible clients like Claude Desktop.
"""

from .server import MCPServer
from .session_server import SessionMCPServer

__all__ = ["MCPServer", "SessionMCPServer"]
