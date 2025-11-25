from datetime import datetime
from pathlib import Path
import logging

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.database import get_db, test_connection, create_tables
from app import crud, schemas
from app.models import TaskStatus
from app.planning_service import PlanningService


LOG_DIR = Path(__file__).resolve().parent / "logs"
LOG_DIR.mkdir(exist_ok=True)
LOG_START_TIME = datetime.now()
LOG_FILE_RUNNING = LOG_DIR / f"flowly_{LOG_START_TIME:%Y%m%d_%H%M%S}_running.log"
_file_handler: logging.FileHandler | None = None


def setup_logging() -> None:
    """Configure console + file logging for the app lifecycle."""
    global _file_handler

    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    file_handler = logging.FileHandler(LOG_FILE_RUNNING, encoding="utf-8")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    _file_handler = file_handler

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.handlers.clear()
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)


setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Flowly API",
    description="Бекенд для управління часом з AI",
    version="1.0.0"
)

# Додаємо CORS після створення застосунку
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Для продакшену вкажіть конкретні домени
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Перевіряє підключення до БД при старті"""
    logger.info("🚀 Запуск Flowly API...")

    if test_connection():
        logger.info("✅ Підключення до БД успішне!")
        try:
            create_tables()
            logger.info("✅ Таблиці БД готові до роботи")
        except Exception as e:
            logger.warning("⚠️  Попередження при створенні таблиць: %s", e)
    else:
        logger.error("❌ Не вдалося підключитися до БД!")


@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Перевірка роботи сервера та БД"""
    try:
        result = db.execute(text("SELECT 1"))
        version_result = db.execute(text("SELECT VERSION()"))
        mysql_version = version_result.scalar()

        return {
            "status": "ok",
            "database": "connected",
            "mysql_version": mysql_version,
            "message": "Сервер та БД працюють нормально"
        }
    except Exception as e:
        logger.exception("Помилка БД при health_check: %s", e)
        raise HTTPException(
            status_code=500,
            detail=f"Помилка БД: {str(e)}"
        )


@app.get("/")
async def root():
    return {
        "message": "Ласкаво просимо до Flowly API",
        "version": "1.0.0"
    }


@app.post("/plan/today", response_model=schemas.PlanningResponse)
def run_planning_today(body: schemas.PlanningRequest, db: Session = Depends(get_db)):
    """Запустити планування на поточний день, зберегти й повернути впорядкований список задач."""
    service = PlanningService(db)
    return service.run(body)


@app.get("/plan/today/optimized", response_model=schemas.PlanningResponse)
def get_optimized_plan(timezone: str = "UTC", db: Session = Depends(get_db)):
    """Отримати вже збережений впорядкований план із таблиці planned_tasks."""
    service = PlanningService(db)
    return service.get_saved_plan(timezone=timezone)


@app.get("/test-db")
async def test_db_connection(db: Session = Depends(get_db)):
    """Тестовий ендпоінт для перевірки роботи БД"""
    try:
        # MySQL treats CURRENT_TIME as reserved, so keep the query simple
        current_time = db.execute(text("SELECT NOW()")).scalar()

        table_count = db.execute(text("""
                                      SELECT COUNT(*)
                                      FROM information_schema.tables
                                      WHERE table_schema = DATABASE()
                                      """))
        tables = table_count.scalar()

        return {
            "status": "success",
            "current_time": current_time,
            "tables_in_database": tables,
            "message": "База даних працює коректно"
        }
    except Exception as e:
        logger.exception("Помилка при роботі з БД: %s", e)
        raise HTTPException(
            status_code=500,
            detail=f"Помилка при роботі з БД: {str(e)}"
        )


# ОСНОВНІ ЕНДПОЇНТИ ДЛЯ РОБОТИ З ЗАДАЧАМИ

@app.post("/tasks/", response_model=schemas.Task)
def create_task(task: schemas.TaskCreate, db: Session = Depends(get_db)):
    """Створити нову задачу"""
    return crud.create_task(db=db, task=task)


@app.get("/tasks/", response_model=list[schemas.Task])
def read_tasks(
        skip: int = 0,
        limit: int = 100,
        status: str = None,
        priority: int = None,
        db: Session = Depends(get_db)
):
    """Отримати список задач з фільтрацією"""
    tasks = crud.get_tasks(db, skip=skip, limit=limit, status=status, priority=priority)
    return tasks


@app.get("/tasks/{task_id}", response_model=schemas.Task)
def read_task(task_id: int, db: Session = Depends(get_db)):
    """Отримати задачу за ID"""
    task = crud.get_task(db, task_id=task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Задачу не знайдено")
    return task


@app.put("/tasks/{task_id}", response_model=schemas.Task)
def update_task(task_id: int, task_update: schemas.TaskUpdate, db: Session = Depends(get_db)):
    """Оновити задачу"""
    task = crud.update_task(db, task_id=task_id, task_update=task_update)
    if task is None:
        raise HTTPException(status_code=404, detail="Задачу не знайдено")
    return task


@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    """Видалити задачу"""
    task = crud.delete_task(db, task_id=task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Задачу не знайдено")
    return {"ok": True}


@app.on_event("shutdown")
async def shutdown_event():
    """Логує момент завершення та зберігає лог з датою/часом завершення."""
    global _file_handler
    end_time = datetime.now()
    target_log = LOG_DIR / f"flowly_{end_time:%Y%m%d_%H%M%S}.log"
    logger.info("🛑 Зупинка Flowly API о %s", end_time.isoformat())

    if _file_handler:
        root_logger = logging.getLogger()
        _file_handler.flush()
        _file_handler.close()
        root_logger.removeHandler(_file_handler)
        _file_handler = None
        try:
            LOG_FILE_RUNNING.rename(target_log)
            logger.info("Логи збережено у файлі: %s", target_log)
        except Exception as exc:
            logger.error("Не вдалося перейменувати лог-файл: %s", exc)


@app.get("/tasks/priority/{priority}", response_model=list[schemas.Task])
def read_tasks_by_priority(priority: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Отримати задачі за пріоритетом"""
    if priority < 1 or priority > 5:
        raise HTTPException(status_code=400, detail="Пріоритет має бути від 1 до 5")
    tasks = crud.get_tasks_by_priority(db, priority=priority, skip=skip, limit=limit)
    return tasks

@app.get("/tasks/status/overdue", response_model=list[schemas.Task])
def read_overdue_tasks(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Отримати прострочені задачі"""
    tasks = crud.get_overdue_tasks(db, skip=skip, limit=limit)
    return tasks

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_config=None)
