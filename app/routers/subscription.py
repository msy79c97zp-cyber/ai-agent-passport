"""POST /activate-subscription — upgrade an agent to paid status."""

from fastapi import APIRouter, Depends

from app.models import ActivateSubscriptionRequest, ActivateSubscriptionResponse
from app.services.agent_service import AgentService
from app.dependencies import get_agent_service

router = APIRouter(tags=["Billing"])


@router.post(
    "/activate-subscription",
    response_model=ActivateSubscriptionResponse,
    summary="Activate a paid subscription",
)
def activate_subscription(
    payload: ActivateSubscriptionRequest,
    service: AgentService = Depends(get_agent_service),
) -> ActivateSubscriptionResponse:
    """
    Move an agent from `trial` to `paid` once their free trial has ended.
    """
    return service.activate_subscription(payload.agent_id)
