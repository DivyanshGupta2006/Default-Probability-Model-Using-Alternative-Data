# In: src/interface/schemas/credit_application.py

from pydantic import BaseModel

# This schema defines the structure for a new credit application.
# Add the most important features you expect from the user input form.
class CreditApplication(BaseModel):
    REGION_RATING_CLIENT_min: int
    AMT_DRAWINGS_ATM_CURRENT_mean: float
    AMT_DRAWINGS_CURRENT_mean: float
    AMT_DRAWINGS_POS_CURRENT_mean: float
    CNT_DRAWINGS_CURRENT_mean: float
    SELLERPLACE_AREA_mean: int
    RCHRG_FRQ: float
    TRD_ACC: float
    NO_OF_SMRT_CARD: int
    NO_TYPE_OF_ACC: int
    OFC_DOC_EXP: int
    GST_FIL_DEF: int
    UTILITY_BIL: float
    NAME_EDUCATION_TYPE_mode: str = "Secondary / secondary special"
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