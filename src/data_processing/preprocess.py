import yaml
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

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
    df_imputed = df.copy()
    for col in columns:
        if col in df_imputed.columns and df_imputed[col].isnull().any():
            median = df_imputed[col].median()
            std = df_imputed[col].std()

            # Ensure std is not zero to avoid errors
            if std == 0 or pd.isna(std):
                std = 1

            null_count = df_imputed[col].isnull().sum()
            random_values = np.random.normal(loc=median, scale=std, size=null_count)

            # Clip values to be within the original column's min/max range
            min_val, max_val = df_imputed[col].min(), df_imputed[col].max()
            random_values = np.clip(random_values, min_val, max_val)

            df_imputed.loc[df_imputed[col].isnull(), col] = random_values

    return df_imputed

def one_hot_encode(df, columns):
    """
    Performs one-hot encoding on specified categorical columns,
    outputting integer values (1 for True, 0 for False).
    """
    df_encoded = df.copy()
    # Add dtype=int to ensure the output is 1s and 0s
    df_encoded = pd.get_dummies(
        df_encoded,
        columns=columns,
        dummy_na=False,
        drop_first=False,
        dtype=int
    )
    return df_encoded

def scale(df, numerical_cols_to_scale):
    print("Scaling numerical features...")
    scaled_df = df.copy()
    scaler = StandardScaler()
    scaler.fit(scaled_df[numerical_cols_to_scale])
    scaled_df[numerical_cols_to_scale] = scaler.transform(scaled_df[numerical_cols_to_scale])
    return scaled_df

def clean(df):
    categorical_cols = config['data']['categorical_final']
    numerical_cols = config['data']['numerical_final']

    target_col = config['data']['target']

    df_imputed_cat = impute_missing_category(df, categorical_cols)
    df_imputed_final = median_impute(df_imputed_cat, numerical_cols)

    df_encoded = one_hot_encode(df_imputed_final, categorical_cols)
    df_encoded = scale(df_encoded, numerical_cols)

    train_df, temp_df = train_test_split(
        df_encoded, test_size=0.3, random_state=42, stratify=df_encoded[target_col]
    )

    # Split the temporary set into validation (15%) and test (15%)
    val_df, test_df = train_test_split(
        temp_df, test_size=0.5, random_state=42, stratify=temp_df[target_col]
    )

    output_path = config['paths']['processed_data_directory']
    print(f"Train set shape: {train_df.shape}")
    print(f"Validation set shape: {val_df.shape}")
    print(f"Test set shape: {test_df.shape}")

    output_dir = config['paths']['processed_data_directory']
    train_df.to_csv(output_dir + "/train_data.csv", index=False)
    val_df.to_csv(output_dir + "/validation_data.csv", index=False)
    test_df.to_csv(output_dir + "/test_data.csv", index=False)

    return train_df, val_df, test_df