import pandas as pd
import numpy as np


def preprocess_data(df):
    nominal_cols = ["Gender", "City", "Occupation", "Partner", "Betting Apps", "TrueCaller Flag",
                    "Sentiment on Social Media"]  # not ordered
    ordinal_cols = ["Education", "Reviews received"]  # ordered
    id_cols = ["Name", "Age", "Phone No."]
    education_order = ['Primary or less', 'Secondary', 'Tertiary or more']
    reviews_order = ['1 Star', '2 Star', '3 Star', '4 Star', '5 Star']
    numerical_cols = [col for col in df.columns if col not in nominal_cols and col not in ordinal_cols and col not in id_cols]

    for col in numerical_cols:
        df[col].fillna(df[col].median(), inplace=True)

    for col in nominal_cols + ordinal_cols:
        df[col].fillna(df[col].mode()[0], inplace=True)



    df_encoded_nominal = pd.get_dummies(df[nominal_cols], columns=nominal_cols, dtype=int)

    education_mapping = {category: i for i, category in enumerate(education_order)}
    reviews_mapping = {category: i for i, category in enumerate(reviews_order)}

    df['Education'] = df['Education'].map(education_mapping)
    df['Reviews received'] = df['Reviews received'].map(reviews_mapping)

    df_final = df.drop(columns=nominal_cols)
    df_final = pd.concat([df_final, df_encoded_nominal], axis=1)

    df_final.to_csv('data/preprocessed_fabricated_data.csv')
