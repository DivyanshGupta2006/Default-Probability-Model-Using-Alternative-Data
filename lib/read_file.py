import pandas as pd
import os
from lib import config


def read_raw_data(filename):
    print(f"Reading file: {filename}")

    file_path = os.path.join(config.RAW_DATA_DIRECTORY, filename)

    if not os.path.exists(file_path):
        print(f"Error: File not found at path: {file_path}")
        return None

    df = pd.read_csv(file_path)
    print("Successfully read file!")
    return df


def read_processed_data(filename):
    print(f"Reading file: {filename}")

    file_path = os.path.join(config.PROCESSED_DATA_DIRECTORY, filename)

    if not os.path.exists(file_path):
        print(f"Error: File not found at path: {file_path}")
        return None

    df = pd.read_csv(file_path)
    print("Successfully read file!")
    return df
