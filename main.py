import os
from fastapi import FastAPI
import redis
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

# Initialize Redis connection pool on startup
@app.on_event("startup")
def startup_event():
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
    # decode_responses=True automatically formats binary data back into clean strings
    app.state.redis = redis.Redis.from_url(redis_url, decode_responses=True)
    print("⚡ Redis Valet Caching Pool Initialized Successfully!")

# Storefront at GET / - must be registered before other routers if paths overlap.
app.include_router(storefront.router)
app.include_router(register.router)
app.include_router(verify.router)
app.include_router(subscription.router)
app.include_router(billing.router)
