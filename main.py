"""
AI Agent Identity Ledger — FastAPI entry point.

Run locally with:
    uvicorn main:app --reload

Interactive API docs:
    http://127.0.0.1:8000/docs
"""

from typing import Dict

from fastapi import FastAPI

from app.routers import billing, register, subscription, verify

# Create the FastAPI application instance.
app = FastAPI(
    title="AI Agent Identity Ledger",
    description=(
        "A simple registry where AI agents can sign up, verify each other's "
        "status, activate paid subscriptions after a free trial, and manage "
        "prepaid verification credits via machine-to-machine billing."
    ),
    version="1.0.0",
)

# Attach feature routers. Each router owns a small group of endpoints.
app.include_router(register.router)
app.include_router(verify.router)
app.include_router(subscription.router)
app.include_router(billing.router)


@app.get("/", tags=["Health"])
def health_check() -> Dict[str, str]:
    """Lightweight endpoint to confirm the API is running."""
    return {"status": "ok", "service": "AI Agent Identity Ledger"}
