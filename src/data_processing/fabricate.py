import numpy as np
import pandas as pd
from pathlib import Path
from scipy.linalg import block_diag

from src.utils import get_config

config = get_config.read_yaml_from_package()

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
    Anchors synthetic numeric features to real columns where specified.
    """
    print("🚀 Starting feature fabrication...")
    rng = np.random.default_rng(seed=rng_seed)
    n_samples = len(merged_df)

    synthetic_df = pd.DataFrame(index=merged_df.index)

    # --- 💡 CUSTOMIZE HERE: Define features and their relationships ---
    # In fabricate.py, inside the fabricate_features function:

    # --- 💡 CUSTOMIZE HERE: Define features and their relationships ---
    feature_definitions = [
        # --- Financial Group ---
        {'name': "Recharge Frequency (per month)", 'short_name': 'RCHRG_FRQ', 'type': 'numeric',
         'params': (1.426, 0.57, 0, 20), 'corr_group': 'financial'},
        {'name': "Trading Accounts", 'short_name': 'TRD_ACC', 'type': 'numeric', 'params': (1.27, 0.9, 0, 10),
         'corr_group': 'financial'},
        # Anchored to cash flow
        {'name': "Revenue from Consumer Apps", 'short_name': 'REV_FRM_CNSMR_APPS', 'type': 'numeric',
         'params': (500, 200, 50, 2000), 'corr_group': 'financial', 'corr_with': 'AMT_DRAWINGS_CURRENT',
         'corr_value': 0.3},
        # Anchored to digital payment usage
        {'name': "Number of Smart Cards", 'short_name': 'NO_OF_SMRT_CARD', 'type': 'numeric',
         'params': (2.6, 0.9, 0, 6), 'corr_group': 'financial', 'corr_with': 'CNT_DRAWINGS_POS_CURRENT',
         'corr_value': 0.35},
        {'name': "Number of Account Types", 'short_name': 'NO_TYPE_OF_ACC', 'type': 'numeric',
         'params': (2.05, 1.5, 0, 8), 'corr_group': 'financial'},

        # --- Compliance Group ---
        {'name': "Official Document Expiry (per year)", 'short_name': 'OFC_DOC_EXP', 'type': 'numeric',
         'params': (3, 2, 0, 12), 'corr_group': 'compliance'},
        # Anchored to regional risk
        {'name': "Default in GST filing (per quarter)", 'short_name': 'GST_FIL_DEF', 'type': 'numeric',
         'params': (0.39, 0.65, 0, 3), 'corr_group': 'compliance', 'corr_with': 'REGION_RATING_CLIENT',
         'corr_value': 0.2},
        # Anchored to regional risk
        {'name': "Registered Vehicle Challans (per year)", 'short_name': 'REG_VEH_CHALLAN', 'type': 'numeric',
         'params': (0.12, 0.5, 0, 100), 'corr_group': 'compliance', 'corr_with': 'REGION_RATING_CLIENT',
         'corr_value': 0.25},

        # --- Digital Group ---
        # Anchored to client stability
        {'name': "SIM Card Failures", 'short_name': 'SIM_CARD_FAIL', 'type': 'numeric', 'params': (1.2, 0.8, 0, 60),
         'corr_group': 'digital', 'corr_with': 'REG_REGION_NOT_WORK_REGION', 'corr_value': 0.15},
        # Anchored to digital payment usage
        {'name': "E-commerce Shopping Returns (per month)", 'short_name': 'ECOM_SHOP_RETURN', 'type': 'numeric',
         'params': (0.35, 0.7, 0, 25), 'corr_group': 'digital', 'corr_with': 'CNT_DRAWINGS_POS_CURRENT',
         'corr_value': 0.3},
        # Anchored to cash flow
        {'name': "Utility Bills (per month)", 'short_name': 'UTILITY_BIL', 'type': 'numeric',
         'params': (9500, 6500, 2500, 35000), 'corr_group': 'digital', 'corr_with': 'AMT_DRAWINGS_CURRENT',
         'corr_value': 0.4},

        # --- Standalone Features (can remain independent) ---
        {'name': "LinkedIn Data (Presence)", 'short_name': 'LINKEDIN_DATA', 'type': 'binary',
         'params': ((0, 1), (0.5, 0.5))},
        {'name': "Truecaller Flag", 'short_name': 'TRUECALR_FLAG', 'type': 'categorical',
         'params': (('Red', 'Blue', 'Golden'), (0.2, 0.75, 0.05))}
    ]
    # --- Separate features by type ---
    numeric_features = [f for f in feature_definitions if f['type'] == 'numeric']
    categorical_features = [f for f in feature_definitions if f['type'] == 'categorical']
    binary_features = [f for f in feature_definitions if f['type'] == 'binary']

    # --- 1. Generate Correlated Numeric Features ---
    print("Generating correlated numeric features...")
    # (Your correlation matrices for financial, compliance, digital go here)
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
    L = np.linalg.cholesky(correlation_matrix)
    uncorrelated = rng.normal(size=(n_samples, len(numeric_features)))
    correlated = uncorrelated @ L.T

    # Scale, clip, and ANCHOR the data
    for i, feature in enumerate(numeric_features):
        mean, std, min_val, max_val = feature['params']
        col_name = feature['short_name']

        correlated_noise = pd.Series(correlated[:, i], index=merged_df.index)

        # Check if this feature should be anchored to a real one
        if 'corr_with' in feature and feature['corr_with'] in merged_df.columns:
            anchor_col_name = feature['corr_with']
            r = feature['corr_value']

            print(f"  - Anchoring '{col_name}' to '{anchor_col_name}' (r={r})")

            anchor_col = merged_df[anchor_col_name]
            anchor_std = (anchor_col - anchor_col.mean()) / anchor_col.std()

            # Combine the real data anchor with the generated correlated noise
            final_col_std = r * anchor_std + np.sqrt(1 - r ** 2) * correlated_noise

            # Rescale to the synthetic feature's desired mean and std
            col_data = final_col_std * std + mean
        else:
            # Fallback for un-anchored features (original logic)
            col_data = correlated_noise * std + mean

        col_data = np.clip(col_data, min_val, max_val)
        synthetic_df[col_name] = col_data.astype('float32')

    # --- 2. Generate Categorical and Binary Features ---
    print("Generating categorical and binary features...")
    all_other_features = categorical_features + binary_features
    for feature in all_other_features:
        col_name = feature['short_name']
        categories, stats = feature['params']
        synthetic_df[col_name] = create_categorical_distribution(categories, stats, n_samples)

    # --- 3. Finalize ---
    print("Combining fabricated features with merged data...")
    final_df = pd.concat([merged_df.reset_index(drop=True), synthetic_df], axis=1)

    output_path = Path(config['paths']['processed_data_directory']) / 'merged_data_fabricated.csv'
    output_path.parent.mkdir(parents=True, exist_ok=True)
    final_df.to_csv(output_path, index=False)

    print("✅ Fabrication successful!")
    return final_df