# In: src/interface/schemas/prediction_result.py

from pydantic import BaseModel
from typing import Dict

class PredictionResult(BaseModel):
    base_value: float
    prediction_probability: float
    feature_impacts: Dict[str, float]