# Credit Risk Default Probability Model Using Alternative Data

This project addresses the challenge of credit scoring for underbanked populations by developing a machine learning model that leverages alternative data sources. Traditional credit models rely heavily on historical financial data, which is often unavailable for individuals in emerging markets. This solution builds a robust pipeline to process, augment, and model credit risk, preparing it for a real-world production environment.

The core of the project involves using the "Home Credit Default Risk" dataset as a base and programmatically fabricating realistic alternative data features (e.g., utility payments, digital footprint metrics). This allows the model to learn from a richer feature set, improving its predictive accuracy and fairness.

## ✨ Features

* **End-to-End ML Pipeline:** A complete, script-based workflow from data downloading to model evaluation.
* **Alternative Data Fabrication:** A sophisticated module to generate synthetic, correlated alternative data features to enhance the base dataset.
* **Modular Model Architecture:** Supports multiple model types (LightGBM, XGBoost, CatBoost, Logistic Regression) through a clean, object-oriented structure.
* **Stacking Ensemble:** Includes a stacking ensemble model that combines the predictive power of base learners with a meta-learner for improved performance.
* **Command-Line Interface:** Easy-to-use command-line arguments for training and testing models, promoting reproducibility.
* **Robust Data Splitting:** Implements a stratified train-validation-test split to ensure reliable model evaluation and prevent data leakage.

---

## 📂 Project Structure
├── data/
│   ├── raw_data/         # Raw data from Kaggle
│   └── processed_data/   # Processed train/validation/test sets
├── models/               # Saved model artifacts (.pkl)
├── notebooks/            # Jupyter notebooks for exploration
├── src/
│   ├── data_processing/  # Scripts for download, merge, fabricate, preprocess
│   ├── model/            # Model classes, training, and testing scripts
│   └── utils/            # Utility functions for analysis and reading files
├── config.yaml           # Configuration file for paths and parameters
└── requirements.txt      # Project dependencies
---

## 🚀 Getting Started

### Prerequisites

* Python 3.8+
* Kaggle API Key: You must have your `kaggle.json` file set up in your `~/.kaggle/` directory to download the data.

### Installation

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/divyanshgupta2006/default-probability-model-using-alternative-data.git](https://github.com/divyanshgupta2006/default-probability-model-using-alternative-data.git)
    cd default-probability-model-using-alternative-data
    ```

2.  **Create and activate a virtual environment (recommended):**
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`
    ```

3.  **Install the required dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

---

## ⚙️ Usage: End-to-End Workflow

Follow these steps in order to run the entire pipeline from data acquisition to model testing.

### Step 1: Run the Data Processing Pipeline

This single command will download the raw data from Kaggle, merge the different files, fabricate the alternative data features, perform cleaning and imputation, and finally split the data into `train.csv`, `validation.csv`, and `test.csv`.

```bash
python -m src.main
```
This will populate the data/raw_data and data/processed_data directories.

Step 2: Train a Model
Use the generic training script to train any of the available models. The script uses the validation set to report performance.

Train a LightGBM model:

```bash
python -m src.model.train --model lightgbm --path models/lgbm_model.pkl
```
Train an XGBoost model:

```bash
python -m src.model.train --model xgboost --path models/xgb_model.pkl
```
Train a Stacking Ensemble model:

```bash
python -m src.model.train --model ensemble --path models/ensemble_model.pkl
```
The trained model will be saved in the models/ directory.

Step 3: Test the Model
Once you have trained a model, you can evaluate its final performance on the unseen test set using the test.py script.

```bash
python -m src.model.test --path models/ensemble_model.pkl
```
This will print the final ROC AUC and Precision-Recall AUC scores, giving you a reliable measure of your model's real-world performance.