# In: src/interface/services/credit_service.py

import joblib
import pandas as pd
import shap
from pathlib import Path

# --- 1. SETUP & CONFIGURATION ---
try:
    ROOT_DIR = Path(__file__).parent.parent.parent.parent
except NameError:
    ROOT_DIR = Path(".").absolute()

MODEL_DIR = ROOT_DIR / "models"
MODEL_PATH = MODEL_DIR / "lightgbm_model.joblib"
PREPROCESSOR_PATH = MODEL_DIR / "preprocessor.joblib"
TRAIN_DATA_PATH = ROOT_DIR / "data" / "processed_data" / "clean_train_data.csv"

# --- 2. LOAD ARTIFACTS AT STARTUP ---
model = None
preprocessor = None
explainer = None

try:
    model = joblib.load(MODEL_PATH)
    preprocessor = joblib.load(PREPROCESSOR_PATH)

    # Use a small background dataset for the SHAP explainer
    train_df_sample = pd.read_csv(TRAIN_DATA_PATH).sample(100, random_state=42)
    id_col = 'SK_ID_CURR'
    target_col = 'TARGET'
    background_data = train_df_sample.drop(columns=[id_col, target_col])

    explainer = shap.TreeExplainer(model.model)
    print("✅ Model, preprocessor, and SHAP explainer loaded successfully!")

except Exception as e:
    print(f"❌ Error loading artifacts: {e}. Ensure all necessary files exist.")

# --- 3. MOCK DATABASE for TRACKING FEATURE ---

MOCK_DB = {
    "USR001_John_Doe": {
        "NAME_EDUCATION_TYPE": "Higher education", "NAME_SELLER_INDUSTRY": "Consumer electronics", "TRUECALR_FLAG": "Blue",
        "REGION_RATING_CLIENT": 2, "REG_REGION_NOT_LIVE_REGION": 0, "REG_REGION_NOT_WORK_REGION": 0,
        "LIVE_REGION_NOT_WORK_REGION": 0, "AMT_DRAWINGS_ATM_CURRENT": 5000.0, "AMT_DRAWINGS_CURRENT": 7500.0,
        "AMT_DRAWINGS_OTHER_CURRENT": 0.0, "AMT_DRAWINGS_POS_CURRENT": 2500.0, "CNT_DRAWINGS_ATM_CURRENT": 2.0,
        "CNT_DRAWINGS_CURRENT": 10.0, "CNT_DRAWINGS_OTHER_CURRENT": 0.0, "CNT_DRAWINGS_POS_CURRENT": 8.0,
        "SELLERPLACE_AREA": 500, "RCHRG_FRQ": 2.0, "TRD_ACC": 1.0, "OFC_DOC_EXP": 5, "GST_FIL_DEF": 0,
        "SIM_CARD_FAIL": 0, "ECOM_SHOP_RETURN": 1, "UTILITY_BIL": 9500.0, "REG_VEH_CHALLAN": 0,
        "LINKEDIN_DATA": 1, "REV_FRM_UBER_RAPIDO": 0.0, "NO_OF_SMRT_CARD": 2, "NO_TYPE_OF_ACC": 3
    },
    "USR002_Jane_Smith": {
        "NAME_EDUCATION_TYPE": "Secondary / secondary special", "NAME_SELLER_INDUSTRY": "Clothing", "TRUECALR_FLAG": "Red",
        "REGION_RATING_CLIENT": 3, "REG_REGION_NOT_LIVE_REGION": 1, "REG_REGION_NOT_WORK_REGION": 1,
        "LIVE_REGION_NOT_WORK_REGION": 0, "AMT_DRAWINGS_ATM_CURRENT": 15000.0, "AMT_DRAWINGS_CURRENT": 20000.0,
        "AMT_DRAWINGS_OTHER_CURRENT": 100.0, "AMT_DRAWINGS_POS_CURRENT": 4900.0, "CNT_DRAWINGS_ATM_CURRENT": 5.0,
        "CNT_DRAWINGS_CURRENT": 25.0, "CNT_DRAWINGS_OTHER_CURRENT": 1.0, "CNT_DRAWINGS_POS_CURRENT": 20.0,
        "SELLERPLACE_AREA": 100, "RCHRG_FRQ": 5.0, "TRD_ACC": 4.0, "OFC_DOC_EXP": 1, "GST_FIL_DEF": 2,
        "SIM_CARD_FAIL": 3, "ECOM_SHOP_RETURN": 4, "UTILITY_BIL": 15000.0, "REG_VEH_CHALLAN": 2,
        "LINKEDIN_DATA": 0, "REV_FRM_UBER_RAPIDO": 8000.0, "NO_OF_SMRT_CARD": 4, "NO_TYPE_OF_ACC": 5
    }
}
# --- 3. HELPER FUNCTION for PREPROCESSING (FINAL, ROBUST VERSION) ---

# In: src/interface/services/credit_service.py

def _apply_inference_pipeline(data: pd.DataFrame) -> pd.DataFrame:
    """Applies the saved preprocessing pipeline to new data."""
    if not preprocessor:
        raise RuntimeError("Preprocessor is not loaded.")

    numerical_cols = preprocessor['numerical_cols']
    categorical_cols = preprocessor['categorical_cols']
    encoder = preprocessor['encoder']
    scaler = preprocessor['scaler']

    input_df = data.copy()

    # Create a new DataFrame with all the raw columns the preprocessor expects
    all_raw_cols = numerical_cols + categorical_cols
    full_raw_df = pd.DataFrame(columns=all_raw_cols)

    # Populate the full DataFrame with the data we received from the user
    for col in input_df.columns:
        if col in full_raw_df.columns:
            full_raw_df[col] = input_df[col]

    # --- THIS IS THE FIX ---
    # Fill missing numerical and categorical columns separately
    num_df = full_raw_df[numerical_cols].fillna(0)
    cat_df = full_raw_df[categorical_cols].fillna("Missing")
    # -----------------------

    # Apply transformations
    encoded_features = encoder.transform(cat_df)
    encoded_df = pd.DataFrame(encoded_features, columns=encoder.get_feature_names_out(categorical_cols))

    scaled_features = scaler.transform(num_df)
    scaled_df = pd.DataFrame(scaled_features, columns=numerical_cols)

    # Combine and ensure the column order is exactly what the model was trained on
    processed_input_df = pd.concat([scaled_df, encoded_df], axis=1)

    expected_model_columns = model.model.feature_name_
    final_df = pd.DataFrame(columns=expected_model_columns)
    final_df = pd.concat([final_df, processed_input_df], ignore_index=True).fillna(0)
    final_df = final_df[expected_model_columns]

    return final_df


# --- 4. CORE SERVICE FUNCTION ---
# In: src/interface/services/credit_service.py

def predict_and_explain(application_data: dict):
    """
    This is a DEBUGGING version. It will print its progress to the terminal.
    """
    try:
        print("\n--- [DEBUG] Inside predict_and_explain ---")
        if not all([model, preprocessor, explainer]):
            raise RuntimeError("ML artifacts are not loaded.")

        print("[DEBUG] Step 1: Creating input DataFrame.")
        input_df = pd.DataFrame([application_data])

        print("[DEBUG] Step 2: Applying inference pipeline.")
        processed_df = _apply_inference_pipeline(input_df)
        print(
            f"[DEBUG] Step 3: Preprocessing complete. Shape: {processed_df.shape}, Columns: {processed_df.columns.tolist()}")

        print("[DEBUG] Step 4: Making prediction with model.")
        probability = model.predict_proba(processed_df)[0, 1]
        print(f"[DEBUG] Step 5: Prediction successful. Probability: {probability}")

        print("[DEBUG] Step 6: Generating SHAP values.")
        shap_values = explainer.shap_values(processed_df)
        print("[DEBUG] Step 7: SHAP values generated.")

        if isinstance(explainer.expected_value, list) and len(explainer.expected_value) > 1:
            base_value = explainer.expected_value[1]
        else:
            base_value = explainer.expected_value

        if isinstance(shap_values, list) and len(shap_values) > 1:
            shap_values_for_class_1 = shap_values[1][0]
        else:
            shap_values_for_class_1 = shap_values[0]

        print("[DEBUG] Step 8: Assembling final explanation.")
        explanation = {
            "base_value": float(base_value),
            "prediction_probability": float(probability),
            "feature_impacts": {
                feature: float(value) for feature, value in zip(processed_df.columns, shap_values_for_class_1)
            }
        }

        print("[DEBUG] Step 9: Returning result.")
        return explanation

    except Exception as e:
        print(f"\n🔥🔥🔥 [DEBUG] AN ERROR OCCURRED! 🔥🔥🔥")
        # Re-raise the exception so FastAPI shows it in the terminal
        raise e


# In src/interface/services/credit_service.py

# ... (add this at the end of the file) ...

def get_full_portfolio_data():
    """
    Calculates the current risk for all users in the mock DB.
    """
    portfolio = []
    for user_id, data in MOCK_DB.items():
        # Create a deep copy to avoid modifying the mock DB
        user_data = data.copy()

        # Get the prediction for the user's current data
        input_df = pd.DataFrame([user_data])
        processed_df = _apply_inference_pipeline(input_df)
        probability = model.predict_proba(processed_df)[0, 1]

        user_data['id'] = user_id
        user_data['risk_score'] = probability * 100
        user_data['status'] = 'Approved' if probability < 0.10 else 'Needs Review'  # Example logic
        user_data['last_updated'] = "2 hours ago"  # Mock data
        portfolio.append(user_data)

    return portfolio


def update_and_reevaluate(user_id: str, updated_features: dict):
    """
    Updates a user's data in the mock DB and returns the new risk probability.
    """
    if user_id not in MOCK_DB:
        raise ValueError(f"User with ID {user_id} not found.")

    # Update the user's data
    MOCK_DB[user_id].update(updated_features)

    # Re-calculate the risk score with the new data
    input_df = pd.DataFrame([MOCK_DB[user_id]])
    processed_df = _apply_inference_pipeline(input_df)
    new_probability = model.predict_proba(processed_df)[0, 1]

    return float(new_probability)