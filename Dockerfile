FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends gcc libpq-dev openssl && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml ./
COPY src/ src/
COPY alembic.ini ./
COPY alembic/ alembic/
RUN pip install -e . && mkdir -p /app/keys

EXPOSE 8000

COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh
ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
