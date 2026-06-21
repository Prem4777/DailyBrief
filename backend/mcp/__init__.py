"""
mcp/__init__.py — Exports all MCP client classes.
"""

from mcp.gcal_client import GCalMCPClient
from mcp.gmail_client import GmailMCPClient
from mcp.notion_client import NotionMCPClient

__all__ = ["GmailMCPClient", "GCalMCPClient", "NotionMCPClient"]
