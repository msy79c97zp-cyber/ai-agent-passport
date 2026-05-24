"""
MCP server configuration — loaded from environment variables.

The MCP server is a thin client: it calls your hosted Render API rather
than talking to Supabase directly. Set these in Claude Desktop config
or export them before running `python mcp_server.py`.
"""

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class MCPSettings:
    """Connection details for the live AI Agent Passport API."""

    # Base URL of the Render deployment (no trailing slash).
    api_base_url: str

    # Required for POST /refill-credits (Stripe MPP machine-wallet webhook).
    billing_webhook_secret: str

    # HTTP timeout in seconds for upstream API calls.
    request_timeout_seconds: float = 30.0


def get_mcp_settings() -> MCPSettings:
    """
    Build settings from environment variables.

    Required:
        PASSPORT_API_URL — e.g. https://ai-agent-passport.onrender.com
        BILLING_WEBHOOK_SECRET — same secret configured on Render

    Raises:
        ValueError: If required variables are missing.
    """
    api_base_url = os.getenv("PASSPORT_API_URL", "").strip().rstrip("/")
    billing_webhook_secret = os.getenv("BILLING_WEBHOOK_SECRET", "").strip()

    if not api_base_url:
        raise ValueError(
            "PASSPORT_API_URL is not set. "
            "Example: https://ai-agent-passport.onrender.com"
        )

    if not billing_webhook_secret:
        raise ValueError(
            "BILLING_WEBHOOK_SECRET is not set. "
            "Use the same value as your Render deployment."
        )

    return MCPSettings(
        api_base_url=api_base_url,
        billing_webhook_secret=billing_webhook_secret,
    )
