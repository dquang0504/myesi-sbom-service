import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://myesi:password@postgres:5432/myesi_db"
    REDIS_URL: str = os.getenv("REDIS_URL", "localhost:6379")
    S3_BUCKET: str = ""
    S3_ENDPOINT: str = ""
    S3_ACCESS_KEY: str = ""
    S3_SECRET_KEY: str = ""
    OBJECT_STORAGE_PROVIDER: str = "s3"
    API_PREFIX: str = "/api/sbom"

    class Config:
        env_file = ".env"


settings = Settings()
