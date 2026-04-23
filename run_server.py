"""
Convenience script to start the FastAPI server.

Usage:
    python run_server.py
    python run_server.py --port 8080
"""

import argparse
import uvicorn


def main():
    parser = argparse.ArgumentParser(description="Start the Review Intelligence API")
    parser.add_argument("--host", default="0.0.0.0", help="Bind host")
    parser.add_argument("--port", type=int, default=8000, help="Bind port")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    args = parser.parse_args()

    uvicorn.run(
        "app.main:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
    )


if __name__ == "__main__":
    main()
