#!/usr/bin/env python3
"""
Race Day Cheat Card — Live Web Server

Serves the cheat card as a dynamic web page that auto-updates.
Reads from /tmp/race_day_data.json (same file generate_pdf.py uses).

Usage:
    python3 server.py [--port 7700] [--data /tmp/race_day_data.json]
"""

import json
import os
import argparse
from pathlib import Path
from datetime import datetime

from fastapi import FastAPI, Response
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

app = FastAPI(title="Race Day Cheat Card")

DATA_PATH = os.environ.get("CHEATCARD_DATA", "/tmp/race_day_data.json")
WEB_DIR = Path(__file__).parent


@app.get("/", response_class=HTMLResponse)
async def index():
    html_path = WEB_DIR / "index.html"
    return HTMLResponse(content=html_path.read_text(), status_code=200)


@app.get("/api/data")
async def get_data():
    try:
        with open(DATA_PATH, "r") as f:
            data = json.load(f)
        # Add server timestamp
        data["_server_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S CT")
        return JSONResponse(content=data)
    except FileNotFoundError:
        return JSONResponse(
            content={"error": f"No data file found at {DATA_PATH}"},
            status_code=404,
        )
    except json.JSONDecodeError as e:
        return JSONResponse(
            content={"error": f"Invalid JSON: {str(e)}"},
            status_code=500,
        )


@app.get("/api/health")
async def health():
    exists = os.path.exists(DATA_PATH)
    mtime = None
    if exists:
        mtime = datetime.fromtimestamp(os.path.getmtime(DATA_PATH)).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    return {
        "status": "ok",
        "data_file": DATA_PATH,
        "data_exists": exists,
        "last_modified": mtime,
    }


def main():
    global DATA_PATH

    parser = argparse.ArgumentParser(description="Race Day Cheat Card Web Server")
    parser.add_argument("--port", type=int, default=7700, help="Port (default: 7700)")
    parser.add_argument("--data", type=str, default=DATA_PATH, help="JSON data path")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host")
    args = parser.parse_args()

    DATA_PATH = args.data

    print(f"Race Day Cheat Card — http://{args.host}:{args.port}")
    print(f"Data file: {DATA_PATH}")
    uvicorn.run(app, host=args.host, port=args.port, log_level="info")


if __name__ == "__main__":
    main()
