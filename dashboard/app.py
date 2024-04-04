import pandas as pd
import streamlit as st
from catboost import CatBoostClassifier
from sklearn.ensemble import RandomForestClassifier
from sklift.models import SoloModel, TwoModels

from train import UpliftPipeline

pipe = UpliftPipeline(
    features_path='df_features.parquet',
    train_path='df_train.parquet',
)

params = {'iterations': 20, 'thread_count': 2, 'random_state': 42, 'silent': True}
params_RF = {
    'n_estimators': 100,
    'max_depth': 3,
    'random_state': 42
}
st.title('Uplift Predictions')

app_mode = st.sidebar.selectbox('Mode', ['About', 'EDA', 'Train & Evaluate'])

if app_mode == "About":
    st.markdown("Uplift Predictions")

    st.markdown("This dashboard allows you to ABC...")

elif app_mode == "EDA":
    if st.button('Load Data'):
        pipe.load_data()
        st.write("Data successfully uploaded!")

    st.sidebar.subheader('Quick Explore')
    st.markdown("Tick the box on the side panel to explore the dataset.")

    df_selection = st.sidebar.selectbox('Data Frame', ['Features', 'Train data'])

    if df_selection == 'Features':
        df = pd.read_parquet(pipe.features_path)
    else:
        df = pd.read_parquet(pipe.train_path)

    if st.sidebar.checkbox("Show Columns"):
        st.subheader('Show Columns List')
        all_columns = df.columns.tolist()
        st.write(all_columns)

    if st.sidebar.checkbox("Statistical Description"):
        st.subheader("Statistical Data Description")
        st.write(df.describe())

    if st.sidebar.checkbox('Missing Values'):
        st.subheader('Missing values')
        st.write(df.isnull().sum())

else:
    size = st.sidebar.slider('Test Set Size', min_value=0.1, max_value=0.5)
    pipe.make_train_test_split(size)

    if st.sidebar.checkbox('Show the shape of training and test set features and labels'):
        st.write('X_train: ', pipe.X_train.shape)
        st.write('y_train: ', pipe.y_train.shape)
        st.write('X_val: ', pipe.X_val.shape)
        st.write('y_val: ', pipe.y_val.shape)

    approach_name = st.selectbox('Approach', ['Solo Model', 'Two Models'])
    classifier_name = st.selectbox('Classifier', ['CatBoostClassifier', 'RandomForestClassifier'])

    pipe.load_model(arch=classifier_name, method=approach_name)

    if approach_name == 'Solo Model':
        if classifier_name == 'CatBoostClassifier':
            init_model = SoloModel(estimator=CatBoostClassifier(**params))
            fig = pipe.train_and_evaluate_model(
                init_model,
                estimator_fit_params={'cat_features': ['gender']}, method='SM', arch='CB'
            )
        else:
            init_model = SoloModel(estimator=RandomForestClassifier(**params_RF))
            fig = pipe.train_and_evaluate_model(
                init_model, method='SM', arch='RF'
            )
    elif approach_name == 'Two Models':
        if classifier_name == 'CatBoostClassifier':
            init_model = TwoModels(
                estimator_trmnt=CatBoostClassifier(**params),
                estimator_ctrl=CatBoostClassifier(**params),
                method='vanilla',
            )

            fig = pipe.train_and_evaluate_model(
                init_model,
                estimator_trmnt_fit_params={'cat_features': ['gender']},
                estimator_ctrl_fit_params={'cat_features': ['gender']},
                method='TL', arch='CB'
            )
        else:
            init_model = TwoModels(
                estimator_trmnt=RandomForestClassifier(**params_RF),
                estimator_ctrl=RandomForestClassifier(**params_RF),
                method='vanilla',
            )

            fig = pipe.train_and_evaluate_model(
                init_model, method='TL', arch='RF')

    st.pyplot(fig)
