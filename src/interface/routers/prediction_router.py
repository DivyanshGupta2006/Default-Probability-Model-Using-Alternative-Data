from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

# Import the Pydantic schemas you created
from src.interface.schemas.credit_application import CreditApplication
from src.interface.schemas.prediction_result import PredictionResult
from src.interface.database.connection import get_database

# Import your service module that contains the ML logic
from src.interface.services import credit_service

# Create a new router instance
router = APIRouter(
    prefix="/predict",
    tags=["Predictions"]
)

# Initialize Jinja2 templates
templates = Jinja2Templates(directory="src/interface/templates")


@router.get("/add_new_user_form", response_class=HTMLResponse)
def show_add_user_form(request: Request):
    """
    Serves the HTML form for submitting a new credit application.
    """
    return templates.TemplateResponse("add_user.html", {"request": request})


@router.post("/new_applicant", response_model=PredictionResult)
def predict_and_store_new_applicant(application: CreditApplication, db: Session = Depends(get_database)):
    """
    Accepts new applicant data, creates a user record in the database,
    runs the initial prediction, stores the assessment, and returns the results.
    """
    try:
        # The Pydantic model now contains both user data and feature data.
        # We need to separate them for the service function.
        application_dict = application.model_dump()

        # 1. Prepare data for creating a new user record.
        user_data = {
            "user_id": application_dict.pop("user_id"),
            "full_name": application_dict.pop("full_name"),
            "email": application_dict.pop("email"),
            "phone": application_dict.pop("phone")
        }

        # The rest of the dictionary now only contains feature data.
        features_data = application_dict

        # 2. Call the service function to create the user and get the initial prediction.
        # This function will handle all the database operations and the prediction itself.
        credit_service.create_new_user(user_data, features_data)

        # 3. After creating, get the latest assessment to return the explanation.
        # This ensures the data is consistent with what's in the DB.
        prediction_result = credit_service.predict_and_explain(features_data)

        return prediction_result

    except ValueError as ve:
        # Handle cases where the user might already exist or data is invalid.
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        # Catch-all for other server errors.
        raise HTTPException(status_code=500, detail=f"An internal error occurred: {str(e)}")
