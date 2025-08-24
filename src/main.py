import os
import pandas as pd

from src.utils import config, read_file
from src.data_processing import download_data, merge

download_data.download_and_unzip_kaggle_dataset()

merged_df = merge.merge_data()

data_dir = config.PROCESSED_DATA_DIRECTORY

if not os.path.exists(data_dir):
    print(f"Creating directory: {data_dir}")
    os.makedirs(data_dir)
else:
    print(f"Directory already exists: {data_dir}")

merged_df.to_csv(f'{config.PROCESSED_DATA_DIRECTORY}/merged_data_pre_existing.csv', index=False)
print("Data merging successful!")