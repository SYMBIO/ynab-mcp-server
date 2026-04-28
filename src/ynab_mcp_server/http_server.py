"""YNAB MCP Server - HTTP/Vercel version with debug logging."""
import os
import logging
import httpx
import yaml
from fastmcp import FastMCP
from fastmcp.server.openapi import MCPType, RouteMap

# Enable httpx debug logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("httpx")
logger.setLevel(logging.DEBUG)

YNAB_API_BASE = "https://api.ynab.com/v1"
YNAB_OPENAPI_SPEC_URL = "https://api.ynab.com/papi/open_api_spec.yaml"

EXCLUDED_ROUTES = [
    RouteMap(
        methods=["GET"],
        pattern=r"^/plans/\{plan_id\}/payees$",
        mcp_type=MCPType.EXCLUDE,
    ),
]

token = os.environ.get("YNAB_API_TOKEN")
if not token:
    raise ValueError("YNAB_API_TOKEN environment variable is required")

spec_response = httpx.get(YNAB_OPENAPI_SPEC_URL)
spec_response.raise_for_status()
openapi_spec = yaml.safe_load(spec_response.text)


# Create event hooks for debugging
async def log_request(request):
    print(f"[YNAB REQUEST] {request.method} {request.url}")
    print(f"[YNAB HEADERS] {dict(request.headers)}")


async def log_response(response):
    print(f"[YNAB RESPONSE] {response.status_code} from {response.url}")
    if response.status_code >= 400:
        await response.aread()
        print(f"[YNAB ERROR BODY] {response.text}")


client = httpx.AsyncClient(
    base_url=YNAB_API_BASE,
    headers={
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
    },
    timeout=30.0,
    event_hooks={
        "request": [log_request],
        "response": [log_response],
    },
)

mcp = FastMCP.from_openapi(
    openapi_spec=openapi_spec,
    client=client,
    name="YNAB MCP Server",
    route_maps=EXCLUDED_ROUTES,
)

app = mcp.http_app(path="/mcp", stateless_http=True)
