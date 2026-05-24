"""
Application configuration.

Loads environment variables from a `.env` file (if present) and exposes
them through a simple Settings object used across the app.
"""

import os
from dataclasses import dataclass

from dotenv import load_dotenv

# Load variables from `.env` into the process environment.
load_dotenv()


@dataclass(frozen=True)
class Settings:
    """Holds all configuration values the app needs to run."""

    supabase_url: str
    supabase_key: str

    # Secret token that machine-wallet webhooks must send to refill credits.
    billing_webhook_secret: str

    # How long a new agent's free trial lasts.
    trial_period_days: int = 7


def get_settings() -> Settings:
    """
    Build and return application settings from environment variables.

    Raises:
        ValueError: If required Supabase credentials are missing.
    """
    supabase_url = os.getenv("SUPABASE_URL", "").strip()
    supabase_key = os.getenv("SUPABASE_KEY", "").strip()
    billing_webhook_secret = os.getenv("BILLING_WEBHOOK_SECRET", "").strip()

    if not supabase_url or not supabase_key:
        raise ValueError(
            "Missing Supabase credentials. "
            "Set SUPABASE_URL and SUPABASE_KEY in your `.env` file."
        )

    if not billing_webhook_secret:
        raise ValueError(
            "Missing billing webhook secret. "
            "Set BILLING_WEBHOOK_SECRET in your `.env` file."
        )

    return Settings(
        supabase_url=supabase_url,
        supabase_key=supabase_key,
        billing_webhook_secret=billing_webhook_secret,
    )
