from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import List, Optional

from src.interface.database import crud
from src.interface.database.connection import get_database
from src.interface.services import credit_service

router = APIRouter(prefix="/track", tags=["Tracking"])
templates = Jinja2Templates(directory="src/interface/templates")


@router.get("/portfolio_page", response_class=HTMLResponse)
def show_tracking_page(request: Request):
    """Serves the main user tracking page."""
    return templates.TemplateResponse("track_user.html", {"request": request})


@router.get("/portfolio")
def get_full_portfolio(
        db: Session = Depends(get_database),
        search: Optional[str] = Query(None, description="Search by user ID, name, or email"),
        risk_level: Optional[str] = Query(None, description="Filter by risk category (low, medium, high)"),
        status: Optional[str] = Query(None, description="Filter by user status (active, inactive)")
):
    """Returns data for all users in the portfolio from the database, with optional filtering."""
    try:
        filters = {
            "search": search,
            "risk_level": risk_level,
            "status": status
        }
        active_filters = {k: v for k, v in filters.items() if v}
        portfolio_data = crud.PortfolioCRUD.get_portfolio_data(db, filters=active_filters)
        return {"portfolio": portfolio_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Could not fetch portfolio data.")


@router.get("/users/{user_id}")
def get_user_details(user_id: str, db: Session = Depends(get_database)):
    """
    Retrieves detailed information for a single user, including their
    current features, latest assessment, and risk history.
    """
    try:
        user = crud.UserCRUD.get_user(db, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        features = crud.FeatureCRUD.get_current_features(db, user_id)
        latest_assessment = crud.AssessmentCRUD.get_latest_assessment(db, user_id)
        history = crud.AssessmentCRUD.get_user_assessment_history(db, user_id, limit=20)

        feature_dict = {c.name: getattr(features, c.name) for c in features.__table__.columns if
                        c.name not in ['feature_id', 'user_id']} if features else {}

        # Sort feature impacts for the latest assessment
        feature_impacts = {}
        if latest_assessment and latest_assessment.feature_impacts:
            # Sort by absolute value, descending
            sorted_impacts = sorted(
                latest_assessment.feature_impacts.items(),
                key=lambda item: abs(item[1]),
                reverse=True
            )
            feature_impacts = dict(sorted_impacts)

        return {
            "user_info": {
                "id": user.user_id,
                "full_name": user.full_name,
                "email": user.email,
                "status": user.status.value,
                "created_at": user.created_at.strftime('%Y-%m-%d %H:%M:%S')
            },
            "current_features": feature_dict,
            "latest_assessment": {
                "prediction_probability": latest_assessment.prediction_probability,
                "risk_category": latest_assessment.risk_category.value,
                "assessed_at": latest_assessment.assessed_at.strftime('%Y-%m-%d %H:%M:%S'),
                "base_value": latest_assessment.base_value,
                "feature_impacts": feature_impacts
            } if latest_assessment else {},
            "assessment_history": [
                {
                    "assessed_at": h.assessed_at.strftime('%Y-%m-%d'),
                    "prediction_probability": h.prediction_probability
                } for h in reversed(history)  # Reverse to show oldest first for charting
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


@router.put("/users/{user_id}")
def update_user_data(user_id: str, updated_data: dict, db: Session = Depends(get_database)):
    """Updates a user's data, re-runs prediction, and stores the new assessment."""
    try:
        new_probability = credit_service.update_and_reevaluate(
            user_id=user_id,
            updated_features=updated_data,
            changed_by="admin_interface"
        )
        return {"user_id": user_id, "new_probability_of_default": new_probability}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="An error occurred during user update.")
