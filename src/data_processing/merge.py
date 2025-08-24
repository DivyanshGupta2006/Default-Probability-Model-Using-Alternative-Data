import os
import pandas as pd
from pathlib import Path

from src.utils import config, read_file

def merge_data():
    print("Reading raw data...")

    merged_df = pd.DataFrame()

    for filename in os.listdir(config.RAW_DATA_DIRECTORY):
        if not filename in config.JUNK_FILES:
            data_point = read_file.read_raw_data(filename)
            data_point = data_point[[col for col in data_point.columns if col in config.COLS]]
            if merged_df.empty:
                merged_df = data_point
            else:
                merged_df = pd.merge(merged_df, data_point, how="outer", on=config.ID)



    return merged_df