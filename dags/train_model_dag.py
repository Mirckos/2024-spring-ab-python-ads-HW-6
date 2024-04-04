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
        catchup=False,  # Добавлено, чтобы предотвратить запуск задач за прошедшие периоды
) as dag:
    # Определение задачи DockerOperator
    train_model = DockerOperator(
        task_id='train_model',
        image='dashboard:latest',  # Убедитесь, что образ доступен локально или в реестре, откуда его можно загрузить
        api_version='auto',
        auto_remove=True,
        command='/bin/bash -c "python script.py"',        # Указываем правильный путь к скрипту в контейнере
        docker_url='unix://var/run/docker.sock',  # Указываем путь к сокету Docker Daemon
        network_mode='bridge',  # Можно изменить в соответствии с требованиями к сети

    )




