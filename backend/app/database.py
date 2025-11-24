from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[2] / ".env",
        env_file_encoding="utf-8",
        env_prefix="BACKEND_DB_",
        extra="ignore",
    )

    host: str = os.getenv("BACKEND_DB_HOST")
    port: int = os.getenv("BACKEND_DB_PORT")
    user: str = os.getenv("BACKEND_DB_USER")
    password: str = os.getenv("BACKEND_DB_PASSWORD")
    name: str = os.getenv("BACKEND_DB_NAME")


settings = Settings()

SQLALCHEMY_DATABASE_URL = (
    f"mysql+pymysql://{settings.user}:{settings.password}"
    f"@{settings.host}:{settings.port}/{settings.name}"
)

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,
    echo=True,  # Для логування SQL-запитів (вимкнути в продакшені)
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
