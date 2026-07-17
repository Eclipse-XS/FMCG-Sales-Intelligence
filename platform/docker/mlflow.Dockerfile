FROM python:3.13-slim
RUN pip install --no-cache-dir mlflow==3.16.1 psycopg[binary]==3.3.5
RUN groupadd --system mlflow && useradd --system --gid mlflow mlflow && mkdir -p /mlflow/artifacts && chown -R mlflow:mlflow /mlflow
USER mlflow
EXPOSE 5000
