from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from enum import Enum

class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255, description="Назва задачі")
    description: Optional[str] = Field(None, description="Опис задачі")
    priority: int = Field(1, ge=1, le=5, description="Пріоритет (1-5, де 1 - найвищий)")
    duration_minutes: Optional[int] = Field(None, ge=1, description="Тривалість у хвилинах")
    deadline: Optional[datetime] = Field(None, description="Дедлайн")
    status: TaskStatus = Field(TaskStatus.PENDING, description="Статус задачі")

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    priority: Optional[int] = Field(None, ge=1, le=5)
    duration_minutes: Optional[int] = Field(None, ge=1)
    deadline: Optional[datetime] = None
    status: Optional[TaskStatus] = None

class Task(TaskBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # orm_mode в Pydantic v2