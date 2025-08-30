# In: src/interface/routers/prediction_router.py

from fastapi import APIRouter, HTTPException, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse  # <-- ADD THIS IMPORT LINE

from src.interface.schemas.credit_application import CreditApplication
from src.interface.services import credit_service

# Create a new router
router = APIRouter(
    prefix="/predict",
    tags=["Predictions"]
)

# Configure templates
templates = Jinja2Templates(directory="src/interface/templates")

@router.get("/add_new_user_form", response_class=HTMLResponse)
def show_add_user_form(request: Request):
    """Serves the HTML form for adding a new user."""
    return templates.TemplateResponse("add_user.html", {"request": request})


@router.post("/new_applicant")
def predict_new_applicant(application: CreditApplication):
    """
    Accepts new applicant data and returns a default risk probability.
    """
    try:
        application_dict = application.model_dump()
        probability = credit_service.predict_new_applicant(application_dict)
        return {"probability_of_default": probability}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))