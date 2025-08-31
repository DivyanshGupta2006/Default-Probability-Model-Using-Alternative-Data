from pydantic import BaseModel
from typing import Optional  # <-- Import Optional


class CreditApplication(BaseModel):
    # These are in your form, so they remain required
    REGION_RATING_CLIENT_min: int
    AMT_DRAWINGS_CURRENT_mean: float
    UTILITY_BIL: float
    NAME_EDUCATION_TYPE_mode: str = "Secondary / secondary special"

    # --- MAKE THESE FIELDS OPTIONAL ---
    # These are not in your simple form, so we provide a default of None
    AMT_DRAWINGS_ATM_CURRENT_mean: Optional[float] = None
    AMT_DRAWINGS_POS_CURRENT_mean: Optional[float] = None
    CNT_DRAWINGS_CURRENT_mean: Optional[float] = None
    SELLERPLACE_AREA_mean: Optional[int] = None
    RCHRG_FRQ: Optional[float] = None
    TRD_ACC: Optional[float] = None
    NO_OF_SMRT_CARD: Optional[int] = None
    NO_TYPE_OF_ACC: Optional[int] = None
    OFC_DOC_EXP: Optional[int] = None
    GST_FIL_DEF: Optional[int] = None
    NAME_SELLER_INDUSTRY_mode: str = "XNA"
    TRUECALR_FLAG: str = "Blue"
    # Example of how to add a default value for the model
    class Config:
        schema_extra = {
            "example": {
                "REGION_RATING_CLIENT_min": 2,
                "AMT_DRAWINGS_ATM_CURRENT_mean": 5000.0,
                "AMT_DRAWINGS_CURRENT_mean": 7500.0,
                "AMT_DRAWINGS_POS_CURRENT_mean": 2500.0,
                "CNT_DRAWINGS_CURRENT_mean": 10.0,
                "SELLERPLACE_AREA_mean": 500,
                "RCHRG_FRQ": 2.0,
                "TRD_ACC": 1.0,
                "NO_OF_SMRT_CARD": 2,
                "NO_TYPE_OF_ACC": 3,
                "OFC_DOC_EXP": 5,
                "GST_FIL_DEF": 0,
                "UTILITY_BIL": 9500.0,
                "NAME_EDUCATION_TYPE_mode": "Higher education",
                "NAME_SELLER_INDUSTRY_mode": "Consumer electronics",
                "TRUECALR_FLAG": "Blue"
            }
        }