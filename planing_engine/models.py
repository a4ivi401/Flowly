from datetime import date, datetime
from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field


class Priority(str, Enum):
    """Task priority levels"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Status(str, Enum):
    """Task status"""
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"


class Task(BaseModel):
    """
    Domain model for Task in Planning Engine.
    This is separate from DB model to keep planning logic independent.
    """
    id: int
    title: str
    description: Optional[str] = None
    priority: Priority
    duration_minutes: int = Field(default=30, ge=1)
    deadline: Optional[date] = None
    status: Status = Status.TODO
    created_at: datetime = Field(default_factory=datetime.now)
    start_date: Optional[date] = None
    is_blocked: bool = False
    tags: List[str] = Field(default_factory=list)
    is_pinned: bool = False

    class Config:
        use_enum_values = True

    def is_overdue(self, reference_date: date = None) -> bool:
        """Check if task is overdue"""
        if not self.deadline:
            return False
        ref = reference_date or date.today()
        return self.deadline < ref

    def is_due_today(self, reference_date: date = None) -> bool:
        """Check if task is due today"""
        if not self.deadline:
            return False
        ref = reference_date or date.today()
        return self.deadline == ref

    def is_urgent(self, reference_date: date = None) -> bool:
        """Check if task is overdue or due today"""
        return self.is_overdue(reference_date) or self.is_due_today(reference_date)