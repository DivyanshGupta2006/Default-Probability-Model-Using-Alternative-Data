import os
import yaml
from pathlib import Path

from src.data_processing import download_data, merge

download_data.download_and_unzip_kaggle_dataset()

merged_df = merge.merge_data()

current_file_path = Path(__file__)
root_dir = current_file_path.parent.parent
config_path = root_dir / "config.yaml"

with open(config_path, 'r') as file:
    config = yaml.safe_load(file)

data_dir = config['paths']['processed_data_directory']

if not os.path.exists(data_dir):
    print(f"Creating directory: {data_dir}")
    os.makedirs(data_dir)
else:
    print(f"Directory already exists: {data_dir}")

merged_df.to_csv(f'{config['paths']['processed_data_directory']}/merged_data_pre_existing.csv', index=False)
print("Data merging successful!")