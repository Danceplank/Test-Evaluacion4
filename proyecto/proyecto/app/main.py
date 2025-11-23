from fastapi import FastAPI, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from pathlib import Path
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys

# Ensure the workspace root is on sys.path so "proyecto" can be imported when running this file directly.
# __file__ -> ...\proyecto\app\main.py
# parents[1] -> proyecto/, parents[2] -> ciberseguridad/ (workspace root)
REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

# Try to import models/router using project package names, fallback to plain package names
try:
    from proyecto.modelo.seguridad import Base
except Exception as e1:
    try:
        from modelo.seguridad import Base
    except Exception as e2:
        raise ImportError(
            "Could not import 'proyecto.modelo.seguridad' or 'modelo.seguridad'. "
            "Make sure you're running from the workspace root or adjust PYTHONPATH."
        ) from e2

try:
    from proyecto.api.endpoints import router as api_router
except Exception:
    try:
        from api.endpoints import router as api_router
    except Exception as e:
        raise ImportError(
            "Could not import 'proyecto.api.endpoints' or 'api.endpoints'. "
            "Make sure you're running from the workspace root or adjust PYTHONPATH."
        ) from e

# Create a simple local SQLite engine + session dependency if no separate database module exists
BASE_DIR = Path(__file__).resolve().parents[1]  # proyecto/
DATABASE_URL = f"sqlite:///{BASE_DIR / 'data.db'}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Crear tablas
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="GravityZone Business Security",
    version="1.0.0",
    description="Solución de seguridad multicapa de última generación para empresas"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Montar archivos estáticos y templates (rutas relativas al directorio proyecto/)
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

# Incluir rutas
app.include_router(api_router, prefix="/api/v1")

# NEW: include admin UI router if available
try:
    from proyecto.api.admin import router as admin_router
except Exception:
    try:
        from api.admin import router as admin_router
    except Exception:
        admin_router = None

if admin_router:
    app.include_router(admin_router)

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})


@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": str(datetime.utcnow())}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)