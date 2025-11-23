from pathlib import Path
import sys
import argparse
from importlib import import_module
import uvicorn

# Ensure workspace root and the 'proyecto' package directory are on sys.path.
# This allows imports like "proyecto.*" and top-level "app.*" (which lives under proyecto/app).
REPO_ROOT = Path(__file__).resolve().parents[1]  # ciberseguridad/
PROYECTO_DIR = REPO_ROOT / "proyecto"
sys.path.insert(0, str(PROYECTO_DIR))
sys.path.insert(0, str(REPO_ROOT))

def main():
    parser = argparse.ArgumentParser(description="Run the GravityZone FastAPI app")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to listen on")
    parser.add_argument("--reload", action="store_true", help="Enable uvicorn reload")
    args = parser.parse_args()

    # Import the app object from proyecto.app.main
    try:
        mod = import_module("proyecto.app.main")
        app = getattr(mod, "app")
    except Exception:
        # Fallback: import as plain app package (if running differently)
        mod = import_module("app.main")
        app = getattr(mod, "app")

    uvicorn.run(app, host=args.host, port=args.port, reload=args.reload)

if __name__ == "__main__":
    main()