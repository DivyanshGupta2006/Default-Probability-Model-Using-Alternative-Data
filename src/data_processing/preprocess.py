import yaml
from pathlib import Path
from src.utils import read_file

# --- File and Config Loading ---
current_file_path = Path(__file__)
root_dir = current_file_path.parent.parent.parent
config_path = root_dir / "config.yaml"

with open(config_path, 'r') as file:
    config = yaml.safe_load(file)

def impute_missing_category(df, columns):
    df_imputed = df.copy()
    for col in columns:
        if col in df_imputed.columns:
            if df_imputed[col].isnull().any():
                df_imputed.loc[:, col] = df_imputed[col].fillna('Missing')
    return df_imputed

def median_impute(df, columns):
    # ... (your numerical imputation function code)
    df_imputed = df.copy()
    for col in columns:
        if col in df_imputed.columns:
            # Corrected to avoid FutureWarning
            median_value = df_imputed[col].median()
            df_imputed.loc[:, col] = df_imputed[col].fillna(median_value)
    return df_imputed

def clean(df):
    categorical_cols = config['data']['categorical_fabricated']
    numerical_cols = config['data']['numerical_fabricated']

    df_imputed_cat = impute_missing_category(df, categorical_cols)
    df_imputed_final = median_impute(df_imputed_cat, numerical_cols)

    output_path = config['paths']['processed_data_directory'] + "/final_data.csv"
    df_imputed_final.to_csv(output_path, index=False)

    return df_imputed_final