from lib import config, download_data, read_file

download_data.download_and_unzip_kaggle_dataset()

sample = read_file.read_raw_data("bureau.csv")

print(sample)
