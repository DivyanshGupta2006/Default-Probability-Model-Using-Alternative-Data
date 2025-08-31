from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Dict, Any

from src.interface.services import credit_service

router = APIRouter(prefix="/track", tags=["Tracking"])
templates = Jinja2Templates(directory="src/interface/templates")

class UserUpdate(BaseModel):
    features: Dict[str, Any]

@router.get("/", response_class=HTMLResponse)
def show_tracking_page(request: Request):
    """Serves the main User Tracking & Management HTML page."""
    return templates.TemplateResponse("tracking.html", {"request": request})

@router.get("/portfolio")
def get_full_portfolio():
    """Returns data for all users in the portfolio to populate the table."""
    try:
        portfolio_data = credit_service.get_full_portfolio_data()
        return {"portfolio": portfolio_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/users/{user_id}")
def update_user_data(user_id: str, update_data: UserUpdate):
    """Updates a user's data and returns their new risk score."""
    try:
        new_probability = credit_service.update_and_reevaluate(user_id, update_data.features)
        return {"user_id": user_id, "new_probability_of_default": new_probability}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))