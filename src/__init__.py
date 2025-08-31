# """
# Main source package for the Credit Risk Model project.
#
# This package exposes the key functionalities from all sub-packages,
# including data processing, model training, prediction, and the web interface.
# """
#
# # --- From data_processing package ---
# from .data_processing import preprocess, fabricate_features
#
# # --- From model package ---
# from .model import train_model, make_prediction
#
# # --- From interface package ---
# from .interface import app
#
# # --- From utils package ---
# from .utils import perform_eda, read_raw_data
#
# # --- Define the public API for the 'src' package ---
# __all__ = [
#     # data_processing
#     "preprocess",
#     "fabricate_features",
#
#     # # model
#     # "train_model",
#     # "make_prediction",
#
#     # interface
#     "app",
#
#     # utils
#     "perform_eda",
#     "read_raw_data"
# ]
# """
# Main source package for the Credit Risk Model project.
#
# This package exposes the key functionalities from all sub-packages,
# including data processing, model training, prediction, and the web interface.
# """
#
# # --- From data_processing package ---
# from .data_processing import preprocess, fabricate_features
#
# # --- From model package ---
# from .model import train_model, make_prediction
#
# # --- From interface package ---
# # from .interface import app
# #
# # --- From utils package ---
# from .utils import perform_eda, read_raw_data
#
# # --- Define the public API for the 'src' package ---
# _all_ = [
#     # data_processing
#     "preprocess_data",
#     "fabricate_features",
#
#     # # model
#     # "train_model",
#     # "make_prediction",
#
#     # interface
#     "app",
#
#     # utils
#     "perform_eda",
#     "read_raw_data"
# ]