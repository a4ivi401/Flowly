from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Налаштування підключення до MySQL
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://username:password@localhost/task_db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,
    echo=True  # Для логування SQL-запитів (вимкнути в продакшені)
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()