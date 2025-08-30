# In: src/interface/routers/home_router.py

from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

# Create a new router
router = APIRouter(
    tags=["Home"]
)

# Configure templates
templates = Jinja2Templates(directory="src/interface/templates")

@router.get("/", response_class=HTMLResponse)
def show_home_page(request: Request):
    """
    Serves the home page of the Finshield application.
    """
    return templates.TemplateResponse("index.html", {"request": request})

@router.get("/dashboard", response_class=HTMLResponse)
def show_dashboard(request: Request):
    """
    Optional dashboard endpoint for future use.
    """
    # For now, redirect to home or show a simple dashboard
    return templates.TemplateResponse("index.html", {
        "request": request,
        "dashboard_mode": True
    })