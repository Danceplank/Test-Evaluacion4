from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from pathlib import Path

router = APIRouter()
# templates dir: proyecto/templates (one level up from proyecto/api)
TEMPLATES_DIR = Path(__file__).resolve().parents[1] / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


@router.get("/admin", include_in_schema=False)
def admin_index(request: Request):
    """
    Página de administración centralizada.
    """
    return templates.TemplateResponse("admin.html", {"request": request})