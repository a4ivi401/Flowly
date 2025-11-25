from sqlalchemy import Column, Integer, String, Text, DateTime, SmallInteger, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum

# Enum для статусів задач (канонічні значення для API)
class TaskStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    priority = Column(SmallInteger, default=1, index=True)  # 1-5, де 1 - найвищий
    duration_minutes = Column(Integer, nullable=True)  # Тривалість у хвилинах
    deadline = Column(DateTime(timezone=True), nullable=True, index=True)
    # Базу тримаємо у спадкових статусах ('todo', 'done' тощо), а на рівні API віддаємо канонічні значення
    status = Column(String(50), default="todo", nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    def __repr__(self):
        return f"<Task(id={self.id}, title='{self.title}', status='{self.status}')>"


class PlannedTask(Base):
    __tablename__ = "planned_tasks"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), unique=True, nullable=False)
    priority_rank = Column(Integer, nullable=False, index=True)
    duration_minutes = Column(Integer, nullable=True)
    planned_start = Column(DateTime(timezone=True), nullable=True)
    planned_end = Column(DateTime(timezone=True), nullable=True)
    note = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    task = relationship("Task")
