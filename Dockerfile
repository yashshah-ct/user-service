FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends gcc libpq-dev openssl && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml ./
COPY src/ src/
COPY alembic.ini ./
COPY alembic/ alembic/
RUN pip install -e . \
    && mkdir -p /app/keys \
    && openssl genrsa -out /app/keys/private.pem 2048 \
    && openssl rsa -in /app/keys/private.pem -pubout -out /app/keys/public.pem

EXPOSE 8000

CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
