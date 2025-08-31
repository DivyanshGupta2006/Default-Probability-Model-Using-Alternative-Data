from pydantic import BaseModel
from typing import Optional

class CreditApplication(BaseModel):
    # Numerical Features from config.yaml
    REGION_RATING_CLIENT_min: Optional[float] = None
    REGION_RATING_CLIENT_max: Optional[float] = None
    REGION_RATING_CLIENT_mean: Optional[float] = None
    REGION_RATING_CLIENT_sum: Optional[float] = None
    REGION_RATING_CLIENT_std: Optional[float] = None
    REG_REGION_NOT_LIVE_REGION_min: Optional[float] = None
    REG_REGION_NOT_LIVE_REGION_max: Optional[float] = None
    REG_REGION_NOT_LIVE_REGION_mean: Optional[float] = None
    REG_REGION_NOT_LIVE_REGION_sum: Optional[float] = None
    REG_REGION_NOT_LIVE_REGION_std: Optional[float] = None
    REG_REGION_NOT_WORK_REGION_min: Optional[float] = None
    REG_REGION_NOT_WORK_REGION_max: Optional[float] = None
    REG_REGION_NOT_WORK_REGION_mean: Optional[float] = None
    REG_REGION_NOT_WORK_REGION_sum: Optional[float] = None
    REG_REGION_NOT_WORK_REGION_std: Optional[float] = None
    LIVE_REGION_NOT_WORK_REGION_min: Optional[float] = None
    LIVE_REGION_NOT_WORK_REGION_max: Optional[float] = None
    LIVE_REGION_NOT_WORK_REGION_mean: Optional[float] = None
    LIVE_REGION_NOT_WORK_REGION_sum: Optional[float] = None
    LIVE_REGION_NOT_WORK_REGION_std: Optional[float] = None
    AMT_DRAWINGS_ATM_CURRENT_min: Optional[float] = None
    AMT_DRAWINGS_ATM_CURRENT_max: Optional[float] = None
    AMT_DRAWINGS_ATM_CURRENT_mean: Optional[float] = None
    AMT_DRAWINGS_ATM_CURRENT_sum: Optional[float] = None
    AMT_DRAWINGS_ATM_CURRENT_std: Optional[float] = None
    AMT_DRAWINGS_CURRENT_min: Optional[float] = None
    AMT_DRAWINGS_CURRENT_max: Optional[float] = None
    AMT_DRAWINGS_CURRENT_mean: Optional[float] = None
    AMT_DRAWINGS_CURRENT_sum: Optional[float] = None
    AMT_DRAWINGS_CURRENT_std: Optional[float] = None
    AMT_DRAWINGS_OTHER_CURRENT_min: Optional[float] = None
    AMT_DRAWINGS_OTHER_CURRENT_max: Optional[float] = None
    AMT_DRAWINGS_OTHER_CURRENT_mean: Optional[float] = None
    AMT_DRAWINGS_OTHER_CURRENT_sum: Optional[float] = None
    AMT_DRAWINGS_OTHER_CURRENT_std: Optional[float] = None
    AMT_DRAWINGS_POS_CURRENT_min: Optional[float] = None
    AMT_DRAWINGS_POS_CURRENT_max: Optional[float] = None
    AMT_DRAWINGS_POS_CURRENT_mean: Optional[float] = None
    AMT_DRAWINGS_POS_CURRENT_sum: Optional[float] = None
    AMT_DRAWINGS_POS_CURRENT_std: Optional[float] = None
    CNT_DRAWINGS_ATM_CURRENT_min: Optional[float] = None
    CNT_DRAWINGS_ATM_CURRENT_max: Optional[float] = None
    CNT_DRAWINGS_ATM_CURRENT_mean: Optional[float] = None
    CNT_DRAWINGS_ATM_CURRENT_sum: Optional[float] = None
    CNT_DRAWINGS_ATM_CURRENT_std: Optional[float] = None
    CNT_DRAWINGS_CURRENT_min: Optional[float] = None
    CNT_DRAWINGS_CURRENT_max: Optional[float] = None
    CNT_DRAWINGS_CURRENT_mean: Optional[float] = None
    CNT_DRAWINGS_CURRENT_sum: Optional[float] = None
    CNT_DRAWINGS_CURRENT_std: Optional[float] = None
    CNT_DRAWINGS_OTHER_CURRENT_min: Optional[float] = None
    CNT_DRAWINGS_OTHER_CURRENT_max: Optional[float] = None
    CNT_DRAWINGS_OTHER_CURRENT_mean: Optional[float] = None
    CNT_DRAWINGS_OTHER_CURRENT_sum: Optional[float] = None
    CNT_DRAWINGS_OTHER_CURRENT_std: Optional[float] = None
    CNT_DRAWINGS_POS_CURRENT_min: Optional[float] = None
    CNT_DRAWINGS_POS_CURRENT_max: Optional[float] = None
    CNT_DRAWINGS_POS_CURRENT_mean: Optional[float] = None
    CNT_DRAWINGS_POS_CURRENT_sum: Optional[float] = None
    CNT_DRAWINGS_POS_CURRENT_std: Optional[float] = None
    SELLERPLACE_AREA_min: Optional[float] = None
    SELLERPLACE_AREA_max: Optional[float] = None
    SELLERPLACE_AREA_mean: Optional[float] = None
    SELLERPLACE_AREA_sum: Optional[float] = None
    SELLERPLACE_AREA_std: Optional[float] = None
    NAME_EDUCATION_TYPE_count: Optional[float] = None
    NAME_EDUCATION_TYPE_nunique: Optional[float] = None
    NAME_SELLER_INDUSTRY_count: Optional[float] = None
    NAME_SELLER_INDUSTRY_nunique: Optional[float] = None
    RCHRG_FRQ: Optional[float] = None
    TRD_ACC: Optional[float] = None
    REV_FRM_CNSMR_APPS: Optional[float] = None
    NO_OF_SMRT_CARD: Optional[float] = None
    NO_TYPE_OF_ACC: Optional[float] = None
    OFC_DOC_EXP: Optional[float] = None
    GST_FIL_DEF: Optional[float] = None
    REG_VEH_CHALLAN: Optional[float] = None
    SIM_CARD_FAIL: Optional[float] = None
    ECOM_SHOP_RETURN: Optional[float] = None
    UTILITY_BIL: Optional[float] = None
    LINKEDIN_DATA: Optional[float] = None

    # Categorical Features from config.yaml
    NAME_EDUCATION_TYPE_mode: Optional[str] = None
    NAME_SELLER_INDUSTRY_mode: Optional[str] = None
    TRUECALR_FLAG: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "REGION_RATING_CLIENT_min": 2,
                "AMT_DRAWINGS_CURRENT_mean": 7500.0,
                "UTILITY_BIL": 9500.0,
                "NAME_EDUCATION_TYPE_mode": "Higher education",
                "RCHRG_FRQ": 2.0,
                "NO_OF_SMRT_CARD": 2,
                # Users only need to provide the fields they know
            }
        }