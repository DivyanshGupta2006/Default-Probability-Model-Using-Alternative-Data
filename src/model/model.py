import joblib
import numpy as np
from sklearn.linear_model import LogisticRegression
import lightgbm as lgb
import xgboost as xgb
import catboost as cb

from src.utils import get_config

config = get_config.read_yaml_from_package()

class Model:
    """
    Abstract base class for all models.
    Defines the standard interface for training, prediction, and saving.
    """

    def __init__(self, model):
        self.model = model

    def fit(self, X, y):
        """Fits the model to the training data."""
        print(f"--- Fitting {self.__class__.__name__} ---")
        self.model.fit(X, y)
        return self

    def predict_proba(self, X):
        """Generates probability predictions."""
        return self.model.predict_proba(X)

    def save(self, path):
        """Saves the trained model to a file."""
        joblib.dump(self.model, path)
        print(f"Model saved to {path}")


# --- Individual Model Wrappers ---

class LightGBMModel(Model):
    def __init__(self, params=None):
        if params is None:
            params = {'random_state': 42, 'class_weight': 'balanced'}
        super().__init__(lgb.LGBMClassifier(**params))


class XGBoostModel(Model):
    def __init__(self, params=None):
        if params is None:
            ratio = config['data']['zero_to_one_ratio']
            params = {'random_state': 42, 'eval_metric': 'logloss', 'scale_pos_weight': ratio}
            super().__init__(xgb.XGBClassifier(**params))
        super().__init__(xgb.XGBClassifier(**params))


class CatBoostModel(Model):
    def __init__(self, params=None):
        if params is None:
            params = {'random_state': 42, 'verbose': 0, 'auto_class_weights': 'Balanced'}
        super().__init__(cb.CatBoostClassifier(**params))


class LogisticRegressionModel(Model):
    def __init__(self, params=None):
        if params is None:
            params = {'random_state': 42}
        super().__init__(LogisticRegression(**params))


# --- Ensemble Model ---

class StackingEnsemble(Model):
    """
    A stacking ensemble model that uses a meta-learner to combine predictions
    from a list of base models.
    """

    def __init__(self, base_models, meta_learner=None):
        if meta_learner is None:
            meta_learner = LogisticRegressionModel().model  # Use the underlying sklearn model

        self.base_models = base_models
        self.meta_learner = meta_learner
        super().__init__(self)  # The model is the ensemble class itself

    def fit(self, X, y):
        print("--- Fitting Stacking Ensemble ---")
        # 1. Train base models and generate meta-features
        meta_features = self._get_meta_features(X, y, train_mode=True)
        # 2. Train the meta-learner on the base model predictions
        print("Fitting meta-learner...")
        self.meta_learner.fit(meta_features, y)
        print("--- Ensemble Fitting Complete ---")
        return self

    def _get_meta_features(self, X, y=None, train_mode=False):
        """Generates predictions from base models."""
        predictions = []

        if train_mode:
            # During training, we train the base models
            for model_wrapper in self.base_models:
                print(f"Fitting base model: {model_wrapper.__class__.__name__}")
                model_wrapper.fit(X, y)
                preds = model_wrapper.predict_proba(X)[:, 1]
                predictions.append(preds)
        else:
            # During prediction, we use the already-trained base models
            for model_wrapper in self.base_models:
                preds = model_wrapper.predict_proba(X)[:, 1]
                predictions.append(preds)

        return np.column_stack(predictions)

    def predict_proba(self, X):
        """Make probability predictions with the ensemble."""
        meta_features = self._get_meta_features(X, train_mode=False)
        return self.meta_learner.predict_proba(meta_features)

    def save(self, path):
        """Saves the entire ensemble model."""
        joblib.dump(self, path)  # Save the entire ensemble instance
        print(f"Ensemble model saved to {path}")