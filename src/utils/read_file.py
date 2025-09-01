import pandas as pd
import os
import joblib
from src.utils import get_config

# Load config using the new centralized function
config = get_config.read_yaml()
# Get the project root path
PROJECT_ROOT = get_config.get_project_root()

def read_raw_data(filename):
    print(f"Reading file: {filename}")
    # Construct the full, absolute path
    file_path = PROJECT_ROOT / config['paths']['raw_data_directory'] / filename
    if not os.path.exists(file_path):
        print(f"Error: File not found at path: {file_path}")
        return None
    df = pd.read_csv(file_path)
    print("Successfully read file!")
    return df

def read_processed_data(filename):
    print(f"Reading file: {filename}")
    # Construct the full, absolute path
    file_path = PROJECT_ROOT / config['paths']['processed_data_directory'] / filename
    if not os.path.exists(file_path):
        print(f"Error: File not found at path: {file_path}")
        return None
    df = pd.read_csv(file_path)
    print("Successfully read file!")
    return df

def read_model_data(filename):
    print(f"Reading file: {filename}")
    # Construct the full, absolute path
    file_path = PROJECT_ROOT / config['paths']['model_data_directory'] / filename
    if not os.path.exists(file_path):
        print(f"Error: File not found at path: {file_path}")
        return None
    data = joblib.load(file_path)
    print("Successfully read file!")
    return data