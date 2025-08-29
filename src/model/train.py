import numpy as np
import pandas as pd
import yaml
from pathlib import Path


current_file_path = Path(__file__)
root_dir = current_file_path.parent.parent.parent
config_path = root_dir / "config.yaml"

with open(config_path, 'r') as file:
    config = yaml.safe_load(file)

def train_model():
    return 0


import pandas as pd
import yaml
from pathlib import Path
import argparse
from sklearn.metrics import roc_auc_score, average_precision_score
from model import StackingEnsemble
import lightgbm as lgb
import xgboost as xgb
import catboost as cb
from sklearn.linear_model import LogisticRegression

# --- Config and Path Setup ---
current_file_path = Path(__file__)
root_dir = current_file_path.parent.parent.parent
config_path = root_dir / "config.yaml"

with open(config_path, 'r') as file:
    config = yaml.safe_load(file)


def train(model_name, model_path):
    """
    Generic training script for a specified model.
    """
    print(f"--- Training Model: {model_name} ---")

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

    # 3. Initialize Model
    models = {
        'lightgbm': lgb.LGBMClassifier(random_state=42),
        'xgboost': xgb.XGBClassifier(random_state=42, use_label_encoder=False, eval_metric='logloss'),
        'catboost': cb.CatBoostClassifier(random_state=42, verbose=0),
        'logistic_regression': LogisticRegression(random_state=42),
        'ensemble': StackingEnsemble(
            base_models=[
                lgb.LGBMClassifier(random_state=42),
                xgb.XGBClassifier(random_state=42, use_label_encoder=False, eval_metric='logloss')
            ]
        )
    }

    if model_name not in models:
        raise ValueError(f"Model '{model_name}' not recognized. Available models: {list(models.keys())}")

    model = models[model_name]

    # 4. Train Model
    model.fit(X_train, y_train)

    # 5. Evaluate
    val_preds = model.predict_proba(X_val)[:, 1]
    auc = roc_auc_score(y_val, val_preds)
    pr_auc = average_precision_score(y_val, val_preds)
    print(f"Validation ROC AUC: {auc:.4f}")
    print(f"Validation PR AUC: {pr_auc:.4f}")

    # 6. Save Model
    model.save(model_path) if hasattr(model, 'save') else joblib.dump(model, model_path)
    print(f"Model saved to {model_path}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', type=str, required=True, help='Name of the model to train.')
    parser.add_argument('--path', type=str, required=True, help='Path to save the trained model.')
    args = parser.parse_args()

    train(model_name=args.model, model_path=args.path)
