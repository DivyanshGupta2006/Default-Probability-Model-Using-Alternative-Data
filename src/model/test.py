import pandas as pd
import yaml
from pathlib import Path
import argparse
import joblib
from sklearn.metrics import roc_auc_score, average_precision_score

# --- Config and Path Setup ---
current_file_path = Path(__file__)
root_dir = current_file_path.parent.parent.parent
config_path = root_dir / "config.yaml"

with open(config_path, 'r') as file:
    config = yaml.safe_load(file)


def test(model):
    """
    Evaluates a trained model on the hold-out test set.
    """
    model_path = config['paths']['model_path'] + model
    print(f"--- Testing Model from: {model_path} ---")

    # 1. Load Model
    model = joblib.load(model_path)

    # 2. Load Test Data
    data_dir = config['paths']['processed_data_directory']
    test_df = pd.read_csv(data_dir + "/test.csv")

    # 3. Prepare Data
    id_col = config['data']['id']
    target_col = config['data']['target']

    X_test = test_df.drop(columns=[id_col, target_col])
    y_test = test_df[target_col]

    # 4. Evaluate
    test_preds = model.predict_proba(X_test)[:, 1]
    auc = roc_auc_score(y_test, test_preds)
    pr_auc = average_precision_score(y_test, test_preds)

    print("\n--- Test Set Performance ---")
    print(f"Test ROC AUC: {auc:.4f}")
    print(f"Test PR AUC: {pr_auc:.4f}")