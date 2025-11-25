from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, case
from sqlalchemy.sql import func
from datetime import datetime, date, timedelta

from app import models, schemas, status_utils


def _normalize_task(task: models.Task):
    """Перетворює статус задачі до канонічного значення для API."""
    return status_utils.normalize_task_status(task)


def _normalize_tasks(tasks: list[models.Task]):
    return status_utils.normalize_tasks(tasks)


def get_task(db: Session, task_id: int):
    """Отримати задачу за ID"""
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    return _normalize_task(task)


def get_tasks(db: Session, skip: int = 0, limit: int = 100, status: str = None, priority: int = None):
    """Отримати список задач з фільтрацією по статусу та пріоритету"""
    query = db.query(models.Task).outerjoin(models.PlannedTask, models.PlannedTask.task_id == models.Task.id)

    if status:
        db_status = status_utils.to_db_status(status)
        query = query.filter(models.Task.status == db_status)
    if priority:
        query = query.filter(models.Task.priority == priority)

    order_expr = case(
        (models.PlannedTask.priority_rank == None, 1),
        else_=0
    )

    tasks = (
        query
        .order_by(order_expr, models.PlannedTask.priority_rank, desc(models.Task.created_at))
        .offset(skip)
        .limit(limit)
        .all()
    )
    return _normalize_tasks(tasks)


def create_task(db: Session, task: schemas.TaskCreate):
    """Створити нову задачу"""
    db_task = models.Task(
        title=task.title,
        description=task.description,
        priority=task.priority,
        duration_minutes=task.duration_minutes,
        deadline=task.deadline,
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return _normalize_task(db_task)


def update_task(db: Session, task_id: int, task_update: schemas.TaskUpdate):
    """Оновити задачу"""
    db_task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if db_task:
        update_data = task_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if field == "status":
                setattr(db_task, field, status_utils.to_db_status(value))
            else:
                setattr(db_task, field, value)
        db.commit()
        db.refresh(db_task)
    return _normalize_task(db_task)


def delete_task(db: Session, task_id: int):
    """Видалити задачу"""
    db_task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if db_task:
        db.delete(db_task)
        db.commit()
    return db_task


def get_plannable_tasks(db: Session):
    """Отримати задачі, які можна планувати (без completed/cancelled)."""
    completed = status_utils.to_db_status(models.TaskStatus.COMPLETED)
    cancelled = status_utils.to_db_status(models.TaskStatus.CANCELLED)
    tasks = db.query(models.Task).filter(~models.Task.status.in_([completed, cancelled])).all()
    return _normalize_tasks(tasks)


def replace_planned_tasks(db: Session, plan):
    """Замінити існуючий план новим (повністю)."""
    db.query(models.PlannedTask).delete()
    for item in plan.tasks:
        db.add(
            models.PlannedTask(
                task_id=item.task_id,
                priority_rank=item.priority_rank,
                duration_minutes=item.duration_minutes,
                planned_start=item.planned_start,
                planned_end=item.planned_end,
                note=item.note,
            )
        )
    db.commit()


def get_planned_tasks(db: Session):
    """Отримати сплановані задачі з деталями."""
    rows = (
        db.query(models.PlannedTask, models.Task)
        .join(models.Task, models.Task.id == models.PlannedTask.task_id)
        .order_by(models.PlannedTask.priority_rank)
        .all()
    )

    result = []
    for plan_row, task in rows:
        normalized_task = _normalize_task(task)
        result.append({"plan": plan_row, "task": normalized_task})
    return result


def get_tasks_by_priority(db: Session, priority: int, skip: int = 0, limit: int = 100):
    """Отримати задачі за пріоритетом"""
    tasks = db.query(models.Task) \
        .filter(models.Task.priority == priority) \
        .order_by(desc(models.Task.created_at)) \
        .offset(skip).limit(limit).all()
    return _normalize_tasks(tasks)


def get_overdue_tasks(db: Session, skip: int = 0, limit: int = 100):
    """Отримати прострочені задачі"""
    completed_status = status_utils.to_db_status(models.TaskStatus.COMPLETED)
    tasks = db.query(models.Task) \
        .filter(and_(
        models.Task.deadline.isnot(None),
        models.Task.deadline < func.now(),
        models.Task.status != completed_status
    )) \
        .order_by(models.Task.deadline) \
        .offset(skip).limit(limit).all()
    return _normalize_tasks(tasks)


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

    allowed_statuses = [
        status_utils.to_db_status(models.TaskStatus.PENDING),
        status_utils.to_db_status(models.TaskStatus.IN_PROGRESS)
    ]

    tasks = db.query(models.Task) \
        .filter(
        and_(
            models.Task.status.in_(allowed_statuses),
            models.Task.deadline.isnot(None),
            models.Task.deadline >= start_date,
            models.Task.deadline <= end_date
        )
    ) \
        .order_by(models.Task.priority, models.Task.deadline) \
        .all()
    return _normalize_tasks(tasks)


# Додаткові CRUD функції
def get_tasks_by_status(db: Session, status: str, skip: int = 0, limit: int = 100):
    """Отримати задачі за статусом"""
    db_status = status_utils.to_db_status(status)
    tasks = db.query(models.Task) \
        .filter(models.Task.status == db_status) \
        .order_by(desc(models.Task.created_at)) \
        .offset(skip).limit(limit).all()
    return _normalize_tasks(tasks)


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

    normalized_status_stats = {
        status_utils.to_api_status(stat.status): stat.count for stat in status_stats
    }

    return {
        "total_tasks": total_tasks,
        "status_stats": normalized_status_stats,
        "priority_stats": {stat.priority: stat.count for stat in priority_stats}
    }
