from __future__ import annotations

import logging
from datetime import datetime
from typing import Iterable, List, Sequence

from planing_engine.gemini_client import GeminiPlan, GeminiPlanner, GeminiPlannerError, PlanItem
from planing_engine.models import Task


def _validate_plan(plan: GeminiPlan, tasks: Sequence[Task]) -> GeminiPlan:
    """Validate Gemini output against known tasks."""
    known_ids = {task.id for task in tasks}
    seen_ranks = set()
    valid_items = []

    for item in plan.tasks:
        if item.task_id not in known_ids:
            continue
        if item.priority_rank in seen_ranks:
            continue
        seen_ranks.add(item.priority_rank)
        valid_items.append(item)

    if not valid_items:
        raise GeminiPlannerError("Gemini план не містить жодної валідної задачі")

    plan.tasks = sorted(valid_items, key=lambda i: i.priority_rank)
    return plan


def _fallback_sort(tasks: Iterable[Task]) -> List[Task]:
    """Fallback deterministic ordering if Gemini fails."""
    def key(task: Task):
        priority_map = {"high": 3, "medium": 2, "low": 1}
        priority_value = -priority_map.get(str(task.priority), 0)
        created = task.created_at or datetime.max
        deadline_score = 0
        if task.deadline:
            deadline_score = 1
        pin_score = 0 if task.is_pinned else 1
        return (pin_score, -deadline_score, priority_value, created)

    return sorted(tasks, key=key)


def generate_plan(
    tasks: Sequence[Task],
    api_key: str,
    timezone: str = "UTC",
    workday_hours: int = 8,
    long_break_minutes: int = 60,
    short_break_minutes: int = 15,
) -> GeminiPlan:
    """
    Generate a plan using Gemini; fallback to deterministic ordering if Gemini fails.
    """
    logger = logging.getLogger(__name__)
    planner = GeminiPlanner(api_key=api_key)
    try:
        plan = planner.generate_plan(
            tasks,
            timezone=timezone,
            workday_hours=workday_hours,
            long_break_minutes=long_break_minutes,
            short_break_minutes=short_break_minutes,
        )
        return _validate_plan(plan, tasks)
    except GeminiPlannerError as exc:
        logger.warning("Gemini planning failed, using fallback: %s", exc)
        ordered = _fallback_sort(tasks)
        now = datetime.utcnow()
        plan_items = [
            PlanItem(
                task_id=task.id,
                priority_rank=idx,
                duration_minutes=task.duration_minutes,
                planned_start=None,
                planned_end=None,
                note="Fallback order without Gemini",
            )
            for idx, task in enumerate(ordered, 1)
        ]

        return GeminiPlan(
            plan_generated_at=now,
            timezone=timezone,
            tasks=plan_items,
        )
