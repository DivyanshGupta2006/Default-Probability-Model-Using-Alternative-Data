from pydantic import BaseModel
from typing import Optional

class CreditApplication(BaseModel):
    # This schema includes all 27 of your final features.
    # All fields are optional to allow for flexible input from the form.

    # Categorical Features
    NAME_EDUCATION_TYPE: Optional[str] = "Secondary / secondary special"
    NAME_SELLER_INDUSTRY: Optional[str] = "XNA"
    TRUECALR_FLAG: Optional[str] = "Blue"

    # Numerical Features
    REGION_RATING_CLIENT: Optional[int] = 2
    REG_REGION_NOT_LIVE_REGION: Optional[int] = 0
    REG_REGION_NOT_WORK_REGION: Optional[int] = 0
    LIVE_REGION_NOT_WORK_REGION: Optional[int] = 0
    AMT_DRAWINGS_ATM_CURRENT: Optional[float] = 0.0
    AMT_DRAWINGS_CURRENT: Optional[float] = 0.0
    AMT_DRAWINGS_OTHER_CURRENT: Optional[float] = 0.0
    AMT_DRAWINGS_POS_CURRENT: Optional[float] = 0.0
    CNT_DRAWINGS_ATM_CURRENT: Optional[float] = 0.0
    CNT_DRAWINGS_CURRENT: Optional[float] = 0.0
    CNT_DRAWINGS_OTHER_CURRENT: Optional[float] = 0.0
    CNT_DRAWINGS_POS_CURRENT: Optional[float] = 0.0
    SELLERPLACE_AREA: Optional[int] = 500
    RCHRG_FRQ: Optional[float] = 1.0
    TRD_ACC: Optional[float] = 0.0
    OFC_DOC_EXP: Optional[int] = 0
    GST_FIL_DEF: Optional[int] = 0
    SIM_CARD_FAIL: Optional[int] = 0
    ECOM_SHOP_RETURN: Optional[int] = 0
    UTILITY_BIL: Optional[float] = 9500.0
    REG_VEH_CHALLAN: Optional[int] = 0
    LINKEDIN_DATA: Optional[int] = 0
    # NOTE: 'REV_FRM_UBER/RAPIDO' is not a valid Python variable name.
    # I have renamed it to REV_FRM_UBER_RAPIDO for compatibility.
    # Please ensure this matches the column name in your training data.
    REV_FRM_UBER_RAPIDO: Optional[float] = 0.0
    NO_OF_SMRT_CARD: Optional[int] = 1
    NO_TYPE_OF_ACC: Optional[int] = 1

    class Config:
        # Pydantic V2 uses 'json_schema_extra'
        json_schema_extra = {
            "example": {
                "NAME_EDUCATION_TYPE": "Higher education",
                "REGION_RATING_CLIENT": 2,
                "AMT_DRAWINGS_CURRENT": 15000.0,
                "UTILITY_BIL": 12000.0,
                "RCHRG_FRQ": 3.0,
                "TRD_ACC": 2.0,
                "NO_OF_SMRT_CARD": 3,
                "TRUECALR_FLAG": "Golden"
                # Add other key example values here
            }
        }