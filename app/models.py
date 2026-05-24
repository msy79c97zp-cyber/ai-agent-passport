"""
Pydantic models (schemas) for request and response bodies.

Pydantic validates incoming JSON automatically and documents the API
shape for FastAPI's interactive docs at `/docs`.
"""

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class AgentStatus(str, Enum):
    """Possible subscription states for an agent."""

    TRIAL = "trial"
    PAID = "paid"


# ---------------------------------------------------------------------------
# Register
# ---------------------------------------------------------------------------


class AgentRegisterRequest(BaseModel):
    """Data sent when a new agent signs up."""

    agent_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Human-readable name for the agent.",
    )
    description: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Optional short description of what the agent does.",
    )


class AgentRegisterResponse(BaseModel):
    """Returned after a successful registration."""

    agent_id: UUID
    agent_name: str
    status: AgentStatus
    is_verified: bool
    is_active: bool
    created_at: datetime
    trial_ends_at: datetime


# ---------------------------------------------------------------------------
# Verify
# ---------------------------------------------------------------------------


class AgentVerifyResponse(BaseModel):
    """Public lookup result for another agent checking identity status."""

    agent_id: UUID
    agent_name: str
    is_verified: bool
    is_active: bool
    status: AgentStatus
    trial_expired: bool
    created_at: datetime
    trial_ends_at: datetime


# ---------------------------------------------------------------------------
# Activate subscription
# ---------------------------------------------------------------------------


class ActivateSubscriptionRequest(BaseModel):
    """Request body to upgrade an agent from trial to paid."""

    agent_id: UUID = Field(..., description="The agent to activate.")


class ActivateSubscriptionResponse(BaseModel):
    """Returned after a successful subscription activation."""

    agent_id: UUID
    status: AgentStatus
    message: str
