# User Service

Microservice for user registration, login, and JWT issuance.

## Endpoints

- POST /users - Register user
- POST /auth/login - Login
- GET /users/{id} - Get user
- PATCH /users/{id} - Update user
- GET /auth/jwks - JWKS for JWT validation
- GET /health - Health check
- GET /metrics - Prometheus metrics

## Run

```bash
docker compose up --build
```

Service runs on port 8000.
