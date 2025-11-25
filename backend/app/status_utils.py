from typing import Iterable, List, Optional
from enum import Enum

from app.models import TaskStatus

# В БД збережені старі значення ('todo', 'done'), але в API хочемо працювати з новими ('pending', 'completed').
LEGACY_TO_CANONICAL = {
    "todo": TaskStatus.PENDING.value,
    "done": TaskStatus.COMPLETED.value,
}

CANONICAL_TO_DB = {
    TaskStatus.PENDING.value: "todo",
    TaskStatus.IN_PROGRESS.value: "in_progress",
    TaskStatus.COMPLETED.value: "done",
    TaskStatus.CANCELLED.value: "cancelled",
}


def _as_str(value: Optional[str | TaskStatus]) -> Optional[str]:
    if value is None:
        return None
    # Підтримуємо будь-які enum (і з моделей, і з схем)
    if isinstance(value, Enum):
        return str(value.value)
    return str(value)


def to_api_status(value: Optional[str | TaskStatus]) -> str:
    """Повертає канонічний статус для API (pending/in_progress/completed/cancelled)."""
    raw = _as_str(value)
    if not raw:
        return TaskStatus.PENDING.value

    normalized = raw.lower()
    return LEGACY_TO_CANONICAL.get(normalized, normalized)


def to_db_status(value: Optional[str | TaskStatus]) -> str:
    """Перетворює канонічний або легасі статус у значення, що підтримає БД."""
    raw = _as_str(value)
    if not raw:
        return CANONICAL_TO_DB[TaskStatus.PENDING.value]

    normalized = raw.lower()
    canonical = LEGACY_TO_CANONICAL.get(normalized, normalized)
    return CANONICAL_TO_DB.get(canonical, canonical)


def normalize_task_status(task) -> Optional[object]:
    """Повертає task з канонічним статусом (in-place)."""
    if task is None or not hasattr(task, "status"):
        return task

    task.status = to_api_status(task.status)
    return task


def normalize_tasks(tasks: Iterable[object]) -> List[object]:
    """Нормалізує статус для колекції задач перед поверненням у API."""
    return [normalize_task_status(task) for task in tasks]
