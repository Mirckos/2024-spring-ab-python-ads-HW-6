import streamlit as st

import numpy as np
import pandas as pd

from dashboard.train import UpliftPipeline


def simulate_data_update(features_path, train_path, test_size=0.2):
    df_features = pd.read_parquet(features_path)
    df_train = pd.read_parquet(train_path)

    remove_n = int(len(df_features) * test_size)
    drop_indices = np.random.choice(df_features.index, remove_n, replace=False)
    df_features = df_features.drop(drop_indices)

    remove_n = int(len(df_train) * test_size)
    drop_indices = np.random.choice(df_train.index, remove_n, replace=False)
    df_train = df_train.drop(drop_indices)

    df_features.to_parquet('df_features_new')
    df_train.to_parquet('df_train_new')


def train_model():
    """Дообучает модель на новых данных."""

    pipe = UpliftPipeline(
        features_path='df_features_new',
        train_path='df_train_new'
    )

    pipe.load_model()
    pipe.make_train_test_split(0.2)
    fig = pipe.train_and_evaluate_model(None,None,None)

    st.pyplot(fig)


def main():
    simulate_data_update('df_features.parquet', 'df_train.parquet')

    train_model()


if __name__ == "__main__":
    main()
