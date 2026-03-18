#!/usr/bin/env python3
"""Lightweight HTTP tool execution server — runs inside vnc_target."""
import asyncio
import json
import os
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer

os.environ.setdefault("DISPLAY", ":1")

from computer_use_demo.tools import (
    BashTool20250124,
    ComputerTool20250124,
    EditTool20250728,
    ToolCollection,
)

tools = ToolCollection(
    ComputerTool20250124(),
    BashTool20250124(),
    EditTool20250728(),
)


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/health":
            self._json(200, {"status": "ok"})
        elif self.path == "/tools":
            self._json(200, [t.to_params() for t in tools.tools])
        else:
            self._json(404, {"error": "not found"})

    def do_POST(self):
        if self.path != "/execute":
            self._json(404, {"error": "not found"})
            return
        body = json.loads(
            self.rfile.read(int(self.headers.get("Content-Length", 0)))
        )
        try:
            result = asyncio.run(
                tools.run(name=body["name"], tool_input=body.get("input", {}))
            )
            resp = {}
            if result.output:
                resp["output"] = result.output
            if result.error:
                resp["error"] = result.error
            if result.base64_image:
                resp["base64_image"] = result.base64_image
            if result.system:
                resp["system"] = result.system
            self._json(200, resp)
        except Exception as e:
            self._json(500, {"error": str(e)})

    def _json(self, code, data):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def log_message(self, format, *args):
        pass


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8888
    srv = HTTPServer(("0.0.0.0", port), Handler)
    print(f"Tool server listening on :{port}", flush=True)
    srv.serve_forever()
