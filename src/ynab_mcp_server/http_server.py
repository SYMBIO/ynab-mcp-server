"""YNAB MCP Server - HTTP/Vercel version."""
import os
import httpx
import yaml
from fastmcp import FastMCP
from fastmcp.server.openapi import MCPType, RouteMap

YNAB_API_BASE = "https://api.ynab.com/v1"
YNAB_OPENAPI_SPEC_URL = "https://api.ynab.com/papi/open_api_spec.yaml"

EXCLUDED_ROUTES = [
    RouteMap(
        methods=["GET"],
        pattern=r"^/budgets/\{budget_id\}/payees$",
        mcp_type=MCPType.EXCLUDE,
    ),
]

token = os.environ.get("YNAB_API_TOKEN")
if not token:
    raise ValueError("YNAB_API_TOKEN environment variable is required")

spec_response = httpx.get(YNAB_OPENAPI_SPEC_URL)
spec_response.raise_for_status()
openapi_spec = yaml.safe_load(spec_response.text)

client = httpx.AsyncClient(
    base_url=YNAB_API_BASE,
    headers={"Authorization": f"Bearer {token}"},
    timeout=30.0,
)

mcp = FastMCP.from_openapi(
    openapi_spec=openapi_spec,
    client=client,
    name="YNAB MCP Server",
    route_maps=EXCLUDED_ROUTES,
)

# MCP endpoint at /mcp (default), stateless mode for Vercel serverless
app = mcp.http_app(path="/mcp", stateless_http=True)
