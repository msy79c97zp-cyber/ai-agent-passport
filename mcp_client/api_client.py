"""
HTTP client for the hosted AI Agent Passport API (Render).

All network calls live here so MCP tool handlers stay small and testable.
Responses are returned as compact JSON strings to minimize LLM token usage.
"""

import json
from typing import Any, Dict, Optional

import httpx

from mcp_client.config import MCPSettings, get_mcp_settings


class PassportAPIError(Exception):
    """Raised when the upstream API returns a non-success status code."""

    def __init__(self, status_code: int, detail: str) -> None:
        self.status_code = status_code
        self.detail = detail
        super().__init__(f"HTTP {status_code}: {detail}")


class PassportAPIClient:
    """
    Thin wrapper around the three core Passport REST endpoints.

    Each method returns a minified JSON string — easy for models to parse.
    """

    def __init__(self, settings: Optional[MCPSettings] = None) -> None:
        self.settings = settings or get_mcp_settings()

    async def register_agent(
        self,
        agent_name: str,
        description: Optional[str] = None,
    ) -> str:
        """
        POST /register — create a new agent identity passport.

        Returns JSON with: agent_id, status, credit_balance, trial_ends_at, ...
        """
        payload: Dict[str, Any] = {"agent_name": agent_name}
        if description:
            payload["description"] = description

        data = await self._request("POST", "/register", json_body=payload)
        return self._compact_json(data)

    async def verify_agent_passport(self, agent_id: str) -> str:
        """
        GET /verify/{agent_id} — check active, paid, trial, and credit status.

        Costs 1 prepaid credit on the target agent's account.
        Returns HTTP 402 JSON if their balance is exhausted.
        """
        data = await self._request("GET", f"/verify/{agent_id}")
        return self._compact_json(data)

    async def refill_agent_credits(self, agent_id: str) -> str:
        """
        POST /refill-credits — machine-wallet top-up (+5000 credits).

        Sends the billing webhook secret required by the Render API.
        """
        data = await self._request(
            "POST",
            "/refill-credits",
            json_body={"agent_id": agent_id},
            extra_headers={
                "X-Billing-Webhook-Secret": self.settings.billing_webhook_secret,
            },
        )
        return self._compact_json(data)

    async def _request(
        self,
        method: str,
        path: str,
        json_body: Optional[Dict[str, Any]] = None,
        extra_headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Execute one HTTP call and normalize success/error payloads."""
        url = f"{self.settings.api_base_url}{path}"
        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        if extra_headers:
            headers.update(extra_headers)

        async with httpx.AsyncClient(
            timeout=self.settings.request_timeout_seconds
        ) as client:
            response = await client.request(method, url, json=json_body, headers=headers)

        if response.is_success:
            return response.json()

        # FastAPI errors use {"detail": "..."}; preserve for the calling LLM.
        try:
            error_body = response.json()
            detail = error_body.get("detail", response.text)
        except ValueError:
            detail = response.text or "Unknown upstream error"

        if isinstance(detail, list):
            detail = json.dumps(detail, separators=(",", ":"))

        raise PassportAPIError(status_code=response.status_code, detail=str(detail))

    @staticmethod
    def _compact_json(data: Dict[str, Any]) -> str:
        """
        Serialize API data with no extra whitespace.

        Compact JSON uses fewer tokens when the result is injected into
        an LLM context window.
        """
        return json.dumps(data, separators=(",", ":"), default=str)


def format_tool_error(error: Exception) -> str:
    """
    Convert exceptions into a consistent JSON error string for LLM tools.

    Using a fixed `ok:false` shape helps models detect failures reliably.
    """
    if isinstance(error, PassportAPIError):
        return json.dumps(
            {
                "ok": False,
                "error": error.detail,
                "status_code": error.status_code,
            },
            separators=(",", ":"),
        )

    return json.dumps(
        {"ok": False, "error": str(error)},
        separators=(",", ":"),
    )
