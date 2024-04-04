# Создание кластера Kubernetes с Kind
kind create cluster --name airflow-cluster --config kind-cluster.yaml

kubectl create namespace airflow
kubectl config use-context airflow-cluster
helm repo add apache-airflow https://airflow.apache.org && helm repo update
helm install airflow apache-airflow/airflow --namespace airflow --debug

echo "Ожидание запуска Airflow..."
sleep 30

helm show values apache-airflow/airflow > values.yaml

yq eval '.executor = "KubernetesExecutor"' -i values.yaml
yq eval '.dags.gitSync.enabled = true' -i values.yaml
yq eval '.dags.gitSync.repo = "https://github.com/Mirckos/2024-spring-ab-python-ads-HW-6.git"' -i values.yaml
yq eval '.dags.gitSync.branch = "main"' -i values.yaml
yq eval '.dags.gitSync.rev = "HEAD"' -i values.yaml
yq eval '.dags.gitSync.depth = 1' -i values.yaml
yq eval '.dags.gitSync.maxFailures = 0' -i values.yaml
yq eval '.dags.gitSync.subPath = "dags"' -i values.yaml

echo "Сборка Docker образа..."
docker build -t airflow-custom:1.0.0 -f Dockerfile.airflow .

kind load docker-image airflow-custom:1.0.0 --name airflow-cluster

yq eval '.defaultAirflowRepository = "airflow-custom"' -i values.yaml
yq eval '.defaultAirflowTag = "1.0.0"' -i values.yaml

helm upgrade --install airflow apache-airflow/airflow --namespace airflow -f values.yaml --debug

echo "Настройка Airflow завершена."

echo "Сборка Docker образа для дэшборда..."
docker build -t dashboard:latest -f Dockerfile.dashboard .

echo "Загрузка Docker образа дэшборда в Kind кластер..."
kind load docker-image dashboard:latest --name airflow-cluster

echo "Развертывание дэшборда в Kubernetes..."

kubectl apply -f dashboard-deployment.yaml -n airflow
sleep 10
kubectl port-forward svc/airflow-webserver 8080:8080 -n airflow &
kubectl port-forward svc/streamlit-dashboard-service 8501:8501 -n airflow &

kubectl get services -n airflow