import sys
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from ynab_mcp_server.http_server import app

# Vercel expects either 'app' or 'handler'
# FastMCP's get_asgi_app() already returns ASGI app
