# app/core/config.py
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    env: str = "dev"  # "dev", "prod", "test", etc.

    class Config:
        env_prefix = "DAIRY_STORE_"
