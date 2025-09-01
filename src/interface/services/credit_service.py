# src/interface/services/credit_service.py

"""
Credit Risk Assessment Service Module

This module provides the core business logic for credit risk assessment,
including predictions, explanations, and database operations.
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import pandas as pd
import numpy as np
import joblib
import shap
from datetime import datetime

# Import database modules
from ..database.connection import get_db_session, create_tables
from ..database.crud import UserCRUD, FeatureCRUD, AssessmentCRUD, PortfolioCRUD
from ..database.models import User, UserFeature, RiskAssessment

# Import the prediction module
from src.model.predict import make_prediction

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CreditRiskService:
    """
    Service class for credit risk assessment operations.
    Handles ML model predictions, SHAP explanations, and database operations.
    """

    def __init__(self):
        """Initialize the credit risk service with ML artifacts."""
        self.model = None
        self.preprocessor = None
        self.explainer = None
        self.is_initialized = False

        # Define paths
        try:
            self.root_dir = Path(__file__).parent.parent.parent.parent
        except NameError:
            self.root_dir = Path(".").absolute()

        self.model_dir = self.root_dir / "models"
        self.model_path = self.model_dir / "lightgbm_model.joblib"
        self.preprocessor_path = self.model_dir / "preprocessor.joblib"

        # Initialize components
        self._initialize_database()
        self._load_ml_artifacts()

    def _initialize_database(self):
        """Initialize database tables and seed data if needed."""
        try:
            create_tables()
            logger.info("✅ Database tables initialized successfully")

            # Check if we need to add sample data
            with get_db_session() as db:
                users = UserCRUD.get_all_active_users(db)
                if len(users) == 0:
                    logger.info("No users found. Database is ready for new data.")

        except Exception as e:
            logger.error(f"❌ Database initialization failed: {e}")
            raise

    def _load_ml_artifacts(self):
        """Load ML model, preprocessor, and initialize SHAP explainer."""
        try:
            # Load model and preprocessor
            if self.model_path.exists() and self.preprocessor_path.exists():
                self.model = joblib.load(self.model_path)
                self.preprocessor = joblib.load(self.preprocessor_path)

                # Initialize SHAP explainer with a small background dataset
                try:
                    self.explainer = shap.TreeExplainer(self.model.model)
                    self.is_initialized = True
                    logger.info("✅ ML artifacts loaded successfully")
                except Exception as e:
                    logger.warning(f"⚠️ SHAP explainer initialization failed: {e}")
                    self.explainer = None
            else:
                logger.warning("⚠️ ML artifacts not found. Service will use fallback predictions.")

        except Exception as e:
            logger.error(f"❌ Failed to load ML artifacts: {e}")
            self.is_initialized = False

    def _prepare_features_for_model(self, features_dict: Dict) -> pd.DataFrame:
        """
        Prepare feature dictionary for model input.
        Converts database column names to model expected format.
        """
        # Map database column names to model expected names (uppercase)
        model_features = {}
        for key, value in features_dict.items():
            # Convert snake_case to UPPERCASE
            model_key = key.upper()
            model_features[model_key] = value

        # Create DataFrame with single row
        return pd.DataFrame([model_features])

    def _generate_mock_prediction(self, features_dict: Dict) -> Dict:
        """
        Generate mock prediction for development/testing when ML artifacts are not available.
        """
        # Simple rule-based mock prediction
        utility_bill = features_dict.get('utility_bil', 10000)
        risk_score = min(0.9, max(0.1, utility_bill / 50000))

        return {
            "base_value": 0.3,
            "prediction_probability": risk_score,
            "feature_impacts": {
                "utility_bil": 0.15 if utility_bill > 15000 else -0.05,
                "region_rating_client": -0.08,
                "truecalr_flag": 0.06,
                "amt_drawings_current": 0.10,
                "rchrg_frq": -0.03
            }
        }

    def predict_with_explanation(self, features_dict: Dict) -> Dict:
        """
        Generate prediction with SHAP explanations.

        Args:
            features_dict: Dictionary of features with database column names

        Returns:
            Dictionary containing base_value, prediction_probability, and feature_impacts
        """
        try:
            # If ML artifacts are not loaded, use mock prediction
            if not self.is_initialized:
                logger.warning("Using mock prediction as ML artifacts are not loaded")
                return self._generate_mock_prediction(features_dict)

            # Prepare features for model
            input_df = self._prepare_features_for_model(features_dict)

            # Use the existing make_prediction function
            prediction_proba = make_prediction(input_df)

            # Extract probability for positive class
            if len(prediction_proba.shape) > 1:
                probability = float(prediction_proba[0, 1])
            else:
                probability = float(prediction_proba[0])

            # Generate SHAP explanations if available
            feature_impacts = {}
            base_value = 0.3  # Default base value

            if self.explainer is not None:
                try:
                    # Process input through preprocessor for SHAP
                    processed_df = self._apply_preprocessor(input_df)
                    shap_values = self.explainer.shap_values(processed_df)

                    # Handle different SHAP output formats
                    if isinstance(self.explainer.expected_value, list):
                        base_value = float(self.explainer.expected_value[1])
                    else:
                        base_value = float(self.explainer.expected_value)

                    if isinstance(shap_values, list):
                        shap_values_class1 = shap_values[1][0]
                    else:
                        shap_values_class1 = shap_values[0]

                    # Map SHAP values to feature names
                    for idx, col in enumerate(processed_df.columns):
                        feature_impacts[col] = float(shap_values_class1[idx])

                except Exception as e:
                    logger.warning(f"SHAP explanation failed: {e}")
                    # Use simplified feature impacts
                    feature_impacts = self._generate_simple_impacts(features_dict, probability)
            else:
                feature_impacts = self._generate_simple_impacts(features_dict, probability)

            return {
                "base_value": base_value,
                "prediction_probability": probability,
                "feature_impacts": feature_impacts
            }

        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            # Return mock prediction as fallback
            return self._generate_mock_prediction(features_dict)

    def _apply_preprocessor(self, input_df: pd.DataFrame) -> pd.DataFrame:
        """Apply preprocessing pipeline to input data."""
        if not self.preprocessor:
            return input_df

        try:
            numerical_cols = self.preprocessor.get('numerical_cols', [])
            categorical_cols = self.preprocessor.get('categorical_cols', [])
            encoder = self.preprocessor.get('encoder')
            scaler = self.preprocessor.get('scaler')

            # Prepare full dataframe with all expected columns
            full_df = pd.DataFrame(columns=numerical_cols + categorical_cols)
            for col in input_df.columns:
                if col in full_df.columns:
                    full_df[col] = input_df[col]

            # Process numerical and categorical features
            num_df = full_df[numerical_cols].fillna(0)
            cat_df = full_df[categorical_cols].fillna("Missing")

            # Apply transformations
            if encoder:
                encoded = encoder.transform(cat_df)
                encoded_df = pd.DataFrame(
                    encoded,
                    columns=encoder.get_feature_names_out(categorical_cols)
                )
            else:
                encoded_df = pd.DataFrame()

            if scaler:
                scaled = scaler.transform(num_df)
                scaled_df = pd.DataFrame(scaled, columns=numerical_cols)
            else:
                scaled_df = num_df

            # Combine processed features
            processed_df = pd.concat([scaled_df, encoded_df], axis=1)

            # Ensure we have all expected model features
            if self.model and hasattr(self.model.model, 'feature_name_'):
                expected_cols = self.model.model.feature_name_
                final_df = pd.DataFrame(columns=expected_cols)
                final_df = pd.concat([final_df, processed_df], ignore_index=True).fillna(0)
                return final_df[expected_cols]

            return processed_df

        except Exception as e:
            logger.error(f"Preprocessing failed: {e}")
            return input_df

    def _generate_simple_impacts(self, features_dict: Dict, probability: float) -> Dict:
        """Generate simplified feature impacts when SHAP is not available."""
        # Simple heuristic-based feature impacts
        impacts = {}

        # High impact features
        high_impact_features = ['utility_bil', 'amt_drawings_current', 'region_rating_client']
        medium_impact_features = ['truecalr_flag', 'rchrg_frq', 'no_of_smrt_card']

        for feature, value in features_dict.items():
            if feature in high_impact_features:
                # Higher values generally increase risk
                if isinstance(value, (int, float)):
                    impacts[feature] = 0.1 * (value / 10000) if probability > 0.5 else -0.05
                else:
                    impacts[feature] = 0.05
            elif feature in medium_impact_features:
                impacts[feature] = 0.03 if probability > 0.5 else -0.02
            else:
                impacts[feature] = 0.01

        return impacts

    def create_new_user(self, user_data: Dict, features_data: Dict) -> str:
        """
        Create a new user with initial assessment.

        Args:
            user_data: Dictionary containing user information (user_id, full_name, email, phone)
            features_data: Dictionary containing feature values

        Returns:
            user_id of the created user
        """
        try:
            with get_db_session() as db:
                # Check if user already exists
                existing_user = UserCRUD.get_user(db, user_data['user_id'])
                if existing_user:
                    raise ValueError(f"User {user_data['user_id']} already exists")

                # Create user
                user = UserCRUD.create_user(db, user_data)
                logger.info(f"Created user: {user.user_id}")

                # Create features
                features = FeatureCRUD.create_user_features(db, user.user_id, features_data)
                logger.info(f"Created features for user: {user.user_id}")

                # Generate initial assessment
                prediction_result = self.predict_with_explanation(features_data)

                # Store assessment
                assessment = AssessmentCRUD.create_assessment(
                    db,
                    user.user_id,
                    features.feature_id,
                    prediction_result,
                    "initial"
                )
                logger.info(f"Created initial assessment for user: {user.user_id}")

                return user.user_id

        except ValueError as ve:
            logger.error(f"User creation validation error: {ve}")
            raise
        except Exception as e:
            logger.error(f"Failed to create user: {e}")
            raise ValueError(f"Could not create user: {str(e)}")

    def update_user_and_reassess(
            self,
            user_id: str,
            updated_features: Dict,
            changed_by: str = "system"
    ) -> float:
        """
        Update user features and perform reassessment.

        Args:
            user_id: User identifier
            updated_features: Dictionary of features to update
            changed_by: Who made the change

        Returns:
            New probability of default
        """
        try:
            with get_db_session() as db:
                # Check user exists
                user = UserCRUD.get_user(db, user_id)
                if not user:
                    raise ValueError(f"User {user_id} not found")

                # Update features with audit trail
                new_features = FeatureCRUD.update_user_features(
                    db,
                    user_id,
                    updated_features,
                    changed_by
                )

                # Convert features to dictionary for prediction
                feature_dict = {
                    column.name: getattr(new_features, column.name)
                    for column in new_features.__table__.columns
                    if column.name not in ['feature_id', 'user_id', 'created_at', 'updated_at', 'is_current']
                       and getattr(new_features, column.name) is not None
                }

                # Generate new prediction
                prediction_result = self.predict_with_explanation(feature_dict)

                # Store new assessment
                assessment = AssessmentCRUD.create_assessment(
                    db,
                    user_id,
                    new_features.feature_id,
                    prediction_result,
                    "update"
                )

                logger.info(
                    f"Updated user {user_id} with new risk score: {prediction_result['prediction_probability']}")

                return float(prediction_result['prediction_probability'])

        except ValueError as ve:
            logger.error(f"Update validation error: {ve}")
            raise
        except Exception as e:
            logger.error(f"Failed to update user {user_id}: {e}")
            raise ValueError(f"Could not update user: {str(e)}")

    def get_portfolio_data(self, filters: Optional[Dict] = None) -> List[Dict]:
        """
        Get portfolio data with optional filtering.

        Args:
            filters: Optional dictionary with 'search', 'risk_level', 'status' keys

        Returns:
            List of user portfolio data
        """
        try:
            with get_db_session() as db:
                return PortfolioCRUD.get_portfolio_data(db, filters)
        except Exception as e:
            logger.error(f"Failed to get portfolio data: {e}")
            return []

    def get_user_risk_history(self, user_id: str, limit: int = 10) -> List[Dict]:
        """
        Get risk assessment history for a user.

        Args:
            user_id: User identifier
            limit: Maximum number of records to return

        Returns:
            List of assessment history records
        """
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
            logger.error(f"Failed to get risk history for {user_id}: {e}")
            return []


# Create singleton instance
_service_instance = None


def get_service() -> CreditRiskService:
    """Get or create the singleton service instance."""
    global _service_instance
    if _service_instance is None:
        _service_instance = CreditRiskService()
    return _service_instance


# --- Public API Functions ---
# These functions provide a simple interface for the routers

def predict_and_explain(application_data: Dict, store_in_db: bool = False, user_id: str = None) -> Dict:
    """
    Generate prediction with explanations.

    Args:
        application_data: Feature dictionary
        store_in_db: Whether to store results in database
        user_id: User ID if storing in database

    Returns:
        Prediction results with explanations
    """
    service = get_service()
    result = service.predict_with_explanation(application_data)

    if store_in_db and user_id:
        try:
            with get_db_session() as db:
                current_features = FeatureCRUD.get_current_features(db, user_id)
                if current_features:
                    AssessmentCRUD.create_assessment(
                        db,
                        user_id,
                        current_features.feature_id,
                        result,
                        "update"
                    )
        except Exception as e:
            logger.error(f"Failed to store assessment: {e}")

    return result


def create_new_user(user_data: Dict, features_data: Dict) -> str:
    """Create a new user with initial assessment."""
    service = get_service()
    return service.create_new_user(user_data, features_data)


def update_and_reevaluate(user_id: str, updated_features: Dict, changed_by: str = "system") -> float:
    """Update user features and reassess risk."""
    service = get_service()
    return service.update_user_and_reassess(user_id, updated_features, changed_by)


def get_full_portfolio_data(filters: Optional[Dict] = None) -> List[Dict]:
    """Get portfolio data with optional filtering."""
    service = get_service()
    return service.get_portfolio_data(filters)


def get_user_risk_history(user_id: str, limit: int = 10) -> List[Dict]:
    """Get user's risk assessment history."""
    service = get_service()
    return service.get_user_risk_history(user_id, limit)


# --- Backward Compatibility ---
# Mock database for backward compatibility (if needed)
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
    }
}