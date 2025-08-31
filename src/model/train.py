import pandas as pd
from sklearn.metrics import roc_auc_score, average_precision_score

# Import your new model classes
from src.model.model import (
    LightGBMModel,
    XGBoostModel,
    CatBoostModel,
    LogisticRegressionModel,
    StackingEnsemble, TabNetModel, ZIBerModel
)
from src.utils import get_config, read_file

config = get_config.read_yaml_from_package()

def get_model(model_name, params):
    """Factory function to get a model instance by name."""
    models = {
        'lightgbm': LightGBMModel,
        'xgboost': XGBoostModel,
        'catboost': CatBoostModel,
        'logistic_regression': LogisticRegressionModel,
        'ziber': ZIBerModel,
        'tabnet': TabNetModel,
        'ensemble': StackingEnsemble
    }

    if model_name not in models:
        raise ValueError(f"Model '{model_name}' not recognized. Available models: {list(models.keys())}")

    if model_name == 'ensemble':
        # Define the base models for the ensemble here
        base_models = [
            LightGBMModel(),
            XGBoostModel(),
            CatBoostModel(),
            LogisticRegressionModel()
        ]
        return StackingEnsemble(base_models=base_models)

    if params is None:
        return models[model_name]()
    else:
        return models[model_name](**params)


def train_model(model_name, model_path, params=None):
    print(f"--- Preparing to Train Model: {model_name} ---")

    train_df = read_file.read_processed_data('clean_train_data.csv')
    val_df = read_file.read_processed_data('clean_val_data.csv')

    # 2. Prepare Data
    id_col = config['data']['id']
    target_col = config['data']['target']
    drop_cols = config['data']['drop_cols']

    X_train = train_df.drop(columns=drop_cols)
    y_train = train_df[target_col]
    X_val = val_df.drop(columns=drop_cols)
    y_val = val_df[target_col]

    # 3. Initialize Model using the factory function
    model = get_model(model_name, params)

    # 4. Train Model (uses the .fit() method from our base class)
    model.fit(X_train, y_train)

    # 5. Evaluate
    val_preds = model.predict_proba(X_val)[:, 1]
    auc = roc_auc_score(y_val, val_preds)
    pr_auc = average_precision_score(y_val, val_preds)
    print(f"Validation ROC AUC: {auc:.4f}")
    print(f"Validation PR AUC (AUC-PR): {pr_auc:.4f}")

    # 6. Save Model (uses the .save() method from our base class)
    model.save(model_path)