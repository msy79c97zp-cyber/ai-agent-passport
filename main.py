"""
AI Agent Identity Ledger — FastAPI entry point.

Run locally with:
    uvicorn main:app --reload

Interactive API docs:
    http://127.0.0.1:8000/docs
"""

from fastapi import FastAPI

from app.routers import billing, register, storefront, subscription, verify

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

# Storefront at GET / — must be registered before other routers if paths overlap.
app.include_router(storefront.router)
app.include_router(register.router)
app.include_router(verify.router)
app.include_router(subscription.router)
app.include_router(billing.router)
