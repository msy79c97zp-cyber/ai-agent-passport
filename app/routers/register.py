"""POST /register — create a new agent identity with a free trial."""

from fastapi import APIRouter, Depends

from app.models import AgentRegisterRequest, AgentRegisterResponse
from app.services.agent_service import AgentService
from app.dependencies import get_agent_service

router = APIRouter(tags=["Registration"])


@router.post(
    "/register",
    response_model=AgentRegisterResponse,
    summary="Register a new AI agent",
)
def register_agent(
    payload: AgentRegisterRequest,
    service: AgentService = Depends(get_agent_service),
) -> AgentRegisterResponse:
    """
    Sign up a new agent in the identity ledger.

    The server automatically sets:
    - `created_at` to the current UTC time
    - `trial_ends_at` to exactly 7 days after creation
    """
    return service.register_agent(payload)
