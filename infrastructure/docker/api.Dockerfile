FROM python:3.13-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
RUN groupadd --system fsi && useradd --system --gid fsi fsi
COPY pyproject.toml ./
COPY src/fmcg_sales_intelligence ./src/fmcg_sales_intelligence
RUN pip install --no-cache-dir .
COPY contracts ./contracts
COPY domain_packs ./domain_packs
USER fsi
EXPOSE 8000
CMD ["uvicorn", "fmcg_sales_intelligence.api.app:app", "--host", "0.0.0.0", "--port", "8000"]

