import joblib
import numpy as np
import torch
from pytorch_tabnet.tab_model import TabNetClassifier
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
        joblib.dump(self, path)
        print(f"Model saved to {path}")


# --- Individual Model Wrappers (CORRECTED) ---

class LightGBMModel(Model):
    def __init__(self, **kwargs):
        params = {'random_state': 42, 'class_weight': 'balanced'}
        params.update(kwargs) # Merge tuned params with defaults
        super().__init__(lgb.LGBMClassifier(**params))


class XGBoostModel(Model):
    def __init__(self, **kwargs):
        ratio = config['data']['zero_to_one_ratio']
        params = {'random_state': 42, 'eval_metric': 'logloss', 'scale_pos_weight': ratio}
        params.update(kwargs) # Merge tuned params with defaults
        super().__init__(xgb.XGBClassifier(**params))


class CatBoostModel(Model):
    def __init__(self, **kwargs):
        params = {'random_state': 42, 'verbose': 0, 'auto_class_weights': 'Balanced'}
        params.update(kwargs) # Merge tuned params with defaults
        super().__init__(cb.CatBoostClassifier(**params))


class LogisticRegressionModel(Model):
    def __init__(self, **kwargs):
        params = {'random_state': 42}
        params.update(kwargs) # Merge tuned params with defaults
        super().__init__(LogisticRegression(**params))


# (The rest of your model.py file remains the same)
# --- ZIBerModel, TabNetModel, StackingEnsemble etc. ---

class ZIBerModel(Model):
    """
    Zero-Inflated Bernoulli (ZIBer) Regression Model from the research paper.
    Fits using an Expectation-Maximization (EM) algorithm.
    """

    def __init__(self, params=None):
        if params is None:
            params = {
                'max_iter': 1000,
                'solver': 'liblinear',
                'C': 1.0,
                'random_state': 42
            }

        # Initialize two logistic regression models as described in the paper
        self.bernoulli_model = LogisticRegression(**params)  # For p_i, the event probability
        self.zero_inflation_model = LogisticRegression(**params)  # For delta_i, the structural zero probability

        # The 'model' attribute holds the class itself to ensure the entire object is saved
        super().__init__(self)

    def fit(self, X, y, X_zero_inflation=None, max_em_iter=10, tol=1e-5):
        """
        Fits the ZIBer model using the EM algorithm described in the paper.

        Args:
            X (pd.DataFrame): Features for the Bernoulli model (x_i).
            y (pd.Series): The binary target variable (y_i).
            X_zero_inflation (pd.DataFrame, optional): Features for the zero-inflation model (z_i).
                                                      If None, uses the same features as X.
            max_em_iter (int): Maximum number of iterations for the EM algorithm.
            tol (float): Tolerance for convergence.
        """
        print(f"--- Fitting {self.__class__.__name__} ---")

        if X_zero_inflation is None:
            X_zero_inflation = X

        # Initialize coefficients (beta and theta)
        beta = np.zeros(X.shape[1] + 1)
        theta = np.zeros(X_zero_inflation.shape[1] + 1)

        log_likelihood_prev = -np.inf

        for i in range(max_em_iter):
            # --- E-step: Estimate the latent variable w_i ---
            # This is the probability of an observation being a structural zero.

            p_i = 1 / (1 + np.exp(-(np.c_[np.ones(X.shape[0]), X] @ beta)))
            delta_i = 1 / (1 + np.exp(-(np.c_[np.ones(X_zero_inflation.shape[0]), X_zero_inflation] @ theta)))

            w = np.zeros_like(y, dtype=float)
            zeros_idx = (y == 0)

            # Update w only for the zero-valued observations as per Equation (13)
            w[zeros_idx] = delta_i[zeros_idx] / (1 - p_i[zeros_idx] * (1 - delta_i[zeros_idx]))

            # --- M-step: Update beta and theta by maximizing log-likelihoods ---

            # Fit the Bernoulli model on all data, weighted by (1 - w)
            self.bernoulli_model.fit(X, y, sample_weight=(1 - w))
            beta = np.r_[self.bernoulli_model.intercept_, self.bernoulli_model.coef_.flatten()]

            # Fit the zero-inflation model using w as the target
            # We use rounded w as target labels for the logistic regression
            self.zero_inflation_model.fit(X_zero_inflation, np.round(w))
            theta = np.r_[self.zero_inflation_model.intercept_, self.zero_inflation_model.coef_.flatten()]

            # --- Check for convergence ---
            p_i_new = self.bernoulli_model.predict_proba(X)[:, 1]
            delta_i_new = self.zero_inflation_model.predict_proba(X_zero_inflation)[:, 1]
            pi_i = (1 - delta_i_new) * p_i_new

            # Calculate log-likelihood based on Equation (7)
            log_likelihood = np.sum(y * np.log(pi_i + 1e-9) + (1 - y) * np.log(1 - pi_i + 1e-9))

            print(f"Iteration {i + 1}, Log-Likelihood: {log_likelihood:.4f}")

            if abs(log_likelihood - log_likelihood_prev) < tol:
                print("Convergence reached.")
                break
            log_likelihood_prev = log_likelihood

        return self

    def predict_proba(self, X, X_zero_inflation=None):
        """
        Generates probability predictions using the fitted ZIBer model.
        """
        if X_zero_inflation is None:
            X_zero_inflation = X

        # Predict p_i from the Bernoulli model
        p_i = self.bernoulli_model.predict_proba(X)[:, 1]

        # Predict delta_i from the zero-inflation model
        # We take the probability of the positive class (which corresponds to w_i = 1)
        delta_i = self.zero_inflation_model.predict_proba(X_zero_inflation)[:, 1]

        # Calculate final probability as pi_i = (1 - delta_i) * p_i
        pi_i = (1 - delta_i) * p_i

        # Return probabilities for class 0 (1 - pi_i) and class 1 (pi_i)
        return np.vstack([1 - pi_i, pi_i]).T

class TabNetModel(Model):
    """
    Wrapper for the TabNet model.
    """
    def __init__(self, params=None):
        if params is None:
            params = {
                'verbose': 0,
                'seed': 42,
            }
        # TabNetClassifier is not from sklearn, so we handle it slightly differently
        super().__init__(TabNetClassifier(**params))

    def fit(self, X, y):
        """Fits the model to the training data."""
        print(f"--- Fitting {self.__class__.__name__} ---")
        # TabNet requires numpy arrays
        X_np = X.to_numpy()
        y_np = y.to_numpy()

        # CORRECTED: Define the weighted loss function here
        loss_fn = torch.nn.CrossEntropyLoss(
            weight=torch.tensor([1.0, config['data']['zero_to_one_ratio']], dtype=torch.float32)
        )

        # Pass the loss function to the fit method
        self.model.fit(
            X_train=X_np,
            y_train=y_np,
            loss_fn=loss_fn,
            max_epochs=15
        )
        return self

    def predict_proba(self, X):
        """Generates probability predictions."""
        X_np = X.to_numpy()
        return self.model.predict_proba(X_np)


class LightGBMZIBerModel(Model):
    """
    A stacked model that first trains a LightGBM model and then uses its
    predictions as an additional feature for a ZIBer model.
    """
    def __init__(self, lgbm_params=None, ziber_params=None):
        # Initialize the base models that will be used internally
        self.lgbm = LightGBMModel(**(lgbm_params or {})).model
        self.ziber = ZIBerModel(params=ziber_params) # ZIBer wrapper expects a 'params' dict
        super().__init__(self) # The model is the class instance itself

    def fit(self, X, y):
        print("--- Fitting LightGBMZIBerModel ---")

        # 1. Train the LightGBM model first
        print("Fitting base LightGBM model...")
        self.lgbm.fit(X, y)

        # 2. Generate predictions from LightGBM to use as a new feature
        print("Generating LightGBM predictions as a new feature...")
        lgbm_preds = self.lgbm.predict_proba(X)[:, 1]

        # 3. Augment the feature set with the new predictions
        X_augmented = X.copy()
        X_augmented['lgbm_prediction'] = lgbm_preds

        # 4. Train the ZIBer model on the augmented data
        print("Fitting ZIBer model on augmented data...")
        self.ziber.fit(X_augmented, y)

        return self

    def predict_proba(self, X):
        """
        Generates final predictions by first predicting with LightGBM,
        augmenting the data, and then predicting with ZIBer.
        """
        # 1. Get predictions from the trained LightGBM model
        lgbm_preds = self.lgbm.predict_proba(X)[:, 1]

        # 2. Augment the input data with these predictions
        X_augmented = X.copy()
        X_augmented['lgbm_prediction'] = lgbm_preds

        # 3. Use the ZIBer model to make the final prediction
        return self.ziber.predict_proba(X_augmented)

    def save(self, path):
        """Saves the entire stacked model."""
        joblib.dump(self, path)
        print(f"LightGBM-ZIBer stacked model saved to {path}")

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