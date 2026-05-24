"""
MCP tool definitions for the AI Agent Passport ledger.

Each function maps 1:1 to an MCP tool exposed to calling LLM models.
Docstrings become tool descriptions visible in Claude Desktop / LangChain.
"""

from typing import Optional

from mcp_client.api_client import PassportAPIClient, format_tool_error


async def register_agent(
    client: PassportAPIClient,
    agent_name: str,
    description: Optional[str] = None,
) -> str:
    """
    Register a new agent identity passport on the AI Agent Passport ledger.

    Use when an AI agent needs a unique ID, trial window, and starting credits.
    Returns agent_id (UUID), status, credit_balance (50), and trial_ends_at.

    Args:
        agent_name: Human-readable name (1-100 chars).
        description: Optional summary of the agent's purpose (max 500 chars).
    """
    try:
        result = await client.register_agent(
            agent_name=agent_name,
            description=description,
        )
        return result
    except Exception as exc:
        return format_tool_error(exc)


async def verify_agent_passport(
    client: PassportAPIClient,
    agent_id: str,
) -> str:
    """
    Verify another agent's passport: active, paid/trial status, and expiry.

    Checks is_active, is_verified, status (trial|paid), trial_expired,
    and remaining credit_balance. Costs 1 credit from the target agent.
    Returns HTTP 402 JSON if their prepaid balance is zero.

    Args:
        agent_id: UUID of the agent to look up.
    """
    try:
        result = await client.verify_agent_passport(agent_id=agent_id)
        return result
    except Exception as exc:
        return format_tool_error(exc)


async def refill_agent_credits(
    client: PassportAPIClient,
    agent_id: str,
) -> str:
    """
    Refill an agent's machine-wallet prepaid credits after Stripe MPP payment.

    Adds 5000 credits to the agent's balance. Requires BILLING_WEBHOOK_SECRET
    configured in the MCP server environment (not passed by the LLM).

    Args:
        agent_id: UUID of the agent whose credits should be refilled.
    """
    try:
        result = await client.refill_agent_credits(agent_id=agent_id)
        return result
    except Exception as exc:
        return format_tool_error(exc)
