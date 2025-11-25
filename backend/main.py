from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.database import get_db, test_connection, create_tables
from app import crud, schemas
from app.models import TaskStatus

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
    print("🚀 Запуск Flowly API...")

    if test_connection():
        print("✅ Підключення до БД успішне!")
        try:
            create_tables()
            print("✅ Таблиці БД готові до роботи")
        except Exception as e:
            print(f"⚠️  Попередження при створенні таблиць: {e}")
    else:
        print("❌ Не вдалося підключитися до БД!")


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
    uvicorn.run(app, host="0.0.0.0", port=8000)
