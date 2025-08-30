import pandas as pd
import os
import yaml
from pathlib import Path
import joblib

current_file_path = Path(__file__)
root_dir = current_file_path.parent.parent.parent
config_path = root_dir / "config.yaml"

with open(config_path, 'r') as file:
    config = yaml.safe_load(file)

def read_raw_data(filename):
    print(f"Reading file: {filename}")

    file_path = os.path.join(config['paths']['raw_data_directory'], filename)

    if not os.path.exists(file_path):
        print(f"Error: File not found at path: {file_path}")
        return None

    df = pd.read_csv(file_path)
    print("Successfully read file!")
    return df


def read_processed_data(filename):
    print(f"Reading file: {filename}")

    file_path = os.path.join(config['paths']['processed_data_directory'], filename)

    if not os.path.exists(file_path):
        print(f"Error: File not found at path: {file_path}")
        return None

    df = pd.read_csv(file_path)
    print("Successfully read file!")
    return df

def read_model_data(filename):
    print(f"Reading file: {filename}")

    file_path = os.path.join(config['paths']['model_data_directory'], filename)

    if not os.path.exists(file_path):
        print(f"Error: File not found at path: {file_path}")
        return None

    data = joblib.load(file_path)
    print("Successfully read file!")
    return data
