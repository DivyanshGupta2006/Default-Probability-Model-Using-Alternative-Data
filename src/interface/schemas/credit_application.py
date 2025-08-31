from pydantic import BaseModel, Field
from typing import Optional

class CreditApplication(BaseModel):
    # --- New User Identification Fields ---
    # These fields will be captured from the form and stored in the 'users' table.
    # We use Field(..., example='...') to provide good examples in the API docs.
    user_id: str = Field(..., example="USR101_Mark_Zane")
    full_name: str = Field(..., example="Mark Zane")
    email: Optional[str] = Field(None, example="mark.zane@example.com")
    phone: Optional[str] = Field(None, example="+1-555-123-4567")

    # --- Existing Feature Fields ---
    # These are the same as before.

    # Categorical Features
    NAME_EDUCATION_TYPE: Optional[str] = "Higher education"
    NAME_SELLER_INDUSTRY: Optional[str] = "Consumer electronics"
    TRUECALR_FLAG: Optional[str] = "Blue"

    # Numerical Features
    REGION_RATING_CLIENT: Optional[int] = 2
    REG_REGION_NOT_LIVE_REGION: Optional[int] = 0
    REG_REGION_NOT_WORK_REGION: Optional[int] = 0
    LIVE_REGION_NOT_WORK_REGION: Optional[int] = 0
    AMT_DRAWINGS_ATM_CURRENT: Optional[float] = 5000.0
    AMT_DRAWINGS_CURRENT: Optional[float] = 7500.0
    AMT_DRAWINGS_OTHER_CURRENT: Optional[float] = 0.0
    AMT_DRAWINGS_POS_CURRENT: Optional[float] = 2500.0
    CNT_DRAWINGS_ATM_CURRENT: Optional[float] = 2.0
    CNT_DRAWINGS_CURRENT: Optional[float] = 10.0
    CNT_DRAWINGS_OTHER_CURRENT: Optional[float] = 0.0
    CNT_DRAWINGS_POS_CURRENT: Optional[float] = 8.0
    SELLERPLACE_AREA: Optional[int] = 500
    RCHRG_FRQ: Optional[float] = 2.0
    TRD_ACC: Optional[float] = 1.0
    OFC_DOC_EXP: Optional[int] = 5
    GST_FIL_DEF: Optional[int] = 0
    SIM_CARD_FAIL: Optional[int] = 0
    ECOM_SHOP_RETURN: Optional[int] = 1
    UTILITY_BIL: Optional[float] = 9500.0
    REG_VEH_CHALLAN: Optional[int] = 0
    LINKEDIN_DATA: Optional[int] = 1
    REV_FRM_UBER_RAPIDO: Optional[float] = 0.0
    NO_OF_SMRT_CARD: Optional[int] = 2
    NO_TYPE_OF_ACC: Optional[int] = 3

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "USR101_Mark_Zane",
                "full_name": "Mark Zane",
                "email": "mark.zane@example.com",
                "phone": "+1-555-123-4567",
                "NAME_EDUCATION_TYPE": "Higher education",
                "REGION_RATING_CLIENT": 2,
                "AMT_DRAWINGS_CURRENT": 15000.0,
                "UTILITY_BIL": 12000.0,
            }
        }
