from src.data_processing import download_data, merge, fabricate, preprocess, split, feature_engineer
from src.utils import get_config, read_file

config = get_config.read_yaml_from_main()

print("Successfully read metadata!")

download_data.download_and_unzip_kaggle_dataset()

print("Data downloading successful!")

merged_df = merge.merge_data()

print("Data merging successful!")

fabricated_merged_df = fabricate.fabricate_features(merged_df)

print("Fabrication successful!")

engineered_df = feature_engineer.engineer_features(fabricated_merged_df)
print("Feature engineering successful!")
# ---------------------

# Pass the engineered dataframe to the split function
train_df, val_df, test_df = split.split_data(engineered_df)
print("Splitting successful!")


train_df = preprocess.clean(train_df, name="clean_train_data.csv")
val_df = preprocess.clean(val_df, name="clean_val_data.csv", use_saved=True)
test_df = preprocess.clean(test_df, name="clean_test_data.csv", use_saved=True)

print("Cleaning successful!")