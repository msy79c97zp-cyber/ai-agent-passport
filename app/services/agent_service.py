"""
Agent service layer.

Routers stay thin: they validate HTTP input/output while this module
talks to Supabase and implements the ledger rules.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID, uuid4

from fastapi import HTTPException, status
from supabase import Client

from app.config import Settings, get_settings
from app.models import (
    ActivateSubscriptionResponse,
    AgentRegisterRequest,
    AgentRegisterResponse,
    AgentStatus,
    AgentVerifyResponse,
)

# Supabase table name used throughout the app.
AGENTS_TABLE = "agents"


class AgentService:
    """Encapsulates all database operations for agents."""

    def __init__(self, client: Client, settings: Optional[Settings] = None) -> None:
        self.client = client
        self.settings = settings or get_settings()

    def register_agent(self, payload: AgentRegisterRequest) -> AgentRegisterResponse:
        """
        Create a new agent record with a 7-day free trial.

        New agents start as:
        - status: trial
        - is_verified: False (verification can be added later)
        - is_active: True
        """
        agent_id = uuid4()
        created_at = datetime.now(timezone.utc)
        trial_ends_at = created_at + timedelta(days=self.settings.trial_period_days)

        record = {
            "id": str(agent_id),
            "agent_name": payload.agent_name,
            "description": payload.description,
            "status": AgentStatus.TRIAL.value,
            "is_verified": False,
            "is_active": True,
            "created_at": created_at.isoformat(),
            "trial_ends_at": trial_ends_at.isoformat(),
        }

        response = self.client.table(AGENTS_TABLE).insert(record).execute()

        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to register agent. Please try again.",
            )

        return AgentRegisterResponse(
            agent_id=agent_id,
            agent_name=payload.agent_name,
            status=AgentStatus.TRIAL,
            is_verified=False,
            is_active=True,
            created_at=created_at,
            trial_ends_at=trial_ends_at,
        )

    def verify_agent(self, agent_id: UUID) -> AgentVerifyResponse:
        """
        Look up an agent and return their public identity status.

        `trial_expired` is True when the trial window has passed and the
        agent has not upgraded to a paid subscription yet.
        """
        agent = self._get_agent_or_404(agent_id)
        now = datetime.now(timezone.utc)

        created_at = self._parse_timestamp(agent["created_at"])
        trial_ends_at = self._parse_timestamp(agent["trial_ends_at"])
        agent_status = AgentStatus(agent["status"])

        trial_expired = (
            now > trial_ends_at and agent_status != AgentStatus.PAID
        )

        return AgentVerifyResponse(
            agent_id=agent_id,
            agent_name=agent["agent_name"],
            is_verified=agent["is_verified"],
            is_active=agent["is_active"],
            status=agent_status,
            trial_expired=trial_expired,
            created_at=created_at,
            trial_ends_at=trial_ends_at,
        )

    def activate_subscription(self, agent_id: UUID) -> ActivateSubscriptionResponse:
        """
        Upgrade an agent from trial to paid.

        Business rule: activation is only allowed after the free trial ends.
        """
        agent = self._get_agent_or_404(agent_id)
        now = datetime.now(timezone.utc)
        trial_ends_at = self._parse_timestamp(agent["trial_ends_at"])
        current_status = AgentStatus(agent["status"])

        if current_status == AgentStatus.PAID:
            return ActivateSubscriptionResponse(
                agent_id=agent_id,
                status=AgentStatus.PAID,
                message="Subscription is already active.",
            )

        if now <= trial_ends_at:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Free trial has not ended yet. "
                    f"Trial ends at {trial_ends_at.isoformat()}."
                ),
            )

        response = (
            self.client.table(AGENTS_TABLE)
            .update({"status": AgentStatus.PAID.value})
            .eq("id", str(agent_id))
            .execute()
        )

        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to activate subscription. Please try again.",
            )

        return ActivateSubscriptionResponse(
            agent_id=agent_id,
            status=AgentStatus.PAID,
            message="Subscription activated successfully.",
        )

    def _get_agent_or_404(self, agent_id: UUID) -> dict:
        """Fetch a single agent row or raise HTTP 404."""
        response = (
            self.client.table(AGENTS_TABLE)
            .select("*")
            .eq("id", str(agent_id))
            .limit(1)
            .execute()
        )

        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agent '{agent_id}' was not found.",
            )

        return response.data[0]

    @staticmethod
    def _parse_timestamp(value: str) -> datetime:
        """Convert Supabase timestamp strings into timezone-aware datetimes."""
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            return parsed.replace(tzinfo=timezone.utc)
        return parsed
