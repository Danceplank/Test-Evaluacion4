from pathlib import Path
import sys

# Ensure workspace root is importable when running via python -m proyecto.app.main
REPO_ROOT = Path(__file__).resolve().parents[2]  # workspace root (ciberseguridad/)
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# Base project dir (proyecto/)
BASE_DIR = Path(__file__).resolve().parents[1]

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# Import app modules (use proyecto.* namespace)
try:
    from proyecto.api.endpoints import router as api_router
except Exception:
    # explicit error to make failures clearer
    raise ImportError("Cannot import proyecto.api.endpoints. Ensure you're running from workspace root.")

try:
    from proyecto.api.admin import router as admin_router
except Exception:
    admin_router = None

try:
    from proyecto.app.database.database import init_db
except Exception:
    raise ImportError("Cannot import proyecto.app.database.database.init_db")

# Ensure device model is loaded so its table is created before init_db()
try:
    import proyecto.modelo.device  # noqa: F401
except Exception:
    # ignore if missing; init_db will still create existing tables
    pass

# Initialize DB (creates tables if needed)
init_db()

# Create app
app = FastAPI(
    title="Iquique Ciberseguridad",
    version="1.0.0",
    description="Plataforma de seguridad digital para PYMEs de Iquique",
    debug=False,
)

# CORS (básico, ajustar en producción)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files and templates (relative to proyecto/)
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

# Include routers
app.include_router(api_router, prefix="/api/v1")
if admin_router is not None:
    app.include_router(admin_router)  # serves /admin

@app.get("/", include_in_schema=False)
async def root():
    return {
        "message": "Bienvenido a Iquique Ciberseguridad",
        "version": app.version,
    }