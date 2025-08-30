import os
import pandas as pd
from pathlib import Path
import yaml
from pathlib import Path
from src.utils import read_file

from src.data_processing import preprocess
from src.utils import read_file

current_file_path = Path(__file__)
root_dir = current_file_path.parent.parent.parent
config_path = root_dir / "config.yaml"

with open(config_path, 'r') as file:
    config = yaml.safe_load(file)

def merge_data():
    print("Starting data merge...")

    merged_df = pd.DataFrame()

    for filename in os.listdir(config['paths']['raw_data_directory']):
        if not filename in config['files']['junk_files']:
            data_point = read_file.read_raw_data(filename)
            data_point = data_point[[col for col in data_point.columns if col in config['data']['cols_to_use']]]
            if merged_df.empty:
                merged_df = data_point
            else:
                merged_df = pd.merge(merged_df, data_point, how="left", on=config['data']['id'])

    aggregations = {}

    for col in config['data']['numerical_pre_existing']:
        aggregations[col] = ['min', 'max', 'mean', 'sum', 'std']

    for col in config['data']['categorical_pre_existing']:
        aggregations[col] = ['count', 'nunique', ('mode', lambda x: x.mode().iloc[0] if not x.mode().empty else None)]

    # 3. Group by ID and Aggregate
    agg_df = merged_df.groupby('SK_ID_CURR').agg(aggregations)

    # 4. Flatten the Multi-level Column Names
    agg_df.columns = ['_'.join(col).strip() for col in agg_df.columns.values]

    # 5. Reset Index to make SK_ID_CURR a column again
    agg_df = agg_df.reset_index()

    # add back the target column
    app_train_df = read_file.read_raw_data("application_train.csv")
    target_df = app_train_df[['SK_ID_CURR', 'TARGET']]

    agg_df_with_target = pd.merge(agg_df, target_df, on='SK_ID_CURR', how='left')

    data_dir = config['paths']['processed_data_directory']

    if not os.path.exists(data_dir):
        print(f"Creating directory: {data_dir}")
        os.makedirs(data_dir)
    else:
        print(f"Directory already exists: {data_dir}")

    agg_df_with_target.to_csv(f'{config['paths']['processed_data_directory']}/merged_data_pre_existing.csv', index=False)

    return agg_df_with_target