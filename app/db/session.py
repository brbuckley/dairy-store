# app/db/session.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config.settings import Settings

settings = Settings()
DATABASE_URL = (
    settings.database_url
)  # e.g. "postgresql+psycopg2://user:pass@localhost:5432/db"

engine = create_engine(DATABASE_URL, future=True)
SessionLocal = sessionmaker(
    bind=engine, autoflush=False, autocommit=False, future=True
)
