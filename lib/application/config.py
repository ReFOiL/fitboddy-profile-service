from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = Field(default="sqlite+pysqlite:///./profile_service.db", alias="DATABASE_URL")
    alembic_ini_path: str = Field(default="alembic.ini", alias="ALEMBIC_INI_PATH")
    auth_service_url: str = Field(default="http://localhost:8001", alias="AUTH_SERVICE_URL")
    tenant_service_url: str = Field(default="http://localhost:8002", alias="TENANT_SERVICE_URL")
    http_timeout_seconds: float = Field(default=5.0, alias="HTTP_TIMEOUT_SECONDS", gt=0)
    s3_media_enabled: bool = Field(default=False, alias="S3_MEDIA_ENABLED")
    s3_endpoint: str = Field(default="", alias="S3_ENDPOINT")
    s3_access_key: str = Field(default="", alias="S3_ACCESS_KEY")
    s3_secret_key: str = Field(default="", alias="S3_SECRET_KEY")
    s3_bucket: str = Field(default="fitboddy-media", alias="S3_BUCKET")
    s3_secure: bool = Field(default=False, alias="S3_SECURE")
    s3_public_base_url: str | None = Field(default=None, alias="S3_PUBLIC_BASE_URL")
    s3_avatars_prefix: str = Field(default="avatars/", alias="S3_AVATARS_PREFIX")
