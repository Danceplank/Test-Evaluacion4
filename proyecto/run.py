from pathlib import Path
import sys
import argparse
from importlib import import_module
import uvicorn

REPO_ROOT = Path(__file__).resolve().parents[1]  # workspace root (ciberseguridad/)
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

def main():
    parser = argparse.ArgumentParser(description="Run Iquique Ciberseguridad app")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--reload", action="store_true")
    args = parser.parse_args()

    mod = import_module("proyecto.app.main")
    app = getattr(mod, "app")
    uvicorn.run(app, host=args.host, port=args.port, reload=args.reload)

if __name__ == "__main__":
    main()