
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Đọc cấu hình từ file .env hoặc biến môi trường."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    postgres_db: str = "service_desk"
    postgres_user: str = "service_desk_user"
    postgres_password: str
    db_host: str = "localhost"
    db_port: int = 5433

    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 30

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+psycopg://{self.postgres_user}:"
            f"{self.postgres_password}@{self.db_host}:"
            f"{self.db_port}/{self.postgres_db}"
        )


settings = Settings()
