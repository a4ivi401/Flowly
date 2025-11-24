from sqlalchemy.orm import Session
from sqlalchemy import desc, and_
from sqlalchemy.sql import func
from datetime import datetime, date, timedelta

from app import models, schemas


def get_task(db: Session, task_id: int):
    """Отримати задачу за ID"""
    return db.query(models.Task).filter(models.Task.id == task_id).first()


def get_tasks(db: Session, skip: int = 0, limit: int = 100, status: str = None, priority: int = None):
    """Отримати список задач з фільтрацією по статусу та пріоритету"""
    query = db.query(models.Task)

    if status:
        query = query.filter(models.Task.status == status)
    if priority:
        query = query.filter(models.Task.priority == priority)

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
        update_data = task_update.model_dump(exclude_unset=True)
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
    return db.query(models.Task) \
        .filter(and_(
        models.Task.deadline.isnot(None),
        models.Task.deadline < func.now(),
        models.Task.status != models.TaskStatus.COMPLETED
    )) \
        .order_by(models.Task.deadline) \
        .offset(skip).limit(limit).all()


def get_tasks_for_today(db: Session, target_date: str = None, days_ahead: int = 0):
    """
    Отримати задачі, актуальні для поточного дня

    - Задачі зі статусом 'pending' або 'in_progress'
    - З дедлайном сьогодні або в найближчі N днів
    """
    # Визначаємо цільову дату
    if target_date:
        target_date = datetime.strptime(target_date, "%Y-%m-%d").date()
    else:
        target_date = date.today()

    # Обчислюємо діапазон дат
    start_date = target_date
    end_date = target_date + timedelta(days=days_ahead)

    return db.query(models.Task) \
        .filter(
        and_(
            models.Task.status.in_([models.TaskStatus.PENDING, models.TaskStatus.IN_PROGRESS]),
            models.Task.deadline.isnot(None),
            models.Task.deadline >= start_date,
            models.Task.deadline <= end_date
        )
    ) \
        .order_by(models.Task.priority, models.Task.deadline) \
        .all()


# Додаткові CRUD функції
def get_tasks_by_status(db: Session, status: str, skip: int = 0, limit: int = 100):
    """Отримати задачі за статусом"""
    return db.query(models.Task) \
        .filter(models.Task.status == status) \
        .order_by(desc(models.Task.created_at)) \
        .offset(skip).limit(limit).all()


def get_tasks_stats(db: Session):
    """Отримати статистику по задачам"""
    total_tasks = db.query(models.Task).count()

    status_stats = db.query(
        models.Task.status,
        func.count(models.Task.id).label('count')
    ).group_by(models.Task.status).all()

    priority_stats = db.query(
        models.Task.priority,
        func.count(models.Task.id).label('count')
    ).group_by(models.Task.priority).all()

    return {
        "total_tasks": total_tasks,
        "status_stats": {stat.status.value: stat.count for stat in status_stats},
        "priority_stats": {stat.priority: stat.count for stat in priority_stats}
    }