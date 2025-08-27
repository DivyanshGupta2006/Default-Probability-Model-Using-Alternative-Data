from faker import Faker
import numpy as np
import pandas as pd
import random as rd
from scipy.stats import truncnorm, norm
from numpy.linalg import eigh

from scipy.linalg import block_diag

def fabricate_features(merged_df, rng_seed=42):
    rng = np.random.default_rng(seed=rng_seed)  # reproducibility

    # --- Statistics definition ---
    stats_list = [
        (1.426, 0.57, 0, 20, "continuous"),       # RCHRG_FRQ
        (1.27, 0.9, 0, 10, "continuous"),         # TRD_ACC
        (3, 2, 0, 12, "continuous"),              # OFC_DOC_EXP
        (0.39, 0.65, 0, 3, "continuous"),         # GST_FIL_DEF
        (1.2, 0.8, 0, 60, "continuous"),          # SIM_CARD_FAIL
        (0.35, 0.7, 0, 25, "continuous"),         # ECOM_SHOP_RETURN
        (9500, 6500, 2500, 35000, "continuous"),  # UTILITY_BIL
        (0.12, 0.5, 0, 100, "continuous"),        # REG_VEH_CHALLAN
        ((0, 1), (0.5, 0.5), "binary"),           # LINKEDIN_DATA
        (500, 200, 50, 2000, "continuous"),       # REV_FRM_CNSMR_APPS
        (2.6, 0.9, 0, 6, "continuous"),           # NO_OF_SMRT_CARD
        (2.05, 1.5, 0, 8, "continuous"),          # NO_TYPE_OF_ACC
        (("Strongly Negative","Negative","Neutral","Positive","Strongly Positive"),
         (20, 32, 32, 12, 4), "categorical")      # SENTI_OF_SOCIAL_M
    ]

    numeric_columns = [
        "Recharge Frequency (per month)",              # RCHRG_FRQ
        "Trading Accounts",                            # TRD_ACC
        "Official Document Expiry (per year)",         # OFC_DOC_EXP
        "Default in GST filing (per quarter)",         # GST_FIL_DEF
        "SIM Card Failures",                           # SIM_CARD_FAIL
        "Truecaller Flag (Category)",                  # TRUECALR_FLAG
        "E-commerce Shopping Returns (per month)",     # ECOM_SHOP_RETURN
        "Utility Bills (per month)",                   # UTILITY_BIL
        "Registered Vehicle Challans (per year)",      # REG_VEH_CHALLAN
        "LinkedIn Data (Presence)",                    # LINKEDIN_DATA
        "Revenue from Consumer Apps",                  # REV_FRM_CNSMR_APPS
        "Number of Smart Cards",                       # NO_OF_SMRT_CARD
        "Number of Account Types",                     # NO_TYPE_OF_ACC
        "Sentiment of Social Media",                   # SENTI_OF_SOCIAL_M
    ]

    # --- Define correlation blocks ---
    corr_financial = np.array([
        [1.0, 0.42, 0.35, 0.38, 0.30],
        [0.42, 1.0, 0.33, 0.36, 0.32],
        [0.35, 0.33, 1.0, 0.40, 0.28],
        [0.38, 0.36, 0.40, 1.0, 0.34],
        [0.30, 0.32, 0.28, 0.34, 1.0]
    ])

    corr_compliance = np.array([
        [1.0, 0.40, 0.35],
        [0.40, 1.0, 0.38],
        [0.35, 0.38, 1.0]
    ])

    corr_digital = np.array([
        [1.0, 0.45, 0.33, 0.28],
        [0.45, 1.0, 0.30, 0.26],
        [0.33, 0.30, 1.0, 0.32],
        [0.28, 0.26, 0.32, 1.0]
    ])

    corr_behavioral = np.array([
        [1.0, 0.36],
        [0.36, 1.0]
    ])

    correlation_matrix = block_diag(
        corr_financial,
        corr_compliance,
        corr_digital,
        corr_behavioral
    )

    # --- Generate correlated data ---
    n = len(merged_df)
    L = np.linalg.cholesky(correlation_matrix)
    uncorrelated = rng.normal(size=(n, correlation_matrix.shape[0]))
    correlated = uncorrelated @ L.T

    scaled_data = []
    valid_numeric_columns = []

    for i, stats in enumerate(stats_list):
        if isinstance(stats[0], tuple):  # skip categorical
            continue

        mean, std, min_val, max_val, _ = stats
        col = correlated[:, i]
        col = (col - np.mean(col)) / np.std(col)  # standardize
        col = col * std + mean
        col = np.clip(col, min_val, max_val)

        scaled_data.append(col.astype("float32"))
        valid_numeric_columns.append(numeric_columns[i])

    synthetic_df = pd.DataFrame(
        np.column_stack(scaled_data),
        columns=valid_numeric_columns
    )

    # --- Add to merged_df ---
    merged_df = pd.concat([merged_df.reset_index(drop=True), synthetic_df], axis=1)

    # Add categorical variables
    truecaller_categories = ('Red', 'Blue', 'Golden')
    truecaller_stats = (0.2, 0.75, 0.05)

    social_sentiments_categories = (
        'Strongly Negative', 'Negative', 'Neutral', 'Positive', 'Strongly Positive'
    )
    social_sentiments_stats = (20, 32, 32, 12, 4)

    merged_df['TrueCaller Flag'] = np.random.choice(
        truecaller_categories, size=len(merged_df), p=truecaller_stats
    )

    merged_df['Sentiment on Social Media'] = np.random.choice(
        social_sentiments_categories,
        size=len(merged_df),
        p=np.array(social_sentiments_stats) / np.sum(social_sentiments_stats)
    )

    return merged_df