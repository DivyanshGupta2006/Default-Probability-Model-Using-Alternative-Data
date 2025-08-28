"""
Data processing package for the credit risk model.
This package handles data downloading, fabrication, and preprocessing.
"""

from .fabricate import fabricate_features
from .preprocess import clean
from .merge import merge_data
from .download_data import download_and_unzip_kaggle_dataset

_all_ = [
    "fabricate_features",
    "preprocess_data",
    "merge_data",
    "download_data"
]