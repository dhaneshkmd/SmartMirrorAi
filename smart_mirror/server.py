from __future__ import annotations

import json
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from smart_mirror import database
from smart_mirror.modules.face_analysis import FaceAnalysisModule
from smart_mirror.modules.makeup_recommendation import MakeupRecommendationEngine
from smart_mirror.modules.product_scanner import ProductScannerModule
from smart_mirror.modules.virtual_try_on import VirtualTryOnModule


ROOT_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = ROOT_DIR / "static"


face_module = FaceAnalysisModule()
makeup_engine = MakeupRecommendationEngine()
product_scanner = ProductScannerModule()
try_on_module = VirtualTryOnModule()


class SmartMirrorRequestHandler(SimpleHTTPRequestHandler):
    server_version = "SmartMirrorPrototype/1.0"

    def do_GET(self) -> None:
        path = urlparse(self.path).path

        if path == "/":
            self._send_file(STATIC_DIR / "index.html", "text/html; charset=utf-8")
            return
        if path.startswith("/static/"):
            self._send_static(path)
            return
        if path == "/api/profile":
            self._send_json(database.fetch_user_profile())
            return
        if path == "/api/outfits":
            self._send_json({"items": database.fetch_outfit_history()})
            return

        self._send_json({"error": "Not found"}, status=404)

    def do_POST(self) -> None:
        path = urlparse(self.path).path
        payload = self._read_json()
        profile = database.fetch_user_profile()

        if path == "/api/face/analyze":
            analysis = face_module.analyze({**profile, **payload}).to_dict()
            plan = makeup_engine.build_plan(analysis)
            self._send_json({"analysis": analysis, "makeup_plan": plan})
            return

        if path == "/api/makeup/plan":
            analysis = payload.get("analysis") or face_module.analyze(profile).to_dict()
            self._send_json(makeup_engine.build_plan(analysis))
            return

        if path == "/api/product/scan":
            self._send_json(product_scanner.scan(payload, profile))
            return

        if path == "/api/try-on/match":
            self._send_json(try_on_module.match(payload, profile))
            return

        self._send_json({"error": "Not found"}, status=404)

    def _read_json(self) -> dict[str, Any]:
        length = int(self.headers.get("Content-Length", 0))
        if length == 0:
            return {}
        raw = self.rfile.read(length).decode("utf-8")
        try:
            value = json.loads(raw)
        except json.JSONDecodeError:
            return {}
        return value if isinstance(value, dict) else {}

    def _send_json(self, data: dict[str, Any], status: int = 200) -> None:
        body = json.dumps(data, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_static(self, path: str) -> None:
        relative = path.removeprefix("/static/")
        target = (STATIC_DIR / relative).resolve()
        if STATIC_DIR.resolve() not in target.parents and target != STATIC_DIR.resolve():
            self._send_json({"error": "Invalid static path"}, status=400)
            return
        if not target.exists() or not target.is_file():
            self._send_json({"error": "Static file not found"}, status=404)
            return

        content_type = {
            ".css": "text/css; charset=utf-8",
            ".js": "application/javascript; charset=utf-8",
            ".html": "text/html; charset=utf-8",
            ".svg": "image/svg+xml",
        }.get(target.suffix, "application/octet-stream")
        self._send_file(target, content_type)

    def _send_file(self, file_path: Path, content_type: str) -> None:
        body = file_path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args: Any) -> None:
        return


def run_server(host: str = "127.0.0.1", port: int = 5000) -> None:
    database.initialize_database()
    server = ThreadingHTTPServer((host, port), SmartMirrorRequestHandler)
    print(f"Smart Mirror running at http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping Smart Mirror server.")
    finally:
        server.server_close()
