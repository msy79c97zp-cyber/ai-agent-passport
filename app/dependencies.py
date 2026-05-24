"""
Shared FastAPI dependencies.

Dependencies are reusable building blocks injected into route handlers.
They keep routers small and make testing easier.
"""

from functools import lru_cache

from app.config import Settings, get_settings
from app.database import get_supabase_client
from app.services.agent_service import AgentService
from app.services.billing_service import BillingService
from app.services.stats_service import StatsService


@lru_cache
def get_settings_dependency() -> Settings:
    """Cached settings object for dependency injection."""
    return get_settings()


def get_agent_service() -> AgentService:
    """Provide an AgentService wired to the Supabase client."""
    settings = get_settings_dependency()
    client = get_supabase_client()
    billing_service = BillingService(client)
    return AgentService(
        client=client,
        settings=settings,
        billing_service=billing_service,
    )


def get_billing_service() -> BillingService:
    """Provide a BillingService wired to the Supabase client."""
    client = get_supabase_client()
    return BillingService(client)


def get_stats_service() -> StatsService:
    """Provide a StatsService wired to the Supabase client."""
    client = get_supabase_client()
    return StatsService(client)
