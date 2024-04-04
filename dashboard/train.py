import os
import pickle

import pandas as pd
from sklearn.model_selection import train_test_split
from sklift.datasets import fetch_x5
from sklift.viz import plot_uplift_curve


class UpliftPipeline():
    def __init__(self, features_path, train_path, model_path='model.pkl'):
        self.features_path = features_path
        self.train_path = train_path
        self.model_path = model_path
        self.model = None
        self.model_choice = None

    def load_data(self):
        dataset = fetch_x5()

        df_clients = dataset.data['clients'].set_index("client_id")
        df_train = pd.concat([dataset.data['train'], dataset.treatment, dataset.target], axis=1).set_index("client_id")

        df_features = df_clients.copy()
        df_features['first_issue_time'] = \
            (pd.to_datetime(df_features['first_issue_date'])
             - pd.Timestamp('1970-01-01')) // pd.Timedelta('1s')
        df_features['first_redeem_time'] = \
            (pd.to_datetime(df_features['first_redeem_date'])
             - pd.Timestamp('1970-01-01')) // pd.Timedelta('1s')
        df_features['issue_redeem_delay'] = df_features['first_redeem_time'] \
                                            - df_features['first_issue_time']
        df_features = df_features.drop(['first_issue_date', 'first_redeem_date'], axis=1)

        df_features.to_parquet(self.features_path)
        df_train.to_parquet(self.train_path)

    def make_train_test_split(self, test_size):
        self.df_features = pd.read_parquet(self.features_path)
        self.df_train = pd.read_parquet(self.train_path)
        indices_learn, indices_valid = train_test_split(
            self.df_train.index, test_size=test_size, random_state=123
        )
        indices_test = pd.Index(set(self.df_features.index) - set(self.df_train.index))

        self.X_train = self.df_features.loc[indices_learn, :]
        self.y_train = self.df_train.loc[indices_learn, 'target']
        self.treat_train = self.df_train.loc[indices_learn, 'treatment_flg']

        self.X_val = self.df_features.loc[indices_valid, :]
        self.y_val = self.df_train.loc[indices_valid, 'target']
        self.treat_val = self.df_train.loc[indices_valid, 'treatment_flg']

        self.X_test = self.df_features.loc[indices_test, :]

    def train_and_evaluate_model(self, model, method, arch, **kwargs):
        if self.model is None:
            self.model = model
        if not method:
            model_param = []
            with open('model_param.txt', 'r+') as file:
                for line in file:
                    model_param.append(line)
                method, arch = model_param

        self.model.fit(
            self.X_train,
            self.y_train,
            self.treat_train,
            **kwargs
        )

        uplift_preds = self.model.predict(self.X_val)
        self.save_model(method, arch)

        return plot_uplift_curve(
            y_true=self.y_val,
            uplift=uplift_preds,
            treatment=self.treat_val,
            perfect=False
        ).figure_

    def save_model(self, method, arch):
        with open(''.join((self.model_path, method, arch)), 'wb') as file:
            pickle.dump(self.model, file)
        with open('model_param.txt', 'r+') as file:
            file.writelines([method, arch])

    def load_model(self, method, arch):
        if os.path.exists(self.model_path):
            with open(''.join((self.model_path, method, arch)), 'rb') as file:
                self.model = pickle.load(file)
