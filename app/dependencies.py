"""
Shared FastAPI dependencies.

Dependencies are reusable building blocks injected into route handlers.
They keep routers small and make testing easier.
"""

from functools import lru_cache

from app.config import Settings, get_settings
from app.database import get_supabase_client
from app.services.agent_service import AgentService


@lru_cache
def get_settings_dependency() -> Settings:
    """Cached settings object for dependency injection."""
    return get_settings()


def get_agent_service() -> AgentService:
    """Provide an AgentService wired to the Supabase client."""
    settings = get_settings_dependency()
    client = get_supabase_client()
    return AgentService(client=client, settings=settings)
