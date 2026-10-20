import os
import socket
import argparse
import uvicorn
from backend.app.core.config import settings
from backend.app.db.session import init_db

def find_available_port(preferred_port: int) -> int:
    port = preferred_port
    while True:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(('127.0.0.1', port)) != 0:
                return port
            port += 1

def main():
    parser = argparse.ArgumentParser(description="Run Project 51 Platform")
    parser.add_argument("--port", type=int, default=5051)
    parser.add_argument("--host", type=str, default="0.0.0.0")
    args = parser.parse_args()

    port = find_available_port(args.port)
    settings.PORT = port
    print("=" * 70)
    print("   PROJECT 51 — SMART ENERGY FORECASTING & DYNAMIC PEAK SHAVING")
    print(f"   Assigned Port: {port} | Mode: Production SOTA Microservice")
    print("=" * 70)
    init_db()
    print(f"Server starting on http://localhost:{port}")
    uvicorn.run("backend.app.main:app", host=args.host, port=port, reload=False)

if __name__ == "__main__":
    main()
