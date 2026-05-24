"""
POST /refill-credits — machine-wallet webhook to top up prepaid credits.

Stripe Machine Payments Protocol (MPP) calls this endpoint after an agent
settles an invoice. The shared webhook secret prevents unauthorized refills.
"""

from fastapi import APIRouter, Depends, Header, HTTPException, status

from app.config import Settings
from app.dependencies import get_billing_service, get_settings_dependency
from app.models import RefillCreditsRequest, RefillCreditsResponse
from app.services.billing_service import BillingService

router = APIRouter(tags=["Billing"])


def verify_webhook_secret(
    x_billing_webhook_secret: str = Header(
        ...,
        description="Shared secret proving the request came from Stripe MPP.",
    ),
    settings: Settings = Depends(get_settings_dependency),
) -> None:
    """
    Reject refill requests that do not carry the correct webhook secret.

    Payment providers should send this value in the `X-Billing-Webhook-Secret`
    header on every POST to `/refill-credits`.
    """
    if x_billing_webhook_secret != settings.billing_webhook_secret:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid billing webhook secret.",
        )


@router.post(
    "/refill-credits",
    response_model=RefillCreditsResponse,
    summary="Refill prepaid credits after machine-wallet payment",
    dependencies=[Depends(verify_webhook_secret)],
)
def refill_credits(
    payload: RefillCreditsRequest,
    billing_service: BillingService = Depends(get_billing_service),
) -> RefillCreditsResponse:
    """
    Secure automated checkout webhook for machine-to-machine billing.

    Locates the agent by ID and adds 5000 credits to their balance after
    Stripe MPP confirms payment. Requires the `X-Billing-Webhook-Secret` header.
    """
    return billing_service.refill_credits(payload.agent_id)
