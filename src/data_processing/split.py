from sklearn.model_selection import train_test_split

from src.utils import get_config

config = get_config.read_yaml_from_package()

def split_data(df):

    target_col = config['data']['target']
    train_df, temp_df = train_test_split(
        df, test_size=0.3, random_state=42, stratify=df[target_col]
    )

    # Split the temporary set into validation (15%) and test (15%)
    val_df, test_df = train_test_split(
        temp_df, test_size=0.5, random_state=42, stratify=temp_df[target_col]
    )

    output_path = config['paths']['processed_data_directory']
    print(f"Train set shape: {train_df.shape}")
    print(f"Validation set shape: {val_df.shape}")
    print(f"Test set shape: {test_df.shape}")

    output_dir = config['paths']['processed_data_directory']
    train_df.to_csv(output_dir + "/train_data.csv", index=False)
    val_df.to_csv(output_dir + "/validation_data.csv", index=False)
    test_df.to_csv(output_dir + "/test_data.csv", index=False)

    return train_df, val_df, test_df