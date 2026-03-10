from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Set via env in production; no hardcoded credentials
    database_url: str = "postgresql+asyncpg://localhost:5432/userdb"
    rabbitmq_url: str = "amqp://localhost:5672/"
    jwt_private_key_path: str = "./keys/private.pem"
    jwt_public_key_path: str = "./keys/public.pem"
    jwt_algorithm: str = "RS256"
    jwt_expiry_seconds: int = 3600
    log_level: str = "INFO"

    class Config:
        env_file = ".env"


settings = Settings()
