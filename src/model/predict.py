from src.data_processing import preprocess
from src.utils import read_file, get_config

config = get_config.read_yaml_from_package()

def make_prediction(input_df):
    input_df = preprocess.clean(input_df, use_saved=True)
    model = read_file.read_model_data(config['model'])
    preds = model.predict_proba(input_df)
    return preds