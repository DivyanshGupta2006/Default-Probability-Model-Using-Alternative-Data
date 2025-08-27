import pandas as pd
import numpy as np
import yaml
from pathlib import Path
from src.utils import read_file

current_file_path = Path(__file__)
root_dir = current_file_path.parent.parent
config_path = root_dir / "config.yaml"

with open(config_path, 'r') as file:
    config = yaml.safe_load(file)

def impute_missing_category(df, columns):
    """
    Imputes missing values in specified categorical columns by creating
    a new 'Missing' category.

    Args:
        df (pd.DataFrame): The DataFrame with missing values.
        columns (list): A list of categorical column names to impute.

    Returns:
        pd.DataFrame: The DataFrame with missing values imputed.
    """
    df_imputed = df.copy()  # Create a copy to avoid changing the original DataFrame
    for col in columns:
        if col in df_imputed.columns:
            if df_imputed[col].isnull().any():
                df_imputed[col].fillna('Missing', inplace=True)
                print(f"✅ Imputed NaN values in '{col}' with 'Missing' category.")
            else:
                print(f"ℹ No NaN values found in '{col}'.")
        else:
            print(f"⚠ Warning: Column '{col}' not found in the DataFrame.")
    return df_imputed

df = read_file.read_processed_data("merged_data.csv")
output_path = config['paths']['processed_data_directory'] + "/processed_data.csv"

# 2. List categorical columns where you want to impute missing values
categorical_cols = ['CODE_GENDER', 'FLAG_OWN_CAR', 'FLAG_OWN_REALTY',]  # example columns

# 3. Apply the function
df_imputed = impute_missing_category(df, categorical_cols)

# 4. Save the new DataFrame
df_imputed.to_csv(output_path, index=False)

print(f"\n✅ Cleaned dataset saved at: {output_path}")