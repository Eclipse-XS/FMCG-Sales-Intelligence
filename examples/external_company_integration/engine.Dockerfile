FROM python:3.13-slim AS engine
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 FSI_PROJECT_ROOT=/app PYTHONPATH=/example
WORKDIR /app
COPY pyproject.toml ./
RUN python -c "import subprocess,tomllib; p=tomllib.load(open('pyproject.toml','rb')); subprocess.check_call(['pip','install','--no-cache-dir',*p['project']['dependencies'],*p['project']['optional-dependencies']['mlflow']])"
COPY src ./src
RUN pip install --no-cache-dir --no-deps .
COPY config ./config
COPY examples/external_company_integration /example
RUN pip install --no-cache-dir --no-deps /example/backend && useradd --uid 10001 --create-home demo && mkdir /state /company-data && chown demo /state /company-data
USER demo
CMD ["uvicorn", "engine_service:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000"]

FROM engine AS verification
USER root
RUN pip install --no-cache-dir pytest==9.1.1 httpx==0.28.1
USER demo
CMD ["python", "-m", "pytest", "/example/tests", "-q", "--tb=short", "-o", "cache_dir=/tmp/pytest-cache"]
