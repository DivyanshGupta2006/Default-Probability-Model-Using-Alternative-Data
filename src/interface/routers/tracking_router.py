from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from src.interface.database import crud, models
from src.interface.database.connection import get_database
from src.interface.services import credit_service

router = APIRouter(prefix="/track", tags=["Tracking"])


@router.get("/portfolio")
def get_full_portfolio(
        db: Session = Depends(get_database),
        # --- FIX START: Add optional query parameters for filtering ---
        search: Optional[str] = Query(None, description="Search by user ID, name, or email"),
        risk_level: Optional[str] = Query(None, description="Filter by risk category (low, medium, high)"),
        status: Optional[str] = Query(None, description="Filter by user status (active, inactive)")
        # --- FIX END ---
):
    """
    Returns data for all users in the portfolio from the database, with optional filtering.
    """
    try:
        # --- FIX START: Pass filters to the CRUD function ---
        filters = {
            "search": search,
            "risk_level": risk_level,
            "status": status
        }
        # Remove None values so we don't pass empty filters
        active_filters = {k: v for k, v in filters.items() if v}

        portfolio_data = crud.PortfolioCRUD.get_portfolio_data(db, filters=active_filters)
        # --- FIX END ---
        return {"portfolio": portfolio_data}
    except Exception as e:
        print(f"Error fetching portfolio: {e}")
        raise HTTPException(status_code=500, detail="Could not fetch portfolio data.")


# ... The rest of your tracking_router.py file remains the same ...
@router.put("/users/{user_id}")
def update_user_data(user_id: str, updated_data: dict, db: Session = Depends(get_database)):
    """
    Updates a user's data and returns their new risk score.
    """
    try:
        # 1. Update features in the database
        crud.FeatureCRUD.update_user_features(db, user_id, updated_data, changed_by="admin_interface")

        # 2. Get the newly updated, complete feature set
        current_features_obj = crud.FeatureCRUD.get_current_features(db, user_id)
        if not current_features_obj:
            raise HTTPException(status_code=404, detail="User features not found after update.")

        # Convert SQLAlchemy object to dictionary for the prediction service
        features_dict = {c.name: getattr(current_features_obj, c.name) for c in current_features_obj.__table__.columns}

        # 3. Get a new prediction
        new_assessment = credit_service.predict_and_explain(features_dict)

        # 4. Save the new assessment to the database
        crud.AssessmentCRUD.create_assessment(
            db=db,
            user_id=user_id,
            feature_id=current_features_obj.feature_id,
            assessment_data=new_assessment,
            assessment_type="update"
        )

        return {"user_id": user_id, "new_probability_of_default": new_assessment['prediction_probability']}

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        print(f"Error updating user: {e}")
        raise HTTPException(status_code=500, detail="An error occurred during user update.")