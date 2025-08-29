import numpy as np
import pandas as pd
import yaml
from pathlib import Path


current_file_path = Path(__file__)
root_dir = current_file_path.parent.parent.parent
config_path = root_dir / "config.yaml"

with open(config_path, 'r') as file:
    config = yaml.safe_load(file)

def train_model():
    return 0
