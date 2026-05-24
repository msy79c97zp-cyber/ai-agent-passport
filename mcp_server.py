#!/usr/bin/env python3
"""
AI Agent Passport — Model Context Protocol (MCP) Server

Exposes the hosted Render API as MCP tools so any LLM client (Claude Desktop,
LangChain, Cursor, etc.) can register agents, verify passports, and refill
machine-wallet credits without knowing REST details.

Run locally (stdio transport — used by Claude Desktop):
    python mcp_server.py

Environment variables (see mcp.json for examples):
    PASSPORT_API_URL          Base URL of your Render deployment
    BILLING_WEBHOOK_SECRET    Secret for POST /refill-credits
"""

from typing import Optional

from mcp.server.fastmcp import FastMCP

from mcp_client.api_client import PassportAPIClient
from mcp_client.tools import (
    refill_agent_credits as _refill_agent_credits,
    register_agent as _register_agent,
    verify_agent_passport as _verify_agent_passport,
)

# ---------------------------------------------------------------------------
# MCP server instance
# ---------------------------------------------------------------------------

# Name shown to LLM clients when they list connected MCP servers.
mcp = FastMCP(
    "AI Agent Passport",
    instructions=(
        "Tools for the AI Agent Identity Ledger on Render. "
        "Use register_agent to create passports, verify_agent_passport to "
        "check status (costs 1 credit), refill_agent_credits after MPP payment."
    ),
)

# Shared API client — created once, reused by every tool call.
_api_client = PassportAPIClient()


# ---------------------------------------------------------------------------
# Tool: register_agent
# ---------------------------------------------------------------------------


@mcp.tool()
async def register_agent(
    agent_name: str,
    description: Optional[str] = None,
) -> str:
    """
    Register a new agent identity passport on the AI Agent Passport ledger.

    Returns compact JSON with agent_id, status, credit_balance (50),
    created_at, and trial_ends_at (7 days from creation).
    """
    return await _register_agent(
        client=_api_client,
        agent_name=agent_name,
        description=description,
    )


# ---------------------------------------------------------------------------
# Tool: verify_agent_passport
# ---------------------------------------------------------------------------


@mcp.tool()
async def verify_agent_passport(agent_id: str) -> str:
    """
    Check if an agent ID is active, paid or on trial, and whether trial expired.

    Returns is_active, is_verified, status, trial_expired, credit_balance.
    Deducts 1 prepaid credit from the target agent. HTTP 402 if balance is 0.
    """
    return await _verify_agent_passport(client=_api_client, agent_id=agent_id)


# ---------------------------------------------------------------------------
# Tool: refill_agent_credits
# ---------------------------------------------------------------------------


@mcp.tool()
async def refill_agent_credits(agent_id: str) -> str:
    """
    Trigger machine-wallet credit refill (+5000) after Stripe MPP payment.

    Returns credits_added, new credit_balance, and confirmation message.
    Webhook secret is read from server env — do not pass it as an argument.
    """
    return await _refill_agent_credits(client=_api_client, agent_id=agent_id)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # stdio is the standard transport for Claude Desktop and most local MCP hosts.
    mcp.run(transport="stdio")
