"""
routers/__init__.py — Exports all FastAPI router instances.
"""

from routers.actions import router as actions_router
from routers.auth import router as auth_router
from routers.briefing import router as briefing_router
from routers.chat import router as chat_router
from routers.oauth import router as oauth_router
from routers.settings import router as settings_router

__all__ = [
    "auth_router",
    "oauth_router",
    "briefing_router",
    "chat_router",
    "actions_router",
    "settings_router",
]
