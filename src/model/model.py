import joblib
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold
import lightgbm as lgb
import xgboost as xgb
import catboost as cb
import yaml
from pathlib import Path

current_file_path = Path(__file__)
root_dir = current_file_path.parent.parent.parent
config_path = root_dir / "config.yaml"

with open(config_path, 'r') as file:
    config = yaml.safe_load(file)

class Model:
    pass


class StackingEnsemble:
    """
    A stacking ensemble model that uses a meta-learner (Logistic Regression)
    to combine predictions from a list of base models.
    """

    def __init__(self, base_models, meta_learner=LogisticRegression(random_state=42)):
        self.base_models = base_models
        self.meta_learner = meta_learner
        self.base_models_trained = []

    def fit(self, X, y):
        print("--- Fitting Stacking Ensemble ---")

        # 1. Train base models on the full training data and store them
        for model in self.base_models:
            print(f"Fitting base model: {model.__class__.__name__}")
            model.fit(X, y)
            self.base_models_trained.append(model)

        # 2. Generate predictions from base models to be used as features for the meta-learner
        meta_features = self._get_meta_features(X)

        # 3. Train the meta-learner on the base model predictions
        print("Fitting meta-learner...")
        self.meta_learner.fit(meta_features, y)
        print("--- Ensemble Fitting Complete ---")
        return self

    def _get_meta_features(self, X):
        """Generates predictions from base models."""
        predictions = []
        for model in self.base_models_trained:
            # Use predict_proba to get probability estimates
            preds = model.predict_proba(X)[:, 1]
            predictions.append(preds)
        return np.column_stack(predictions)

    def predict_proba(self, X):
        """Make probability predictions with the ensemble."""
        # Generate predictions from base models
        meta_features = self._get_meta_features(X)
        # The meta-learner makes the final prediction
        return self.meta_learner.predict_proba(meta_features)

    def save(self, path):
        """Saves the entire ensemble model."""
        joblib.dump(self, path)
        print(f"Ensemble model saved to {path}")

# --- You can add individual model classes here if needed for more complex logic ---
# For now, we will instantiate them directly in the training script for simplicity.