import pandas as pd
from sklearn.metrics import roc_auc_score, average_precision_score, accuracy_score
import optuna
import lightgbm as lgb
import xgboost as xgb
import catboost as cb

# Import your new model classes
from src.model.model import (
    LightGBMModel,
    XGBoostModel,
    CatBoostModel,
    LogisticRegressionModel,
    StackingEnsemble, TabNetModel, ZIBerModel, LightGBMZIBerModel
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
        'ensemble': StackingEnsemble,
        'lightgbm-ziber': LightGBMZIBerModel
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

def objective(trial, model_name):
    """Defines the search space for Optuna and returns the PR AUC score."""
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
    if model_name == 'lightgbm':
        params = {
            'objective': 'binary',
            'metric': 'aucpr',
            'n_estimators': trial.suggest_int('n_estimators', 500, 2000),
            'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.1),
            'num_leaves': trial.suggest_int('num_leaves', 20, 300),
            'max_depth': trial.suggest_int('max_depth', 5, 12),
            'lambda_l1': trial.suggest_float('lambda_l1', 1e-8, 10.0, log=True),
            'lambda_l2': trial.suggest_float('lambda_l2', 1e-8, 10.0, log=True),
            'class_weight': 'balanced',
            'random_state': 42,
            'verbose': -1
        }
        model = lgb.LGBMClassifier(**params)
    elif model_name == 'catboost':
        params = {
            'iterations': trial.suggest_int('iterations', 500, 2000),
            'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.1),
            'depth': trial.suggest_int('depth', 5, 12),
            'l2_leaf_reg': trial.suggest_float('l2_leaf_reg', 1, 10),
            'auto_class_weights': 'Balanced',
            'random_state': 42,
            'verbose': 0
        }
        model = cb.CatBoostClassifier(**params)
    else:
        raise ValueError(f"Tuning for model '{model_name}' is not defined.")

    model.fit(X_train, y_train)
    val_preds = model.predict_proba(X_val)[:, 1]
    pr_auc = average_precision_score(y_val, val_preds)
    return pr_auc

def tune_model_with_optuna(model_name, n_trials=10):
    """
    Runs an Optuna study to find the best hyperparameters for a given model.
    """
    print(f"--- Starting Hyperparameter Tuning for {model_name} ---")
    study = optuna.create_study(direction='maximize')
    study.optimize(lambda trial: objective(trial, model_name), n_trials=n_trials)

    print(f"\n--- Tuning Complete for {model_name} ---")
    print("Number of finished trials: ", len(study.trials))
    print("Best trial:")
    trial = study.best_trial

    print("  Value (PR AUC): ", trial.value)
    print("  Params: ")
    for key, value in trial.params.items():
        print(f"    {key}: {value}")

    return study.best_params

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
    model = get_model(model_name, params=params)

    # 4. Train Model (uses the .fit() method from our base class)
    model.fit(X_train, y_train)

    # 5. Evaluate
    val_preds = model.predict_proba(X_val)[:, 1]
    test_preds_class = (val_preds >= config['threshold']).astype(int)

    acc = accuracy_score(y_val, test_preds_class)
    auc = roc_auc_score(y_val, val_preds)
    pr_auc = average_precision_score(y_val, val_preds)
    print(f"Validation accuracy: {acc:.4f}")
    print(f"Validation ROC AUC: {auc:.4f}")
    print(f"Validation PR AUC (AUC-PR): {pr_auc:.4f}")

    # 6. Save Model (uses the .save() method from our base class)
    model.save(model_path)