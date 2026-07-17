SELECT 'CREATE DATABASE mlflow OWNER fmcg'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'mlflow')\gexec

