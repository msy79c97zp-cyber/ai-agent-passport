"""GET /verify/{agent_id} - public lookup of agent status."""

import json
from uuid import UUID
from fastapi import APIRouter, Depends, Request
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
    request: Request,
    service: AgentService = Depends(get_agent_service),
) -> AgentVerifyResponse:
    """
    Check whether an agent is verified, active, and still within trial.

    Each call costs 1 prepaid credit. When `credit_balance` is zero, the API
    returns HTTP 402 with instructions to refill via Stripe MPP.
    """
    cache_key = f"agent_passport:{agent_id}"
    redis_client = getattr(request.app.state, "redis", None)

    # 1. Fast Path: Attempt Redis Cache Lookup
    if redis_client:
        try:
            cached_passport = redis_client.get(cache_key)
            if cached_passport:
                print(f"🚀 Cache Hit! Returning passport {agent_id} from Redis under 10ms.")
                return json.loads(cached_passport)
        except Exception as e:
            print(f"⚠️ Redis read error: {e}")

    # 2. Fallback Path: Cache Miss -> Query Supabase via Service Layer
    response = service.verify_agent(agent_id)

    # 3. Background Cache Write: Update Redis for next time
    if redis_client and response:
        try:
            redis_client.setex(cache_key, 3600, response.model_dump_json())
            print(f"💾 Cache Miss. Fetched from database and stored passport in Redis.")
        except Exception as e:
            print(f"⚠️ Redis write error: {e}")

    return response
