# In: src/interface/services/credit_service.py

import joblib
import pandas as pd
from pathlib import Path

# --- 1. SETUP & CONFIGURATION ---

# Define paths to your saved model and preprocessor
# This assumes your script is run from the root of the project
MODEL_DIR = Path("models/")
MODEL_PATH = MODEL_DIR / "lightgbm_model.joblib"
PREPROCESSOR_PATH = MODEL_DIR / "preprocessor.joblib"

# --- 2. LOAD ARTIFACTS ---

# Load the artifacts at startup to ensure they are ready for predictions
try:
    model = joblib.load(MODEL_PATH)
    preprocessor = joblib.load(PREPROCESSOR_PATH)
    print("✅ Model and preprocessor loaded successfully!")
except FileNotFoundError as e:
    print(f"❌ Error loading artifacts: {e}. Make sure the model and preprocessor files are in the 'models/' directory.")
    model = None
    preprocessor = None


# --- 3. CORE SERVICE FUNCTION ---

def predict_new_applicant(application_data: dict):
    """
    Preprocesses input data and returns a default probability.
    """
    if not model or not preprocessor:
        raise RuntimeError("Model or preprocessor not loaded. Cannot make predictions.")

    # Convert the input dictionary to a pandas DataFrame
    input_df = pd.DataFrame([application_data])

    # Apply the saved preprocessing pipeline
    # The apply_pipeline function is defined in your src/data_processing/preprocess.py
    # We will need to adapt it slightly for inference if it's not already.
    # For now, let's assume a simplified application of the preprocessor:

    # Separate columns
    numerical_cols = preprocessor['numerical_cols']
    categorical_cols = preprocessor['categorical_cols']

    # Create a full DataFrame with all expected columns
    all_cols = numerical_cols + preprocessor['encoder'].get_feature_names_out(categorical_cols).tolist()

    # Preprocess categorical features
    encoded_features = preprocessor['encoder'].transform(input_df[categorical_cols])
    encoded_df = pd.DataFrame(encoded_features, columns=preprocessor['encoder'].get_feature_names_out(categorical_cols))

    # Preprocess numerical features
    scaled_features = preprocessor['scaler'].transform(input_df[numerical_cols])
    scaled_df = pd.DataFrame(scaled_features, columns=numerical_cols)

    # Combine into a single DataFrame in the correct order
    processed_df = pd.concat([scaled_df, encoded_df], axis=1)

    # Make prediction
    probability = model.predict_proba(processed_df)[:, 1]

    return float(probability[0])