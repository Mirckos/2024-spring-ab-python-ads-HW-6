from airflow import DAG
from airflow.providers.docker.operators.docker import DockerOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2024, 4, 2),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
        'train_model_daily',
        default_args=default_args,
        schedule_interval='@daily',
        catchup=False,  
) as dag: 
    train_model = DockerOperator(
        task_id='train_model',
        image='dashboard:latest',  
        api_version='auto',
        auto_remove=True,
        command='/bin/bash -c "python add_train.py"',   
        docker_url='unix://var/run/docker.sock', 
        network_mode='bridge',  

    )




