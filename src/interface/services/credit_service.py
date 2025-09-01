# src/interface/services/credit_service.py
#updated
import joblib
import pandas as pd
import shap
from pathlib import Path
from typing import Dict, List
from sqlalchemy.orm import Session

# Import database modules
from ..database.connection import get_db_session, create_tables
from ..database.crud import UserCRUD, FeatureCRUD, AssessmentCRUD, PortfolioCRUD
from ..database.models import User, UserFeature, RiskAssessment

# --- 1. SETUP & CONFIGURATION ---
try:
    ROOT_DIR = Path(__file__).parent.parent.parent.parent
except NameError:
    ROOT_DIR = Path(".").absolute()

MODEL_DIR = ROOT_DIR / "models"
MODEL_PATH = MODEL_DIR / "lightgbm_model.joblib"
PREPROCESSOR_PATH = MODEL_DIR / "preprocessor.joblib"
TRAIN_DATA_PATH = ROOT_DIR / "data" / "processed_data" / "clean_train_data.csv"


# --- 2. INITIALIZE SAMPLE DATA FUNCTION (DEFINE BEFORE USING) ---
def initialize_sample_data():
    """Initialize sample data for demo purposes"""
    with get_db_session() as db:
        # Check if users already exist
        existing_users = UserCRUD.get_all_active_users(db)
        if len(existing_users) > 0:
            return

        # Sample users data
        sample_users = [
            # {
            #     'user_id': 'USR001_John_Doe',
            #     'full_name': 'John Doe',
            #     'email': 'john.doe@email.com',
            #     'phone': '+91-9876543210'
            # },
            # {
            #     'user_id': 'USR002_Jane_Smith',
            #     'full_name': 'Jane Smith',
            #     'email': 'jane.smith@email.com',
            #     'phone': '+91-9876543211'
            # }
        ]

        sample_features = [
            {
                'name_education_type': 'Higher education',
                'name_seller_industry': 'Consumer electronics',
                'truecalr_flag': 'Blue',
                'region_rating_client': 2,
                'reg_region_not_live_region': 0,
                'reg_region_not_work_region': 0,
                'live_region_not_work_region': 0,
                'amt_drawings_atm_current': 5000.0,
                'amt_drawings_current': 7500.0,
                'amt_drawings_other_current': 0.0,
                'amt_drawings_pos_current': 2500.0,
                'cnt_drawings_atm_current': 2.0,
                'cnt_drawings_current': 10.0,
                'cnt_drawings_other_current': 0.0,
                'cnt_drawings_pos_current': 8.0,
                'sellerplace_area': 500,
                'rchrg_frq': 2.0,
                'trd_acc': 1.0,
                'ofc_doc_exp': 5,
                'gst_fil_def': 0,
                'sim_card_fail': 0,
                'ecom_shop_return': 1,
                'utility_bil': 9500.0,
                'reg_veh_challan': 0,
                'linkedin_data': 1,
                'rev_frm_uber_rapido': 0.0,
                'no_of_smrt_card': 2,
                'no_type_of_acc': 3
            },
            {
                'name_education_type': 'Secondary / secondary special',
                'name_seller_industry': 'Clothing',
                'truecalr_flag': 'Red',
                'region_rating_client': 3,
                'reg_region_not_live_region': 1,
                'reg_region_not_work_region': 1,
                'live_region_not_work_region': 0,
                'amt_drawings_atm_current': 15000.0,
                'amt_drawings_current': 20000.0,
                'amt_drawings_other_current': 100.0,
                'amt_drawings_pos_current': 4900.0,
                'cnt_drawings_atm_current': 5.0,
                'cnt_drawings_current': 25.0,
                'cnt_drawings_other_current': 1.0,
                'cnt_drawings_pos_current': 20.0,
                'sellerplace_area': 100,
                'rchrg_frq': 5.0,
                'trd_acc': 4.0,
                'ofc_doc_exp': 1,
                'gst_fil_def': 2,
                'sim_card_fail': 3,
                'ecom_shop_return': 4,
                'utility_bil': 15000.0,
                'reg_veh_challan': 2,
                'linkedin_data': 0,
                'rev_frm_uber_rapido': 8000.0,
                'no_of_smrt_card': 4,
                'no_type_of_acc': 5
            }
        ]

        # Create users and features
        for user_data, features_data in zip(sample_users, sample_features):
            try:
                # Create user
                user = UserCRUD.create_user(db, user_data)

                # Create features
                features = FeatureCRUD.create_user_features(db, user.user_id, features_data)

                # For initial demo, create a mock assessment since we might not have the ML model yet
                mock_assessment = {
                    "base_value": 0.2,
                    "prediction_probability": 0.35 if 'John' in user_data['full_name'] else 0.65,
                    "feature_impacts": {"utility_bil": 0.1, "region_rating_client": -0.05}
                }
                AssessmentCRUD.create_assessment(db, user.user_id, features.feature_id, mock_assessment, "initial")

            except Exception as e:
                print(f"Error creating sample user {user_data.get('user_id', 'Unknown')}: {e}")


# --- 3. LOAD ARTIFACTS AT STARTUP ---
model = None
preprocessor = None
explainer = None

try:
    # Initialize database first
    create_tables()

    # Try to load ML artifacts
    try:
        model = joblib.load(MODEL_PATH)
        preprocessor = joblib.load(PREPROCESSOR_PATH)

        # Use a small background dataset for the SHAP explainer
        if TRAIN_DATA_PATH.exists():
            train_df_sample = pd.read_csv(TRAIN_DATA_PATH).sample(100, random_state=42)
            id_col = 'SK_ID_CURR'
            target_col = 'TARGET'
            background_data = train_df_sample.drop(columns=[id_col, target_col])
            explainer = shap.TreeExplainer(model.model)
            print("✅ ML Model and SHAP explainer loaded successfully!")
        else:
            print("⚠️ Training data not found, SHAP explainer not initialized")

    except Exception as ml_error:
        print(f"⚠️ ML artifacts not loaded (this is okay for development): {ml_error}")

    # Initialize sample data
    initialize_sample_data()

    print("✅ Database initialized successfully!")

except Exception as e:
    print(f"❌ Error during initialization: {e}")


# --- 4. PREPROCESSING FUNCTION ---
def _apply_inference_pipeline(data: pd.DataFrame) -> pd.DataFrame:
    """Applies the saved preprocessing pipeline to new data."""
    if not preprocessor:
        raise RuntimeError("Preprocessor is not loaded.")

    numerical_cols = preprocessor['numerical_cols']
    categorical_cols = preprocessor['categorical_cols']
    encoder = preprocessor['encoder']
    scaler = preprocessor['scaler']

    input_df = data.copy()
    all_raw_cols = numerical_cols + categorical_cols
    full_raw_df = pd.DataFrame(columns=all_raw_cols)

    for col in input_df.columns:
        if col in full_raw_df.columns:
            full_raw_df[col] = input_df[col]

    num_df = full_raw_df[numerical_cols].fillna(0)
    cat_df = full_raw_df[categorical_cols].fillna("Missing")

    encoded_features = encoder.transform(cat_df)
    encoded_df = pd.DataFrame(encoded_features, columns=encoder.get_feature_names_out(categorical_cols))

    scaled_features = scaler.transform(num_df)
    scaled_df = pd.DataFrame(scaled_features, columns=numerical_cols)

    processed_input_df = pd.concat([scaled_df, encoded_df], axis=1)

    expected_model_columns = model.model.feature_name_
    final_df = pd.DataFrame(columns=expected_model_columns)
    final_df = pd.concat([final_df, processed_input_df], ignore_index=True).fillna(0)
    final_df = final_df[expected_model_columns]

    return final_df


# --- 5. ENHANCED SERVICE FUNCTIONS ---
def predict_and_explain(application_data: dict, store_in_db: bool = False, user_id: str = None):
    """Enhanced prediction function with optional database storage"""
    try:
        # If ML artifacts are not loaded, return mock data for development
        if not all([model, preprocessor, explainer]):
            print("⚠️ ML artifacts not loaded, returning mock prediction")
            mock_probability = 0.45  # Mock probability
            result = {
                "base_value": 0.2,
                "prediction_probability": mock_probability,
                "feature_impacts": {
                    "utility_bil": 0.1,
                    "region_rating_client": -0.05,
                    "truecalr_flag": 0.08,
                    "amt_drawings_current": 0.12
                }
            }
        else:
            # Real ML prediction
            input_df = pd.DataFrame([application_data])
            processed_df = _apply_inference_pipeline(input_df)
            probability = model.predict_proba(processed_df)[0, 1]
            shap_values = explainer.shap_values(processed_df)

            if isinstance(explainer.expected_value, list) and len(explainer.expected_value) > 1:
                base_value = explainer.expected_value[1]
            else:
                base_value = explainer.expected_value

            if isinstance(shap_values, list) and len(shap_values) > 1:
                shap_values_for_class_1 = shap_values[1][0]
            else:
                shap_values_for_class_1 = shap_values[0]

            result = {
                "base_value": float(base_value),
                "prediction_probability": float(probability),
                "feature_impacts": {
                    feature: float(value) for feature, value in zip(processed_df.columns, shap_values_for_class_1)
                }
            }

        # Store in database if requested
        if store_in_db and user_id:
            with get_db_session() as db:
                current_features = FeatureCRUD.get_current_features(db, user_id)
                if current_features:
                    AssessmentCRUD.create_assessment(db, user_id, current_features.feature_id, result, "update")

        return result

    except Exception as e:
        print(f"🔥 Error in prediction: {e}")
        raise e


def get_full_portfolio_data(filters: Dict = None) -> List[Dict]:
    """Get portfolio data from database"""
    try:
        with get_db_session() as db:
            return PortfolioCRUD.get_portfolio_data(db, filters)
    except Exception as e:
        print(f"Error getting portfolio data: {e}")
        return []


def update_and_reevaluate(user_id: str, updated_features: Dict, changed_by: str = "system") -> float:
    """Update user features and reevaluate risk"""
    try:
        with get_db_session() as db:
            # Update features
            new_features = FeatureCRUD.update_user_features(db, user_id, updated_features, changed_by)

            # Convert features to dict for prediction
            feature_dict = {
                column.name: getattr(new_features, column.name)
                for column in new_features.__table__.columns
                if column.name not in ['feature_id', 'user_id', 'created_at', 'updated_at', 'is_current']
                   and getattr(new_features, column.name) is not None
            }

            # Run prediction
            result = predict_and_explain(feature_dict)

            # Store assessment
            AssessmentCRUD.create_assessment(db, user_id, new_features.feature_id, result, "update")

            return float(result['prediction_probability'])

    except Exception as e:
        print(f"Error updating user {user_id}: {e}")
        raise ValueError(f"Could not update user {user_id}: {str(e)}")


def get_user_risk_history(user_id: str, limit: int = 10) -> List[Dict]:
    """Get user's risk assessment history"""
    try:
        with get_db_session() as db:
            assessments = AssessmentCRUD.get_user_assessment_history(db, user_id, limit)
            return [
                {
                    'assessed_at': assessment.assessed_at.isoformat(),
                    'prediction_probability': float(assessment.prediction_probability),
                    'risk_category': assessment.risk_category.value,
                    'assessment_type': assessment.assessment_type.value
                }
                for assessment in assessments
            ]
    except Exception as e:
        print(f"Error getting risk history for {user_id}: {e}")
        return []


def create_new_user(user_data: Dict, features_data: Dict) -> str:
    """Create a new user with features and initial assessment"""
    try:
        with get_db_session() as db:
            # Create user
            user = UserCRUD.create_user(db, user_data)

            # Create features
            features = FeatureCRUD.create_user_features(db, user.user_id, features_data)

            # Run initial assessment
            result = predict_and_explain(features_data)
            AssessmentCRUD.create_assessment(db, user.user_id, features.feature_id, result, "initial")

            return user.user_id

    except Exception as e:
        print(f"Error creating new user: {e}")
        raise ValueError(f"Could not create user: {str(e)}")


# --- 6. BACKWARD COMPATIBILITY (for existing code that uses MOCK_DB) ---
# Keep this for any existing code that might still reference the old mock database
MOCK_DB = {
    "USR001_John_Doe": {
        "NAME_EDUCATION_TYPE": "Higher education",
        "NAME_SELLER_INDUSTRY": "Consumer electronics",
        "TRUECALR_FLAG": "Blue",
        "REGION_RATING_CLIENT": 2,
        "REG_REGION_NOT_LIVE_REGION": 0,
        "REG_REGION_NOT_WORK_REGION": 0,
        "LIVE_REGION_NOT_WORK_REGION": 0,
        "AMT_DRAWINGS_ATM_CURRENT": 5000.0,
        "AMT_DRAWINGS_CURRENT": 7500.0,
        "AMT_DRAWINGS_OTHER_CURRENT": 0.0,
        "AMT_DRAWINGS_POS_CURRENT": 2500.0,
        "CNT_DRAWINGS_ATM_CURRENT": 2.0,
        "CNT_DRAWINGS_CURRENT": 10.0,
        "CNT_DRAWINGS_OTHER_CURRENT": 0.0,
        "CNT_DRAWINGS_POS_CURRENT": 8.0,
        "SELLERPLACE_AREA": 500,
        "RCHRG_FRQ": 2.0,
        "TRD_ACC": 1.0,
        "OFC_DOC_EXP": 5,
        "GST_FIL_DEF": 0,
        "SIM_CARD_FAIL": 0,
        "ECOM_SHOP_RETURN": 1,
        "UTILITY_BIL": 9500.0,
        "REG_VEH_CHALLAN": 0,
        "LINKEDIN_DATA": 1,
        "REV_FRM_UBER_RAPIDO": 0.0,
        "NO_OF_SMRT_CARD": 2,
        "NO_TYPE_OF_ACC": 3
    },
    "USR002_Jane_Smith": {
        "NAME_EDUCATION_TYPE": "Secondary / secondary special",
        "NAME_SELLER_INDUSTRY": "Clothing",
        "TRUECALR_FLAG": "Red",
        "REGION_RATING_CLIENT": 3,
        "REG_REGION_NOT_LIVE_REGION": 1,
        "REG_REGION_NOT_WORK_REGION": 1,
        "LIVE_REGION_NOT_WORK_REGION": 0,
        "AMT_DRAWINGS_ATM_CURRENT": 15000.0,
        "AMT_DRAWINGS_CURRENT": 20000.0,
        "AMT_DRAWINGS_OTHER_CURRENT": 100.0,
        "AMT_DRAWINGS_POS_CURRENT": 4900.0,
        "CNT_DRAWINGS_ATM_CURRENT": 5.0,
        "CNT_DRAWINGS_CURRENT": 25.0,
        "CNT_DRAWINGS_OTHER_CURRENT": 1.0,
        "CNT_DRAWINGS_POS_CURRENT": 20.0,
        "SELLERPLACE_AREA": 100,
        "RCHRG_FRQ": 5.0,
        "TRD_ACC": 4.0,
        "OFC_DOC_EXP": 1,
        "GST_FIL_DEF": 2,
        "SIM_CARD_FAIL": 3,
        "ECOM_SHOP_RETURN": 4,
        "UTILITY_BIL": 15000.0,
        "REG_VEH_CHALLAN": 2,
        "LINKEDIN_DATA": 0,
        "REV_FRM_UBER_RAPIDO": 8000.0,
        "NO_OF_SMRT_CARD": 4,
        "NO_TYPE_OF_ACC": 5
    }
}