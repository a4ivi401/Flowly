from sqlalchemy import Column, Integer, String, Text, Enum, DateTime, SmallInteger
from sqlalchemy.sql import func
from app.database import Base
import enum

# Enum для статусів задач
class TaskStatus(enum.Enum):
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
    status = Column(
        Enum(TaskStatus),
        default=TaskStatus.PENDING,
        nullable=False,
        index=True
    )
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    def __repr__(self):
        return f"<Task(id={self.id}, title='{self.title}', status='{self.status}')>"