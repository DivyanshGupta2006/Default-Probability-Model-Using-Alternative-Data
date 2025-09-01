from sklearn.metrics import roc_auc_score, average_precision_score, accuracy_score

from src.utils import get_config, read_file

config = get_config.read_yaml_from_package()

def test_model(model):
    model = read_file.read_model_data(model+'_model.joblib')

    test_df = read_file.read_processed_data('clean_test_data.csv')

    # 3. Prepare Data
    id_col = config['data']['id']
    target_col = config['data']['target']
    drop_cols = config['data']['drop_cols']

    X_test = test_df.drop(columns=drop_cols)
    y_test = test_df[target_col]

    # 4. Evaluate
    test_preds = model.predict_proba(X_test)[:, 1]
    test_preds_class = (test_preds >= config['threshold']).astype(int)

    acc = accuracy_score(y_test, test_preds_class)
    auc = roc_auc_score(y_test, test_preds)
    pr_auc = average_precision_score(y_test, test_preds)

    print("\n--- Test Set Performance ---")
    print(f"Test accuracy: {acc:.4f}")
    print(f"Test ROC AUC: {auc:.4f}")
    print(f"Test PR AUC: {pr_auc:.4f}")