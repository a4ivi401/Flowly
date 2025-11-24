import os
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Завантажуємо змінні з .env файлу
load_dotenv()

# Отримуємо параметри підключення з .env (з вашого конфігу)
DB_HOST = os.getenv("BACKEND_DB_HOST", "localhost")
DB_PORT = os.getenv("BACKEND_DB_PORT", "3306")
DB_USER = os.getenv("BACKEND_DB_USER", "root")
DB_PASSWORD = os.getenv("BACKEND_DB_PASSWORD", "")
DB_NAME = os.getenv("BACKEND_DB_NAME", "ai_time_manager")

# Формуємо URL для підключення
DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

print(f"🔗 Підключення до БД: {DB_USER}@{DB_HOST}:{DB_PORT}/{DB_NAME}")

# Створюємо engine з налаштуваннями для стабільності
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Перевіряє з'єднання перед використанням
    pool_recycle=3600,   # Перестворює з'єднання кожну годину
    echo=True,           # Логування SQL (для дебагу)
    pool_size=10,        # Максимальна кількість з'єднань
    max_overflow=20,     # Додаткові з'єднання при навантаженні
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()

# Функція для отримання сесії БД
def get_db():
    """
    Залежність для FastAPI, що надає сесію БД
    """
    db = SessionLocal()
    try:
        # Перевіряємо підключення
        db.execute(text("SELECT 1"))
        yield db
    except Exception as e:
        # Якщо помилка - закриваємо сесію
        db.close()
        raise e
    finally:
        db.close()

# Функція для тестування підключення
def test_connection():
    """
    Тестує підключення до БД
    """
    try:
        db = SessionLocal()
        result = db.execute(text("SELECT 1"))
        db.close()
        print("✅ Підключення до БД успішне!")
        return True
    except Exception as e:
        print(f"❌ Помилка підключення до БД: {e}")
        return False

# Функція для створення таблиць
def create_tables():
    """
    Створює всі таблиці в БД
    """
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Таблиці успішно створені!")
    except Exception as e:
        print(f"❌ Помилка створення таблиць: {e}")