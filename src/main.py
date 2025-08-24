import os
import pandas as pd

from src.utils import config, read_file
from src.data_processing import download_data

download_data.download_and_unzip_kaggle_dataset()

merged_df = pd.DataFrame()

for filename in os.listdir(config.RAW_DATA_DIRECTORY):
    if not filename in config.JUNK_FILES:
        data_point = read_file.read_raw_data(filename)
        data_point = data_point[[col for col in data_point.columns if col in config.COLS]]
        if merged_df.empty:
            merged_df = data_point
        else:
            merged_df = pd.merge(merged_df, data_point, how="left", on=config.ID)

data_dir = config.PROCESSED_DATA_DIRECTORY

if not os.path.exists(data_dir):
    print(f"Creating directory: {data_dir}")
    os.makedirs(data_dir)
else:
    print(f"Directory already exists: {data_dir}")

merged_df.to_csv(f'{config.PROCESSED_DATA_DIRECTORY}/merged_data.csv', index=False)
print("Data merging successful!")