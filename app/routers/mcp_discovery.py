"""Router to expose the Model Context Protocol (MCP) discovery file."""

import json
import os
from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter()

# Locate the mcp.json file at the project root directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MCP_JSON_PATH = os.path.join(BASE_DIR, "mcp.json")

@router.get("/.well-known/mcp.json", tags=["Discovery"])
def get_mcp_discovery():
    """
    Expose the standardized mcp.json tool directory to the open internet.
    Enables autonomous agent networks to organically discover your capabilities.
    """
    try:
        with open(MCP_JSON_PATH, "r") as f:
            data = json.load(f)
        return JSONResponse(content=data, status_code=200)
    except Exception as e:
        return JSONResponse(
            content={"detail": f"Failed to load discovery configuration: {str(e)}"},
            status_code=500
        )
