FROM python:3.13-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
RUN groupadd --system fsi && useradd --system --gid fsi fsi
COPY pyproject.toml ./
COPY src/fmcg_sales_intelligence ./src/fmcg_sales_intelligence
RUN pip install --no-cache-dir . psycopg[binary]==3.3.5 sqlalchemy
COPY config ./config
USER fsi
CMD ["python", "src/fmcg_sales_intelligence/product/analytics/publish_scientific_results.py"]
