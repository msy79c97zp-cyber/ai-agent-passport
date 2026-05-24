"""
Machine-to-machine (M2M) billing and credit tracking.

This module owns all prepaid credit logic:
- Checking balance before a verification lookup
- Deducting credits per verification
- Refilling credits after a machine-wallet payment webhook
"""

from uuid import UUID

from fastapi import HTTPException, status
from supabase import Client

from app.billing_constants import (
    PAYMENT_REQUIRED_MESSAGE,
    REFILL_CREDITS_AMOUNT,
    VERIFICATION_CREDIT_COST,
)
from app.models import RefillCreditsResponse

# Same table the agent service uses — one row per agent account.
AGENTS_TABLE = "agents"


class BillingService:
    """Handles prepaid credit checks, deductions, and refills."""

    def __init__(self, client: Client) -> None:
        self.client = client

    def ensure_can_verify(self, credit_balance: int) -> None:
        """
        Block verification when the agent has no credits left.

        Raises:
            HTTPException: HTTP 402 when `credit_balance` is zero or less.
        """
        if credit_balance <= 0:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail=PAYMENT_REQUIRED_MESSAGE,
            )

    def deduct_verification_credit(
        self,
        agent_id: UUID,
        current_balance: int,
    ) -> int:
        """
        Subtract one credit for a passport validation and persist the change.

        Call `ensure_can_verify` first so agents with zero balance are
        rejected before any deduction happens.

        Returns:
            The agent's updated credit balance after the deduction.
        """
        new_balance = current_balance - VERIFICATION_CREDIT_COST

        response = (
            self.client.table(AGENTS_TABLE)
            .update({"credit_balance": new_balance})
            .eq("id", str(agent_id))
            .execute()
        )

        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to deduct verification credit. Please try again.",
            )

        return new_balance

    def refill_credits(self, agent_id: UUID) -> RefillCreditsResponse:
        """
        Add prepaid credits after a successful machine-wallet payment.

        This is invoked by the `/refill-credits` webhook when Stripe MPP
        confirms that an invoice was settled.
        """
        agent = self._get_agent_or_404(agent_id)
        current_balance = int(agent.get("credit_balance", 0))
        new_balance = current_balance + REFILL_CREDITS_AMOUNT

        response = (
            self.client.table(AGENTS_TABLE)
            .update({"credit_balance": new_balance})
            .eq("id", str(agent_id))
            .execute()
        )

        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to refill credits. Please try again.",
            )

        return RefillCreditsResponse(
            agent_id=agent_id,
            credits_added=REFILL_CREDITS_AMOUNT,
            credit_balance=new_balance,
            message=(
                f"Successfully added {REFILL_CREDITS_AMOUNT} credits via "
                "Stripe Machine Payments Protocol (MPP)."
            ),
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
