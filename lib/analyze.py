# This is the full content for your file: lib/analyze.py

import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt


# ==============================================================================
#  NEW: Function to Plot Individual Column Distributions (Your Request)
# ==============================================================================

def plot_univariate_distributions(df):
    """
    Analyzes each column in the DataFrame to plot its probability distribution.
    - For numeric columns, it plots a probability density histogram.
    - For categorical columns, it plots a probability bar chart.
    """
    print("\n" + "=" * 60)
    print("      Generating Univariate Probability Distributions")
    print("=" * 60 + "\n")

    for col in df.columns:
        # --- Plotting for NUMERIC columns ---
        if pd.api.types.is_numeric_dtype(df[col]):
            plt.figure(figsize=(10, 6))
            # stat="density" calculates the probability density, making the area under the histogram sum to 1.
            sns.histplot(df[col], kde=True, stat="density", color="skyblue")
            plt.title(f'Probability Density of {col}', fontsize=16)
            plt.xlabel(col, fontsize=12)
            plt.ylabel('Probability Density', fontsize=12)
            plt.show()

        # --- Plotting for CATEGORICAL columns ---
        elif pd.api.types.is_object_dtype(df[col]) or pd.api.types.is_categorical_dtype(df[col]):
            # Skip columns with too many unique values to be plotted meaningfully
            if 1 < df[col].nunique() < 50:
                plt.figure(figsize=(10, 6))
                # value_counts(normalize=True) calculates the probability of each category
                probabilities = df[col].value_counts(normalize=True)
                sns.barplot(x=probabilities.index, y=probabilities.values, hue=probabilities.index, palette="viridis",
                            legend=False)
                plt.title(f'Probability Distribution of {col}', fontsize=16)
                plt.xlabel(col, fontsize=12)
                plt.ylabel('Probability', fontsize=12)
                plt.xticks(rotation=45, ha='right')
                plt.tight_layout()
                plt.show()
            else:
                print(f"--> Skipping distribution plot for '{col}': Not a plottable categorical column.")


# ==============================================================================
#  Supporting Plotting Functions (Heatmap, Pairplot, etc.)
# ==============================================================================

def plot_heatmap(data, vmax=1.0):
    if data.shape[0] < 2 or data.shape[1] < 2: return
    plt.figure(figsize=(10, 6))
    sns.heatmap(data, cmap='coolwarm', annot=True, annot_kws={'size': 12}, vmax=vmax, fmt=".2f")
    plt.title("Correlation Heatmap of Numerical Features", fontsize=16)
    plt.show()


def plot_pairplot(data):
    numeric_data = data.select_dtypes(include='number')
    if numeric_data.empty: return
    sns.pairplot(numeric_data, diag_kind='kde')  # Use kde on diagonal for smoother distribution view
    plt.suptitle("Pairplot of Numerical Features", y=1.02, fontsize=16)
    plt.show()


def plot_bivariate_analysis(df):
    """
    Plots the mean of numeric columns grouped by categorical columns.
    This shows relationships between variables.
    """
    print("\n" + "=" * 60)
    print("      Generating Bivariate Analysis (Numeric vs. Categorical)")
    print("=" * 60 + "\n")

    categorical_cols = df.select_dtypes(include=['object', 'category']).columns
    numeric_cols = df.select_dtypes(include='number').columns

    for cat_col in categorical_cols:
        if 1 < df[cat_col].nunique() < 50:
            for num_col in numeric_cols:
                df_copy = df.copy()
                df_copy[cat_col] = df_copy[cat_col].astype(str)

                plt.figure(figsize=(12, 6))
                grouped = df_copy.groupby(cat_col)[num_col].mean().sort_values(ascending=False)
                sns.barplot(x=grouped.index, y=grouped.values, hue=grouped.index, palette="viridis", legend=False)
                plt.title(f"Mean of '{num_col}' by '{cat_col}'", fontsize=16)
                plt.xlabel(cat_col, fontsize=12)
                plt.ylabel(f"Average {num_col}", fontsize=12)
                plt.xticks(rotation=45, ha='right')
                plt.tight_layout()
                plt.show()


# ==============================================================================
#  UPDATED: Main EDA Function
# ==============================================================================

def perform_eda(df):
    print(f"Analyzing DataFrame...")
    print(f"Shape: {df.shape}")
    print(f"Data types: \n{df.dtypes}")
    print(f"Columns: \n{df.columns.tolist()}")
    print(f"Number of unique values: \n{df.nunique()}")
    print(f"First 5 rows: \n{df.head()}")
    print(f"Last 5 rows: \n{df.tail()}")
    print(f"Null count per column: \n{df.isnull().sum()}")
    print(f"Descriptive Stats: \n{df.describe(include='all')}")
    """
    Performs a full Exploratory Data Analysis with a focus on distributions.
    """
    print("\n" + "=" * 60)
    print("      Starting Comprehensive Exploratory Data Analysis")
    print("=" * 60 + "\n")

    # --- Step 1: Individual Probability Distributions (Your Primary Request) ---
    plot_univariate_distributions(df)

    # --- Step 2: High-Level Numeric Relationships ---
    print("\n--- Generating high-level numeric relationship plots ---")
    numeric_df = df.select_dtypes(include='number')
    if numeric_df.shape[1] >= 2:
        correlation_matrix = numeric_df.corr()
        plot_heatmap(correlation_matrix)
        plot_pairplot(df)

    # --- Step 3: Bivariate Analysis (Optional but Recommended) ---
    # This shows how numeric variables change across different categories.
    plot_bivariate_analysis(df)

    print("\n" + "=" * 60)
    print("      Exploratory Data Analysis Complete")
    print("=" * 60 + "\n")