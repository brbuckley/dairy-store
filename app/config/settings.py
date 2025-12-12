# app/core/config.py
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    env: str = "db"  # "dev", "prod", "test", etc.
    database_url: str = (
        "postgresql+psycopg2://postgres:postgres@localhost:5432/dairy"
    )

    class Config:
        env_prefix = "DAIRY_STORE_"
