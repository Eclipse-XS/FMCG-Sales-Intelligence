FROM python:3.13-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /company
COPY examples/external_company_integration/backend /company
RUN pip install --no-cache-dir . && useradd --uid 10001 --create-home servicedesk
USER servicedesk
CMD ["uvicorn", "servicedesk.app:create_app", "--factory", "--host", "0.0.0.0", "--port", "8080"]
