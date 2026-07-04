#!/usr/bin/env python3
"""Serve the G-code workflow UI over HTTP."""

from __future__ import annotations

import argparse
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path


class WorkflowHandler(SimpleHTTPRequestHandler):
    def end_headers(self) -> None:
        self.send_header("Cache-Control", "no-store")
        super().end_headers()


def main() -> int:
    parser = argparse.ArgumentParser(description="Serve the G-code node workflow page.")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind. Default: 127.0.0.1")
    parser.add_argument("--port", default=8765, type=int, help="Port to bind. Default: 8765")
    args = parser.parse_args()

    root = Path(__file__).resolve().parent
    handler = lambda *handler_args, **handler_kwargs: WorkflowHandler(  # noqa: E731
        *handler_args,
        directory=str(root),
        **handler_kwargs,
    )

    server = ThreadingHTTPServer((args.host, args.port), handler)
    print(f"Serving G-code workflow at http://{args.host}:{args.port}/")
    print("Press Ctrl+C to stop.")
    server.serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
