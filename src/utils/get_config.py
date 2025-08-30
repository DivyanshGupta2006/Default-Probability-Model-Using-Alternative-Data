import yaml
from pathlib import Path

def read_yaml_from_package():
    current_file_path = Path(__file__)
    root_dir = current_file_path.parent.parent.parent
    config_path = root_dir / "config.yaml"
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
    return config

def read_yaml_from_main():
    current_file_path = Path(__file__)
    root_dir = current_file_path.parent.parent.parent
    config_path = root_dir / "config.yaml"
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
    return config