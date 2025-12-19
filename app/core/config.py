from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    app_name: str = Field(default="jwt-toy", alias="APP_NAME")
    env: str = Field(default="dev", alias="ENV")

    jwt_issuer: str = Field(default="jwt-toy", alias="JWT_ISSUER")
    jwt_audience: str = Field(default="jwt-toy-client", alias="JWT_AUDIENCE")
    access_token_expires_min: int = Field(default=15, alias="ACCESS_TOKEN_EXPIRES_MIN")
    refresh_token_expires_days: int = Field(default=30, alias="REFRESH_TOKEN_EXPIRES_DAYS")

    jwt_secret_key: str = Field(..., alias="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")


settings = Settings()