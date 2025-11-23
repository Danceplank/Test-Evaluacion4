from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from pathlib import Path

router = APIRouter()
TEMPLATES_DIR = Path(__file__).resolve().parents[1] / "templates"  # proyecto/templates
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


@router.get("/admin", include_in_schema=False)
def admin_index(request: Request):
    return templates.TemplateResponse("admin.html", {"request": request})