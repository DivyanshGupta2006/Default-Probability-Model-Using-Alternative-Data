from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

# Import the Pydantic schemas you created
from src.interface.schemas.credit_application import CreditApplication
from src.interface.schemas.prediction_result import PredictionResult

# Import your service module that contains the ML logic
from src.interface.services import credit_service

# Create a new router instance
# All endpoints defined here will have a URL starting with /predict
router = APIRouter(
    prefix="/predict",
    tags=["Predictions"]  # This tag groups the endpoints in the /docs UI
)

# Initialize the Jinja2 templates to find your HTML files
templates = Jinja2Templates(directory="src/interface/templates")


@router.get("/add_new_user_form", response_class=HTMLResponse)
def show_add_user_form(request: Request):
    """
    Serves the HTML form for submitting a new credit application.
    Navigate to http://127.0.0.1:8000/predict/add_new_user_form to see it.
    """
    return templates.TemplateResponse("add_user.html", {"request": request})


@router.post("/new_applicant", response_model=PredictionResult)
def predict_new_applicant(application: CreditApplication):
    """
    Accepts new applicant data in JSON format, runs the prediction,
    and returns the probability of default along with a SHAP explanation.
    """
    try:
        # Convert the Pydantic model to a dictionary
        application_dict = application.model_dump()

        # Call the correct function from your service layer
        result = credit_service.predict_and_explain(application_dict)

        return result

    except Exception as e:
        # If anything goes wrong in the service, return an error
        raise HTTPException(status_code=500, detail=str(e))