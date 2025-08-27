import yaml
from pathlib import Path

from src.data_processing import download_data, merge, fabricate, preprocess

current_file_path = Path(__file__)
root_dir = current_file_path.parent.parent
config_path = root_dir / "config.yaml"

with open(config_path, 'r') as file:
    config = yaml.safe_load(file)

download_data.download_and_unzip_kaggle_dataset()

merged_df = merge.merge_data()

print("Data merging successful!")

fabricated_merged_df = fabricate.fabricate_features(merged_df)

print("Fabrication successful!")

clean_df = preprocess.clean(fabricated_merged_df)

print("Cleaning successful!")