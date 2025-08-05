import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

def analyze_dataframe(df):
    print(f"Analyzing DataFrame...")
    print(f"Shape: {df.shape}")
    print(f"Data types: \n{df.dtypes}")
    print(f"Columns: \n{df.columns.tolist()}")
    print(f"Number of unique values: \n{df.nunique()}")
    print(f"First 5 rows: \n{df.head()}")
    print(f"Last 5 rows: \n{df.tail()}")
    print(f"Null count per column: \n{df.isnull().sum()}")
    print(f"Descriptive Stats: \n{df.describe(include='all')}")

    numeric_df = df.select_dtypes(include='number')
    if not numeric_df.empty:
        print("Correlation Heatmap:")
        plot_heatmap(numeric_df.corr(numeric_only=True), vmax=1)

        print("Pairplot of numerical features:")
        plot_pairplot(numeric_df)

    print("Value Counts for Categorical Features:")
    plot_value_counts(df)

    id_column = 'Aadhar No.'
    df = df.reset_index()
    print(f"Bar plots by `{id_column}`:")
    for col in df.columns:
        if col != id_column and pd.api.types.is_numeric_dtype(df[col]):
            plot_bargraph(df, (id_column, col))
    df.set_index(id_column, inplace=True)

def plot_heatmap(data, vmax):
    plt.figure(figsize=(10,6))
    sns.set(font_scale = 1.4)
    sns.heatmap(data, cmap='coolwarm', annot=True, annot_kws={'size': 15}, vmax=vmax, fmt=".2f")
    plt.title("Correlation Heatmap")
    plt.show()

def plot_pairplot(data):
    sns.pairplot(data.select_dtypes(include='number'))
    plt.suptitle("Pairplot of Numerical Features", y=1.02)
    plt.show()


def plot_bargraph(data, columns, bins=30):
    x, y = columns  # unpack the tuple

    plt.figure(figsize=(8, 4))

    # If numeric → histogram
    if pd.api.types.is_numeric_dtype(data[y]) and data[y].nunique() > 20:
        plt.hist(data[y].dropna(), bins=bins, density=True, alpha=0.7, color='g')
        plt.title(f"Distribution of {y}")
        plt.xlabel(y)
        plt.ylabel("Probability Density")
    else:
        grouped = data.groupby(x)[y].mean().sort_values(ascending=False)
        sns.barplot(x=grouped.index, y=grouped.values)
        plt.title(f"{y} by {x}")
        plt.xticks(rotation=45)

    plt.tight_layout()
    plt.show()

def plot_value_counts(df):
    for col in df.select_dtypes(include='object').columns:
        if df[col].nunique() < 500:
            plt.figure(figsize=(8, 3))
            df[col].value_counts().plot(kind='bar')
            plt.title(f"Value Counts: {col}")
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.show()
