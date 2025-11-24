from sqlalchemy.orm import Session
from app import models, schemas

def get_task(db: Session, task_id: int):
    """Отримати задачу за ID"""
    return db.query(models.Task).filter(models.Task.id == task_id).first()

def get_tasks(db: Session, skip: int = 0, limit: int = 100):
    """Отримати список задач"""
    return db.query(models.Task).offset(skip).limit(limit).all()

def create_task(db: Session, task: schemas.TaskCreate):
    """Створити нову задачу"""
    db_task = models.Task(
        title=task.title,
        description=task.description,
        is_completed=task.is_completed
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

def update_task(db: Session, task_id: int, task_update: schemas.TaskUpdate):
    """Оновити задачу"""
    db_task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if db_task:
        update_data = task_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_task, field, value)
        db.commit()
        db.refresh(db_task)
    return db_task

def delete_task(db: Session, task_id: int):
    """Видалити задачу"""
    db_task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if db_task:
        db.delete(db_task)
        db.commit()
    return db_task


from sqlalchemy.orm import Session
from app import models, schemas
from sqlalchemy import desc


def get_task(db: Session, task_id: int):
    """Отримати задачу за ID"""
    return db.query(models.Task).filter(models.Task.id == task_id).first()


def get_tasks(db: Session, skip: int = 0, limit: int = 100, status: str = None):
    """Отримати список задач з фільтрацією по статусу"""
    query = db.query(models.Task)

    if status:
        query = query.filter(models.Task.status == status)

    return query.order_by(desc(models.Task.created_at)).offset(skip).limit(limit).all()


def create_task(db: Session, task: schemas.TaskCreate):
    """Створити нову задачу"""
    db_task = models.Task(
        title=task.title,
        description=task.description,
        priority=task.priority,
        duration_minutes=task.duration_minutes,
        deadline=task.deadline,
        status=task.status
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


def update_task(db: Session, task_id: int, task_update: schemas.TaskUpdate):
    """Оновити задачу"""
    db_task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if db_task:
        update_data = task_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_task, field, value)
        db.commit()
        db.refresh(db_task)
    return db_task


def delete_task(db: Session, task_id: int):
    """Видалити задачу"""
    db_task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if db_task:
        db.delete(db_task)
        db.commit()
    return db_task


def get_tasks_by_priority(db: Session, priority: int, skip: int = 0, limit: int = 100):
    """Отримати задачі за пріоритетом"""
    return db.query(models.Task) \
        .filter(models.Task.priority == priority) \
        .order_by(desc(models.Task.created_at)) \
        .offset(skip).limit(limit).all()


def get_overdue_tasks(db: Session, skip: int = 0, limit: int = 100):
    """Отримати прострочені задачі"""
    from sqlalchemy import and_
    return db.query(models.Task) \
        .filter(and_(
        models.Task.deadline.isnot(None),
        models.Task.deadline < func.now(),
        models.Task.status != models.TaskStatus.COMPLETED
    )) \
        .order_by(models.Task.deadline) \
        .offset(skip).limit(limit).all()