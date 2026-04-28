"""Standalone test - tries to call YNAB API directly from Vercel."""
import os
import json
import httpx
from http.server import BaseHTTPRequestHandler


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        token = os.environ.get("YNAB_API_TOKEN", "MISSING")
        
        try:
            response = httpx.get(
                "https://api.ynab.com/v1/plans",
                headers={
                    "Authorization": f"Bearer {token}",
                    "User-Agent": "python-httpx/0.28.1",
                },
                timeout=30.0,
            )
            
            result = {
                "status_code": response.status_code,
                "headers_sent": dict(response.request.headers),
                "response_body": response.text[:500],
                "ynab_response_headers": dict(response.headers),
            }
        except Exception as e:
            result = {"error": str(e), "type": type(e).__name__}
        
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(result, indent=2, default=str).encode())
