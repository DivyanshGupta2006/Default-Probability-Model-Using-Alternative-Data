import joblib
import pandas as pd
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import shap
import numpy as np

# Import your project's functions
from src.data_processing.preprocess import apply_pipeline
from src.utils import get_config

# --- App Initialization ---
app = FastAPI()
config = get_config.read_yaml_from_package()

# --- Load Pre-trained Objects ---
# Load the preprocessing pipeline
preprocessor_path = config['paths']['model_data_directory'] + "preprocessor.joblib"
fitted_objects = joblib.load(preprocessor_path)

# Load the trained model (let's assume you're using the ensemble)
model_path = config['paths']['model_data_directory'] + "ensemble_model.joblib"
model = joblib.load(model_path)

# Load SHAP explainer (for individual predictions)
# Note: You might need to adjust this depending on the model type
actual_model = model.meta_learner # Assuming meta-learner is what you want to explain
explainer = shap.KernelExplainer(actual_model.predict_proba, np.zeros((1, len(model.base_models))))


# --- Template and Static File Configuration ---
app.mount("/static", StaticFiles(directory="src/interface/static"), name="static")
templates = Jinja2Templates(directory="src/interface/templates")