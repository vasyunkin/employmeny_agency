from pydantic import SecretStr, Field
from pydantic_settings import BaseSettings as _BaseSettings
from pydantic_settings import SettingsConfigDict
from sqlalchemy import URL


class BaseSettings(_BaseSettings):
    model_config = SettingsConfigDict(
        extra="ignore",
        env_file=".env",
        env_file_encoding="utf-8",
    )


class PostgresConfig(BaseSettings, env_prefix="POSTGRES_"):
    host: str
    port: int
    user: str
    password: SecretStr
    database: str

    enable_logging: bool = False

    def build_dsn(self) -> str:
        return URL.create(
            drivername="postgresql+asyncpg",
            username=self.user,
            password=self.password.get_secret_value(),
            host=self.host,
            port=self.port,
            database=self.db,
        ).render_as_string(hide_password=False)


class AuthConfig(BaseSettings, env_prefix="AUTH_"):
    """Конфигурация для аутентификации и JWT"""
    secret_key: SecretStr = Field(..., min_length=32)

    def get_secret_key(self) -> str:
        """Возвращает секретный ключ как строку"""
        return self.secret_key.get_secret_value()


postgres_config = PostgresConfig()
auth_config = AuthConfig()