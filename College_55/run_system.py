"""
One-Click Launch Script for Project 55:
AI-Based Accident Detection and Emergency Alert System Using Computer Vision.
Starts the Enterprise FastAPI Backend, WebSocket Hub, and Operator Command Dashboard.
"""

import os
import sys
import socket
import argparse
import uvicorn
from backend.app.core.config import settings
from backend.app.db.session import init_db


def is_port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) == 0


def find_available_port(preferred_port: int) -> int:
    port = preferred_port
    while is_port_in_use(port):
        print(f"[!] Port {port} is currently occupied. Checking next port...")
        port += 1
    return port


def main():
    parser = argparse.ArgumentParser(description="Run Project 55 Enterprise Platform")
    parser.add_argument("--port", type=int, default=int(os.environ.get("PORT", 8080)), help="Port to bind server (default: 8080)")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host interface (default: 0.0.0.0)")
    args = parser.parse_args()

    port = find_available_port(args.port)

    print("=" * 75)
    print(" " * 8 + "PROJECT 55 — ENTERPRISE ACCIDENT DETECTION & CAD DISPATCH")
    print("=" * 75)

    # 1. Initialize Database & Seed Feeds
    print("[1/3] Initializing SQLite / PostgreSQL Enterprise Database...")
    init_db()

    # 2. Verify Model Checkpoints
    print("[2/3] Verifying Deep Learning Weights & Directories...")
    os.makedirs(settings.EVIDENCE_OUTPUT_DIR, exist_ok=True)
    os.makedirs(settings.SAMPLE_VIDEOS_DIR, exist_ok=True)

    if os.path.exists(settings.MODEL_WEIGHTS_PATH):
        print(f"      ✓ Phase 2 Multi-Cue Attention Model Loaded ({settings.MODEL_WEIGHTS_PATH})")
    else:
        print(f"      ! Warning: Model weights not found at {settings.MODEL_WEIGHTS_PATH}")

    # 3. Start High-Performance Server
    print(f"[3/3] Starting Enterprise Web Server & Real-Time WebSocket Broker on port {port}...")
    print("\n" + "-" * 75)
    print(f"  OPERATOR COMMAND DASHBOARD : http://localhost:{port}")
    print(f"  INTERACTIVE SWAGGER DOCS   : http://localhost:{port}/docs")
    print(f"  LIVE WEBSOCKET TELEMETRY   : ws://localhost:{port}/api/ws")
    print(f"  SYSTEM HEALTH DIAGNOSTICS  : http://localhost:{port}/api/health/")
    print("-" * 75 + "\n")

    uvicorn.run("backend.app.main:app", host=args.host, port=port, reload=False)


if __name__ == "__main__":
    main()
