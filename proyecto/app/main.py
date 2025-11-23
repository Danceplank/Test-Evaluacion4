from pathlib import Path
import sys

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# Ensure workspace root is importable when running via python -m proyecto.app.main
REPO_ROOT = Path(__file__).resolve().parents[2]  # workspace root (ciberseguridad/)
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# Base project dir (proyecto/)
BASE_DIR = Path(__file__).resolve().parents[1]

# Import app modules (expect proyecto.* namespace)
from proyecto.api.endpoints import router as api_router
from proyecto.api.admin import router as admin_router
from proyecto.app.database.database import init_db

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
app.include_router(admin_router)  # serves /admin

@app.get("/", include_in_schema=False)
async def root():
    return {
        "message": "Bienvenido a Iquique Ciberseguridad",
        "version": app.version,
    }