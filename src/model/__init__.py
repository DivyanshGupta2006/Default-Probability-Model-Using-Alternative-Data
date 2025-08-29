"""
Model package for training and prediction.
"""

from .train import train_model
from .predict import make_prediction
from .model import Model # If you have a model class

__all__ = [
    "train_model",
    "make_prediction",
    "Model"
]