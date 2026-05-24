"""
Database connection helpers.

This module creates a single Supabase client that routers and services
share throughout the application.
"""

from functools import lru_cache

from supabase import Client, create_client

from app.config import get_settings


@lru_cache
def get_supabase_client() -> Client:
    """
    Return a cached Supabase client.

    Using `@lru_cache` means we only create one client for the lifetime
    of the app, which is efficient and avoids repeated connection setup.
    """
    settings = get_settings()
    return create_client(settings.supabase_url, settings.supabase_key)
