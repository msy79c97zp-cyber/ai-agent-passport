"""Public storefront and ledger statistics endpoints."""

from typing import Dict

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from starlette.templating import Jinja2Templates

from app.billing_constants import DEFAULT_STARTING_CREDITS, REFILL_CREDITS_AMOUNT
from app.dependencies import get_stats_service
from app.paths import TEMPLATES_DIR
from app.services.stats_service import StatsService

router = APIRouter(tags=["Storefront"])

# Absolute path so Render finds templates no matter the working directory.
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


@router.get("/", response_class=HTMLResponse, include_in_schema=False)
def storefront(request: Request) -> HTMLResponse:
    """Serve the developer-first marketing storefront at the root URL."""
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "free_trial_credits": DEFAULT_STARTING_CREDITS,
            "bundle_credits": REFILL_CREDITS_AMOUNT,
            "bundle_price_usd": 10,
        },
    )


@router.get("/health", tags=["Health"])
def health_check() -> Dict[str, str]:
    """Lightweight JSON endpoint to confirm the API is running."""
    return {"status": "ok", "service": "AI Agent Identity Ledger"}


@router.get("/api/ledger/stats", tags=["Storefront"])
def ledger_stats(
    stats_service: StatsService = Depends(get_stats_service),
) -> Dict[str, int]:
    """
    Live ledger statistics for the storefront counter.

    Polled by the homepage JavaScript every few seconds.
    """
    return {
        "verified_active_agents": stats_service.count_verified_active_agents(),
    }
