from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from app.database import SessionLocal, engine
from app import models, schemas, crud
from app.models import Base

# Створюємо таблиці в базі даних
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Flowly Task Manager API",
    description="Базовий бекенд для управління задачами",
    version="1.0.0"
)

# Залежність для отримання сесії бази даних
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/health")
async def health_check():
    """Ендпоінт для перевірки роботи сервера"""
    return {"status": "ok"}

@app.get("/")
async def root():
    """Кореневий ендпоінт"""
    return {"message": "Ласкаво просимо до Task Manager API"}

@app.get("/tasks/", response_model=list[schemas.Task])
def read_tasks(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Отримати список задач"""
    tasks = crud.get_tasks(db, skip=skip, limit=limit)
    return tasks

@app.post("/tasks/", response_model=schemas.Task)
def create_task(task: schemas.TaskCreate, db: Session = Depends(get_db)):
    """Створити нову задачу"""
    return crud.create_task(db=db, task=task)

@app.get("/tasks/{task_id}", response_model=schemas.Task)
def read_task(task_id: int, db: Session = Depends(get_db)):
    """Отримати задачу за ID"""
    task = crud.get_task(db, task_id=task_id)
    return task

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


    @app.get("/test-db")
    async def test_db_connection(db: Session = Depends(get_db)):
        """Тестовий ендпоінт для перевірки роботи БД"""
        try:
            result = db.execute(text("SELECT NOW() as current_time"))
            current_time = result.fetchone()

            table_count = db.execute(text("""
                                          SELECT COUNT(*)
                                          FROM information_schema.tables
                                          WHERE table_schema = DATABASE()
                                          """))
            tables = table_count.scalar()

            return {
                "status": "success",
                "current_time": current_time[0],
                "tables_in_database": tables,
                "message": "База даних працює коректно"
            }
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Помилка при роботі з БД: {str(e)}"
            )