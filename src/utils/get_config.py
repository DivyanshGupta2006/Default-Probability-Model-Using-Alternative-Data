import yaml
from pathlib import Path

def get_project_root() -> Path:
    # .resolve() makes the path absolute
    return Path(__file__).resolve().parent.parent.parent

def read_yaml() -> dict:
    config_path = get_project_root() / "config.yaml"
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
    return config

read_yaml_from_package = read_yaml
read_yaml_from_main = read_yaml