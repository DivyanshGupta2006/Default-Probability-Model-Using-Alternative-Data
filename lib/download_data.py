import os
import subprocess
import zipfile
import sys
from lib import config

data_dir = config.RAW_DATA_DIRECTORY

competition_name = "home-credit-default-risk"

def download_and_unzip_kaggle_dataset():
    print(f"--- Starting Kaggle Dataset Download for '{competition_name}' ---")
    if not os.path.exists(data_dir):
        print(f"Creating directory: {data_dir}")
        os.makedirs(data_dir)
    else:
        print(f"Directory already exists: {data_dir}")

    if os.listdir(data_dir):
        print("Data directory is not empty. Assuming dataset is already present.")
        print("--- Process Complete ---")
        return
    zip_file_path = os.path.join(data_dir, f"{competition_name}.zip")
    command = [
        "kaggle",
        "competitions",
        "download",
        "-c",
        competition_name,
        "-p",
        data_dir,
    ]
    try:
        result = subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        print(result.stdout)
    except FileNotFoundError:
        print("\nERROR: 'kaggle' command not found.")
        print("Please ensure the Kaggle library is installed ('pip install kaggle') and that its location is in your system's PATH.")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"\nERROR: Kaggle API call failed with exit code {e.returncode}.")
        print("Please check the following:")
        print("1. You have accepted the competition rules on the Kaggle website.")
        print("2. Your Kaggle API token (~/.kaggle/kaggle.json) is correctly set up.")
        print("\nKaggle API error message:")
        print(e.stderr)
        sys.exit(1)

    print(f"\nUnzipping {zip_file_path}...")
    try:
        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            zip_ref.extractall(data_dir)
        print("Unzipping complete.")
    except zipfile.BadZipFile:
        print(f"ERROR: Failed to unzip file. It may be corrupted.")
        sys.exit(1)

    print(f"Removing zip file: {zip_file_path}")
    os.remove(zip_file_path)

    print("Download successful!")