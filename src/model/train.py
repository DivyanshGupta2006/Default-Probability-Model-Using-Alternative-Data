# src/model/train.py

import pandas as pd
import yaml
from pathlib import Path
import argparse
from sklearn.metrics import roc_auc_score, average_precision_score

# Import your new model classes
from src.model.model import (
    LightGBMModel,
    XGBoostModel,
    CatBoostModel,
    LogisticRegressionModel,
    StackingEnsemble
)

# --- Config and Path Setup ---
# (Your existing config loading code remains here)
current_file_path = Path(__file__)
root_dir = current_file_path.parent.parent.parent
config_path = root_dir / "config.yaml"

with open(config_path, 'r') as file:
    config = yaml.safe_load(file)


def get_model(model_name):
    """Factory function to get a model instance by name."""
    models = {
        'lightgbm': LightGBMModel,
        'xgboost': XGBoostModel,
        'catboost': CatBoostModel,
        'logistic_regression': LogisticRegressionModel,
        'ensemble': StackingEnsemble
    }

    if model_name not in models:
        raise ValueError(f"Model '{model_name}' not recognized. Available models: {list(models.keys())}")

    if model_name == 'ensemble':
        # Define the base models for the ensemble here
        base_models = [
            LightGBMModel(),
            XGBoostModel()
        ]
        return StackingEnsemble(base_models=base_models)

    return models[model_name]()


def train(model_name, model_path):
    """
    Generic training script for a specified model.
    """
    print(f"--- Preparing to Train Model: {model_name} ---")

    # 1. Load Data
    data_dir = config['paths']['processed_data_directory']
    train_df = pd.read_csv(data_dir + "/train.csv")
    val_df = pd.read_csv(data_dir + "/validation.csv")

    # 2. Prepare Data
    id_col = config['data']['id']
    target_col = config['data']['target']

    X_train = train_df.drop(columns=[id_col, target_col])
    y_train = train_df[target_col]
    X_val = val_df.drop(columns=[id_col, target_col])
    y_val = val_df[target_col]

    # 3. Initialize Model using the factory function
    model = get_model(model_name)

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


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', type=str, required=True, help='Name of the model to train.')
    parser.add_argument('--path', type=str, required=True, help='Path to save the trained model.')
    args = parser.parse_args()

    train(model_name=args.model, model_path=args.path)