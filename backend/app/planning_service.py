import os
from pathlib import Path
from typing import List

from fastapi import HTTPException
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from datetime import datetime

from planing_engine import generate_plan
from planing_engine.models import Task as PlanningTask, Priority, Status
from planing_engine.gemini_client import GeminiPlannerError

from app import crud, models, status_utils, schemas


class PlanningService:
    """Coordinates planning workflow with Gemini and DB persistence."""

    def __init__(self, db: Session):
        self.db = db
        base_dir = Path(__file__).resolve().parents[1]  # backend/
        for env_path in [
            base_dir / ".env",
            base_dir / "planing_engine" / ".env",
            base_dir.parent / "planing_engine" / ".env",
        ]:
            if env_path.exists():
                load_dotenv(env_path, override=False)
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise HTTPException(status_code=500, detail="GEMINI_API_KEY is not configured")

    def _priority_from_db(self, value: int) -> Priority:
        if value is None:
            return Priority.MEDIUM
        if value <= 2:
            return Priority.HIGH
        if value == 3:
            return Priority.MEDIUM
        return Priority.LOW

    def _status_from_db(self, value: str) -> Status:
        canonical = status_utils.to_api_status(value)
        if canonical == models.TaskStatus.COMPLETED.value:
            return Status.DONE
        if canonical == models.TaskStatus.IN_PROGRESS.value:
            return Status.IN_PROGRESS
        return Status.TODO

    def _to_planning_tasks(self, tasks: List[models.Task]) -> List[PlanningTask]:
        planning_tasks: List[PlanningTask] = []
        for task in tasks:
            planning_tasks.append(
                PlanningTask(
                    id=task.id,
                    title=task.title,
                    description=task.description,
                    priority=self._priority_from_db(task.priority).value,
                    duration_minutes=task.duration_minutes or 30,
                    deadline=task.deadline.date() if task.deadline else None,
                    status=self._status_from_db(task.status).value,
                    created_at=task.created_at,
                    is_blocked=False,
                    start_date=task.created_at.date() if task.created_at else None,
                    tags=[],
                    is_pinned=False,
                )
            )
        return planning_tasks

    def run(self, params: schemas.PlanningRequest) -> schemas.PlanningResponse:
        tasks = crud.get_plannable_tasks(self.db)
        if not tasks:
            return schemas.PlanningResponse(generated_at=None, timezone=params.timezone, tasks=[])

        planning_tasks = self._to_planning_tasks(tasks)
        try:
            plan = generate_plan(
                planning_tasks,
                api_key=self.api_key,
                timezone=params.timezone,
                workday_hours=params.workday_hours,
                long_break_minutes=params.long_break_minutes,
                short_break_minutes=params.short_break_minutes,
            )
        except GeminiPlannerError as exc:
            raise HTTPException(status_code=502, detail=f"Gemini planning failed: {exc}") from exc

        # Ігноруємо plan_generated_at від Gemini та фіксуємо поточний час сервера
        plan.plan_generated_at = datetime.utcnow()

        crud.replace_planned_tasks(self.db, plan)

        stored_plan = crud.get_planned_tasks(self.db)
        response_items: List[schemas.PlannedTaskItem] = []
        for item in stored_plan:
            plan_row = item["plan"]
            task = item["task"]
            response_items.append(
                schemas.PlannedTaskItem(
                    task_id=plan_row.task_id,
                    priority_rank=plan_row.priority_rank,
                    planned_start=plan_row.planned_start,
                    planned_end=plan_row.planned_end,
                    duration_minutes=plan_row.duration_minutes,
                    note=plan_row.note,
                    task=schemas.Task.model_validate(task),
                )
            )

        return schemas.PlanningResponse(
            generated_at=plan.plan_generated_at,
            timezone=plan.timezone,
            tasks=response_items,
        )
