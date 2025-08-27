import numpy as np
import pandas as pd
from scipy.linalg import block_diag
import yaml
from pathlib import Path

current_file_path = Path(__file__)
root_dir = current_file_path.parent.parent.parent
config_path = root_dir / "config.yaml"

with open(config_path, 'r') as file:
    config = yaml.safe_load(file)

# --- Helper for categorical distributions ---
def create_categorical_distribution(categories, stats, n, nan_probability=0):
    """Generates a series of categorical data."""
    probs = np.array(stats) / np.sum(stats)
    if np.random.rand() < nan_probability:
        return pd.Series([np.nan] * n)
    return pd.Series(np.random.choice(categories, size=n, p=probs))


# --- Main fabrication function ---
def fabricate_features(merged_df, rng_seed=42):
    """
    Generates and adds synthetic features to the provided DataFrame.
    """
    print("Starting feature fabrication...")
    rng = np.random.default_rng(seed=rng_seed)
    n_samples = len(merged_df)

    # --- Feature Definitions ---
    feature_definitions = [
        # Financial Group
        {'name': "Recharge Frequency (per month)", 'short_name': 'RCHRG_FRQ', 'type': 'numeric',
         'params': (1.426, 0.57, 0, 20), 'corr_group': 'financial'},
        {'name': "Trading Accounts", 'short_name': 'TRD_ACC', 'type': 'numeric', 'params': (1.27, 0.9, 0, 10),
         'corr_group': 'financial'},
        {'name': "Revenue from Consumer Apps", 'short_name': 'REV_FRM_CNSMR_APPS', 'type': 'numeric',
         'params': (500, 200, 50, 2000), 'corr_group': 'financial'},
        {'name': "Number of Smart Cards", 'short_name': 'NO_OF_SMRT_CARD', 'type': 'numeric',
         'params': (2.6, 0.9, 0, 6), 'corr_group': 'financial'},
        {'name': "Number of Account Types", 'short_name': 'NO_TYPE_OF_ACC', 'type': 'numeric',
         'params': (2.05, 1.5, 0, 8), 'corr_group': 'financial'},
        # Compliance Group
        {'name': "Official Document Expiry (per year)", 'short_name': 'OFC_DOC_EXP', 'type': 'numeric',
         'params': (3, 2, 0, 12), 'corr_group': 'compliance'},
        {'name': "Default in GST filing (per quarter)", 'short_name': 'GST_FIL_DEF', 'type': 'numeric',
         'params': (0.39, 0.65, 0, 3), 'corr_group': 'compliance'},
        {'name': "Registered Vehicle Challans (per year)", 'short_name': 'REG_VEH_CHALLAN', 'type': 'numeric',
         'params': (0.12, 0.5, 0, 100), 'corr_group': 'compliance'},
        # Digital Group
        {'name': "SIM Card Failures", 'short_name': 'SIM_CARD_FAIL', 'type': 'numeric', 'params': (1.2, 0.8, 0, 60),
         'corr_group': 'digital'},
        {'name': "E-commerce Shopping Returns (per month)", 'short_name': 'ECOM_SHOP_RETURN', 'type': 'numeric',
         'params': (0.35, 0.7, 0, 25), 'corr_group': 'digital'},
        {'name': "Utility Bills (per month)", 'short_name': 'UTILITY_BIL', 'type': 'numeric',
         'params': (9500, 6500, 2500, 35000), 'corr_group': 'digital'},
        # Standalone Features
        {'name': "LinkedIn Data (Presence)", 'short_name': 'LINKEDIN_DATA', 'type': 'binary',
         'params': ((0, 1), (0.5, 0.5))},
        {'name': "Truecaller Flag", 'short_name': 'TRUECALR_FLAG', 'type': 'categorical',
         'params': (('Red', 'Blue', 'Golden'), (0.2, 0.75, 0.05))}
    ]

    # --- Separate features by type ---
    numeric_features = [f for f in feature_definitions if f['type'] == 'numeric']
    categorical_features = [f for f in feature_definitions if f['type'] == 'categorical']
    binary_features = [f for f in feature_definitions if f['type'] == 'binary']

    synthetic_df = pd.DataFrame(index=merged_df.index)

    # --- 1. Generate Correlated Numeric Features ---
    print("Generating correlated numeric features...")
    # Define correlation blocks
    corr_financial = np.array([
        # Recharge Freq, Trading Acc, Revenue Apps, Smart Cards, Acc Types
        [1.00, -0.15, 0.10, 0.05, -0.12],  # Recharge Frequency
        [-0.15, 1.00, 0.20, 0.10, 0.35],  # Trading Accounts
        [0.10, 0.20, 1.00, 0.15, 0.22],  # Revenue from Consumer Apps
        [0.05, 0.10, 0.15, 1.00, 0.08],  # Number of Smart Cards
        [-0.12, 0.35, 0.22, 0.08, 1.00]  # Number of Account Types
    ])
    # Realistic compliance correlations
    corr_compliance = np.array([
        # Doc Expiry, GST Default, Vehicle Challans
        [1.00, -0.10, -0.12],  # Official Document Expiry
        [-0.10, 1.00, 0.25],  # Default in GST filing
        [-0.12, 0.25, 1.00]  # Registered Vehicle Challans
    ])
    # Realistic digital correlations
    corr_digital = np.array([
        # SIM Failures, E-comm Returns, Utility Bills
        [1.00, -0.05, -0.28],  # SIM Card Failures
        [-0.05, 1.00, 0.15],  # E-commerce Shopping Returns
        [-0.28, 0.15, 1.00]  # Utility Bills
    ])


    correlation_matrix = block_diag(corr_financial, corr_compliance, corr_digital)

    # Generate base correlated data (standard normal)
    L = np.linalg.cholesky(correlation_matrix)
    uncorrelated = rng.normal(size=(n_samples, len(numeric_features)))
    correlated = uncorrelated @ L.T

    # Scale and clip the data
    for i, feature in enumerate(numeric_features):
        mean, std, min_val, max_val = feature['params']
        col_name = feature['short_name']

        # This is the correct way to map correlated columns to features
        col_data = correlated[:, i]

        # Scale to desired mean and std
        col_data = col_data * std + mean

        # Clip to min/max bounds
        col_data = np.clip(col_data, min_val, max_val)

        synthetic_df[col_name] = col_data.astype('float32')

    print("Generating categorical and binary features...")
    all_other_features = categorical_features + binary_features
    for feature in all_other_features:
        col_name = feature['name']
        categories, stats = feature['params']
        synthetic_df[col_name] = create_categorical_distribution(categories, stats, n_samples)

    print("Combining fabricated features with merged data...")
    final_df = pd.concat([merged_df.reset_index(drop=True), synthetic_df], axis=1)

    final_df.to_csv(f'{config['paths']['processed_data_directory']}/merged_data_fabricated.csv', index=False)

    return final_df