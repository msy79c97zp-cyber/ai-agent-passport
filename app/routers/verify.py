"""GET /verify/{agent_id} — public lookup of agent status."""

from uuid import UUID

from fastapi import APIRouter, Depends

from app.models import AgentVerifyResponse
from app.services.agent_service import AgentService
from app.dependencies import get_agent_service

router = APIRouter(tags=["Verification"])


@router.get(
    "/verify/{agent_id}",
    response_model=AgentVerifyResponse,
    summary="Verify an agent's identity status",
)
def verify_agent(
    agent_id: UUID,
    service: AgentService = Depends(get_agent_service),
) -> AgentVerifyResponse:
    """
    Check whether an agent is verified, active, and still within trial.

    Each call costs 1 prepaid credit. When `credit_balance` is zero, the API
    returns HTTP 402 with instructions to refill via Stripe MPP.
    """
    return service.verify_agent(agent_id)
