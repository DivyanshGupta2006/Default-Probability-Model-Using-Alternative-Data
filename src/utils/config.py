import os

# path related variables
RAW_DATA_DIRECTORY = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'raw_data'))
PROCESSED_DATA_DIRECTORY = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'processed_data'))

# data related variables
ID = "SK_ID_CURR"
JUNK_FILES = [
    'HomeCredit_columns_description.csv', 'application_test.csv', 'bureau.csv',
    'bureau_balance.csv', 'installments_payments.csv', 'POS_CASH_balance.csv', 'sample_submission.csv'
]
COLS = [
    'NAME_EDUCATION_TYPE', 'REGION_RATING_CLIENT', 'REG_REGION_NOT_LIVE_REGION', 'REG_REGION_NOT_WORK_REGION',
    'LIVE_REGION_NOT_WORK_REGION', 'AMT_DRAWINGS_ATM_CURRENT', 'AMT_DRAWINGS_CURRENT', 'AMT_DRAWINGS_OTHER_CURRENT',
    'AMT_DRAWINGS_POS_CURRENT', 'CNT_DRAWINGS_ATM_CURRENT', 'CNT_DRAWINGS_CURRENT', 'CNT_DRAWINGS_OTHER_CURRENT',
    'CNT_DRAWINGS_POS_CURRENT', 'SELLERPLACE_AREA', 'NAME_SELLER_INDUSTRY', 'RCHRG_FRQ', 'TRD_ACC', 'OFC_DOC_EXP',
    'GST_FIL_DEF', 'SIM_CARD_FAIL', 'TRUECALR_FLAG', 'ECOM_SHOP_RETURN', 'UTILITY_BIL', 'REG_VEH_CHALLAN', 'LINKEDIN_DATA',
    'REV_FRM_UBER/RAPIDO', 'NO_OF_SMRT_CARD', 'NO_TYPE_OF_ACC', 'SK_ID_CURR', 'TARGET'
]
