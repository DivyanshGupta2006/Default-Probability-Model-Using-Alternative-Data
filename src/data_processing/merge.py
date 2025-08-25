import os
import pandas as pd
from pathlib import Path
import yaml
from pathlib import Path

from src.utils import read_file

current_file_path = Path(__file__)
root_dir = current_file_path.parent.parent.parent
config_path = root_dir / "config.yaml"

with open(config_path, 'r') as file:
    config = yaml.safe_load(file)

def merge_data():
    print("Reading raw data...")

    merged_df = pd.DataFrame()

    for filename in os.listdir(config['paths']['raw_data_directory']):
        if not filename in config['files']['junk_files']:
            data_point = read_file.read_raw_data(filename)
            data_point = data_point[[col for col in data_point.columns if col in config['features']['cols_to_use']]]
            if merged_df.empty:
                merged_df = data_point
            else:
                merged_df = pd.merge(merged_df, data_point, how="outer", on=config['data']['id'])



    return merged_df