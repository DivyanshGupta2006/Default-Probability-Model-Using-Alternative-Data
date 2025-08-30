# In: src/interface/routers/about_router.py

from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

# Create a new router
router = APIRouter(
    tags=["About"]
)

# Configure templates
templates = Jinja2Templates(directory="src/interface/templates")

@router.get("/about")
def show_about_page(request: Request):
    """
    Serves the 'About' page which explains the model.
    """
    # The context dictionary can pass data to your template if needed later
    return templates.TemplateResponse("about.html", {"request": request})