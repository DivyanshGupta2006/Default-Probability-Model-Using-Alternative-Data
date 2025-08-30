import numpy as np
import pandas as pd
import os
import joblib
from sklearn.preprocessing import StandardScaler, MinMaxScaler, OneHotEncoder

from src.utils import get_config

config = get_config.read_yaml_from_package()

def categorical_impute(df, columns):
    df_imputed = df.copy()
    for col in columns:
        if col in df_imputed.columns:
            df_imputed[columns] = df_imputed[columns].fillna('Missing')
    return df_imputed

def median_impute(df, columns):
    df_imputed = df.copy()
    imputation_stats = {}
    for col in columns:
        if col in df_imputed.columns and df_imputed[col].isnull().any():
            loc = df_imputed[col].median()
            std = df_imputed[col].std()
            if std == 0 or pd.isna(std):
                std = 1
            min_val, max_val = df_imputed[col].min(), df_imputed[col].max()
            imputation_stats[col] = {'loc': loc, 'std': std if std > 0 else 1, 'min': min_val, 'max': max_val}

            stats = imputation_stats[col]
            null_count = df_imputed[col].isnull().sum()

            random_values = np.random.normal(loc=stats['loc'], scale=stats['std'], size=null_count)
            random_values = np.clip(random_values, stats['min'], stats['max'])

            df_imputed.loc[df_imputed[col].isnull(), col] = random_values

    return df_imputed, imputation_stats

def apply_imputation(df, columns, imputation_stats):
    df_imputed = df.copy()
    for col in columns:
        if col in df_imputed.columns and df_imputed[col].isnull().any():
            stats = imputation_stats[col]
            null_count = df_imputed[col].isnull().sum()

            random_values = np.random.normal(loc=stats['loc'], scale=stats['std'], size=null_count)
            random_values = np.clip(random_values, stats['min'], stats['max'])

            df_imputed.loc[df_imputed[col].isnull(), col] = random_values
    return df_imputed

def mean_impute(df, columns):
    df_imputed = df.copy()
    imputation_stats = {}
    for col in columns:
        if col in df_imputed.columns and df_imputed[col].isnull().any():
            loc = df_imputed[col].mean()
            std = df_imputed[col].std()
            if std == 0 or pd.isna(std):
                std = 1
            min_val, max_val = df_imputed[col].min(), df_imputed[col].max()
            imputation_stats[col] = {'loc': loc, 'std': std if std > 0 else 1, 'min': min_val, 'max': max_val}

            stats = imputation_stats[col]
            null_count = df_imputed[col].isnull().sum()

            random_values = np.random.normal(loc=stats['loc'], scale=stats['std'], size=null_count)
            random_values = np.clip(random_values, stats['min'], stats['max'])

            df_imputed.loc[df_imputed[col].isnull(), col] = random_values

    return df_imputed, imputation_stats

def standar_scale(df, numerical_cols_to_scale):
    print("Scaling numerical features...")
    scaled_df = df.copy()
    scaler = StandardScaler()
    scaler.fit(scaled_df[numerical_cols_to_scale])
    scaled_df[numerical_cols_to_scale] = scaler.transform(scaled_df[numerical_cols_to_scale])
    return scaled_df, scaler

def min_max_scale(df, numerical_cols_to_scale):
    print("Scaling numerical features...")
    scaled_df = df.copy()
    scaler = MinMaxScaler()
    scaler.fit(scaled_df[numerical_cols_to_scale])
    scaled_df[numerical_cols_to_scale] = scaler.transform(scaled_df[numerical_cols_to_scale])
    return scaled_df, scaler

def one_hot_encode(df, categorical_cols):
    df_to_encode = df.copy()
    encoder = OneHotEncoder(handle_unknown='ignore', sparse_output=False)

    # FIT on data
    encoder.fit(df_to_encode[categorical_cols])

    # TRANSFORM and create new DataFrames
    encoded_cols = encoder.get_feature_names_out(categorical_cols)
    df_encoded = pd.DataFrame(encoder.transform(df_to_encode[categorical_cols]), index=df_to_encode.index,
                                 columns=encoded_cols)

    df_to_encode = df_to_encode.drop(columns=categorical_cols)

    # Concatenate numerical and encoded categorical data
    df_final = pd.concat([df_to_encode, df_encoded], axis=1)

    return df_final, encoded_cols, encoder

def preprocess_pipeline(
    data: pd.DataFrame,
    imputation_strategy: str = 'median',
    scaling_strategy: str = 'standard',
    encode: bool = True
) -> (pd.DataFrame, pd.DataFrame, pd.DataFrame):
    numerical_cols = config['data']['numerical_final']
    categorical_cols = config['data']['categorical_final']

    df = data.copy()

    fitted_objects = {}

    fitted_objects['numerical_cols'] = numerical_cols
    fitted_objects['categorical_cols'] = categorical_cols

    print(f"Imputing missing values using '{imputation_strategy}' strategy...")
    if imputation_strategy == 'median':
        df, fitted_objects['imputation_values'] = median_impute(df, numerical_cols)
    elif imputation_strategy == 'mean':
        df, fitted_objects['imputation_values'] = mean_impute(df, numerical_cols)

    # df.to_csv(config['paths']['processed_data_directory'] + "/before_cat_impute_data.csv", index=False)

    df = categorical_impute(df, categorical_cols)

    # df.to_csv(config['paths']['processed_data_directory'] + "/before_encoding_data.csv", index=False)

    if encode:
        print("One-hot encoding categorical features...")
        df, fitted_objects['encoded_columns'], fitted_objects['encoder'] = one_hot_encode(df, categorical_cols)

    # df.to_csv(config['paths']['processed_data_directory'] + "/before_scaling_data.csv", index=False)

    print(f"Scaling numerical features using '{scaling_strategy}' scaler...")
    if scaling_strategy == 'standard':
        df, fitted_objects['scaler'] = standar_scale(df, numerical_cols)
    elif scaling_strategy == 'minmax':
        df, fitted_objects['scaler'] = min_max_scale(df, numerical_cols)

    print("Saving fitted objects...")
    # --- Save the fitted objects for future use ---
    data_dir = config['paths']['model_data_directory']
    if not os.path.exists(data_dir):
        print(f"Creating directory: {data_dir}")
        os.makedirs(data_dir)
    else:
        print(f"Directory already exists: {data_dir}")
    preprocessor_path = data_dir + "preprocessor.joblib"
    joblib.dump(fitted_objects, preprocessor_path)
    print(f"\nPreprocessing pipeline saved to: {preprocessor_path}")

    print("Finalizing datasets...")
    return df


def apply_pipeline(data: pd.DataFrame,
    encode: bool = True
) -> pd.DataFrame:
    print("--- Applying Inference Preprocessing Pipeline ---")

    preprocessor_path = config['paths']['model_data_directory'] + "preprocessor.joblib"
    fitted_objects = joblib.load(preprocessor_path)
    print(f"Preprocessor loaded successfully from {preprocessor_path}")

    imputation_values = fitted_objects['imputation_values']
    scaler = fitted_objects['scaler']
    encoder = fitted_objects['encoder']

    numerical_cols = fitted_objects['numerical_cols']
    categorical_cols = fitted_objects['categorical_cols']

    processed_df = data.copy()


    # Apply transformations in the exact same order
    processed_df = apply_imputation(processed_df, numerical_cols, imputation_values)
    # processed_df.to_csv(config['paths']['processed_data_directory'] + "/before_cat_impute_data.csv", index=False)
    processed_df = categorical_impute(processed_df, categorical_cols)

    final_df = processed_df.copy()

    if encode:
        # processed_df.to_csv(config['paths']['processed_data_directory'] + "/before_encode_data.csv", index=False)
        encoded_cols = fitted_objects['encoded_columns']
        df_encoded = pd.DataFrame(encoder.transform(processed_df[categorical_cols]), index=processed_df.index,
                              columns=encoded_cols)
        final_df = pd.concat([processed_df.drop(columns=categorical_cols), df_encoded], axis=1)

    # processed_df.to_csv(config['paths']['processed_data_directory'] + "/before_scaling_data.csv", index=False)
    final_df[numerical_cols] = scaler.transform(final_df[numerical_cols])

    print("Inference Preprocessing Complete!")
    return final_df

def clean(
        data: pd.DataFrame,
        imputation_strategy: str = 'median',
        scaling_strategy: str = 'standard',
        encode: bool = True,
        use_saved: bool = False,
        name: str = "clean_data.csv",
):
    if use_saved:
        final_df = apply_pipeline(data, encode=encode)
        final_df.to_csv(config['paths']['processed_data_directory'] + name, index=False)
        return final_df
    else:
        final_df= preprocess_pipeline(
            data=data,
            imputation_strategy=imputation_strategy,
            scaling_strategy=scaling_strategy,
            encode=encode,
        )

        final_df.to_csv(config['paths']['processed_data_directory'] + name, index=False)

        return final_df