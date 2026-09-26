"""
FIREGUARD AI - Single-Command FastAPI Application Launcher
SIH Problem Statement SIH26162
Launches the FastAPI end-to-end command server with Uvicorn and opens the browser.
"""
import os
import sys
import webbrowser
import threading
import time
from pathlib import Path
import uvicorn

PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

def open_browser(port: int):
    time.sleep(1.5)
    url = f"http://127.0.0.1:{port}/"
    print(f"\n[FIREGUARD AI] Opening browser at {url} ...\n")
    try:
        webbrowser.open(url)
    except Exception:
        pass

if __name__ == "__main__":
    from backend.config.settings import settings
    port = settings.PORT

    print("=" * 70)
    print("  FIREGUARD AI: Industrial Fire & Thermal Source Command Center")
    print("  SIH Problem Statement SIH26162 | End-to-End FastAPI Platform")
    print("=" * 70)
    print(f"  Landing Portal:       http://127.0.0.1:{port}/")
    print(f"  Command Operations:   http://127.0.0.1:{port}/app")
    print(f"  Interactive OpenAPI:  http://127.0.0.1:{port}/docs")
    print(f"  ReDoc Documentation:  http://127.0.0.1:{port}/redoc")
    print(f"  Health Monitor API:   http://127.0.0.1:{port}/api/v1/health")
    print(f"  SIH Demo Pipeline:    POST http://127.0.0.1:{port}/api/v1/demo/run")
    print("=" * 70)

    # Launch browser in separate thread
    threading.Thread(target=open_browser, args=(port,), daemon=True).start()

    # Run FastAPI via Uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=port, log_level="info", access_log=True)
