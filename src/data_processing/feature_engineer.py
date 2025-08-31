import pandas as pd
import numpy as np
from pathlib import Path
from src.utils import get_config

config = get_config.read_yaml_from_package()


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Engineers new features based on existing and fabricated data to create more
    meaningful predictors for the credit risk model.

    Args:
        df (pd.DataFrame): The input DataFrame, ideally after merging and fabrication.

    Returns:
        pd.DataFrame: The DataFrame with new, engineered features.
    """
    print("🚀 Starting feature engineering...")

    engineered_df = df.copy()

    # --- 1. Financial Stability & Behavior Ratios ---
    # These features mimic traditional credit scoring ratios using alternative data.

    # Ratio of cash drawings to total drawings. A high ratio might indicate liquidity issues.
    engineered_df['CASH_DRAWING_RATIO'] = (engineered_df['AMT_DRAWINGS_ATM_CURRENT_mean'] /
                                           engineered_df['AMT_DRAWINGS_CURRENT_mean']).fillna(0)

    # A proxy for disposable income vs. digital spending.
    engineered_df['UTILITY_VS_SPENDING_RATIO'] = (engineered_df['UTILITY_BIL'] /
                                                  engineered_df['AMT_DRAWINGS_POS_CURRENT_mean']).fillna(0)

    # Average transaction amount for point-of-sale drawings.
    engineered_df['AVG_POS_TRANSACTION_VALUE'] = (engineered_df['AMT_DRAWINGS_POS_CURRENT_mean'] /
                                                  engineered_df['CNT_DRAWINGS_POS_CURRENT_mean']).fillna(0)

    # --- 2. Digital Footprint & Engagement Score ---
    # Combines digital activity features into a single score.

    # Normalize features before combining them
    rev_apps_norm = (engineered_df['REV_FRM_CNSMR_APPS'] - engineered_df['REV_FRM_CNSMR_APPS'].min()) / \
                    (engineered_df['REV_FRM_CNSMR_APPS'].max() - engineered_df['REV_FRM_CNSMR_APPS'].min())

    smart_card_norm = (engineered_df['NO_OF_SMRT_CARD'] - engineered_df['NO_OF_SMRT_CARD'].min()) / \
                      (engineered_df['NO_OF_SMRT_CARD'].max() - engineered_df['NO_OF_SMRT_CARD'].min())

    engineered_df['DIGITAL_ADOPTION_SCORE'] = rev_apps_norm + smart_card_norm + engineered_df['LINKEDIN_DATA']

    # --- 3. Risk Interaction Features ---
    # These features capture how regional risk interacts with financial behavior.

    # Interaction between client's region rating and their recharge frequency.
    engineered_df['REGION_RISK_X_RECHARGE'] = engineered_df['REGION_RATING_CLIENT_mean'] * engineered_df['RCHRG_FRQ']

    # Interaction between regional risk and GST filing defaults.
    engineered_df['REGION_RISK_X_GST_DEFAULT'] = engineered_df['REGION_RATING_CLIENT_mean'] * engineered_df[
        'GST_FIL_DEF']

    # --- 4. Behavioral Consistency Features ---
    # These features check for consistency in a user's registered locations.

    engineered_df['LOCATION_INCONSISTENCY'] = (engineered_df['REG_REGION_NOT_LIVE_REGION_mean'] +
                                               engineered_df['REG_REGION_NOT_WORK_REGION_mean'] +
                                               engineered_df['LIVE_REGION_NOT_WORK_REGION_mean'])

    # Replace infinite values that may have been created from division by zero
    engineered_df.replace([np.inf, -np.inf], 0, inplace=True)

    print("✅ Feature engineering successful!")

    # Save the engineered data
    output_path = Path(config['paths']['processed_data_directory']) / 'merged_data_engineered.csv'
    engineered_df.to_csv(output_path, index=False)

    return engineered_df