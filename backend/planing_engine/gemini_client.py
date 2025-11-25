import json
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable, List, Optional

import requests
from dotenv import load_dotenv

from planing_engine.models import Task

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

GEMINI_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"


@dataclass
class PlanItem:
    task_id: int
    priority_rank: int
    planned_start: Optional[datetime]
    planned_end: Optional[datetime]
    duration_minutes: Optional[int]
    note: Optional[str] = None


@dataclass
class GeminiPlan:
    plan_generated_at: datetime
    timezone: str
    tasks: List[PlanItem]


class GeminiPlannerError(Exception):
    """Raised when Gemini planning fails or response is invalid."""


class GeminiPlanner:
    """
    Thin wrapper around Gemini API for daily planning.
    Expects JSON-only responses for predictable parsing.
    """

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise GeminiPlannerError("GEMINI_API_KEY is not set")
        # Дозволяємо задавати модель через env; дефолт — актуальний -latest
        self.model = model or os.getenv("GEMINI_MODEL") or "gemini-1.5-flash-latest"

    def _build_prompt(
        self,
        tasks: Iterable[Task],
        timezone: str,
        workday_hours: int,
        long_break_minutes: int,
        short_break_minutes: int,
    ) -> str:
        """Compose a deterministic prompt for Gemini."""
        task_dump = []
        for task in tasks:
            task_dump.append(
                {
                    "id": task.id,
                    "title": task.title,
                    "description": task.description or "",
                    "priority": task.priority,
                    "duration_minutes": task.duration_minutes,
                    "deadline": task.deadline.isoformat() if task.deadline else None,
                    "status": task.status,
                    "is_blocked": task.is_blocked,
                    "is_pinned": task.is_pinned,
                    "tags": task.tags,
                    "start_date": task.start_date.isoformat() if task.start_date else None,
                }
            )

        return (
            "You are an AI scheduling assistant. Build an optimized plan for the next workday.\n"
            f"Timezone: {timezone}.\n"
            f"Workday hours total: {workday_hours}.\n"
            f"Long break (lunch) minutes: {long_break_minutes}.\n"
            f"Short break minutes: {short_break_minutes}.\n"
            "Rules:\n"
            "- Prefer pinned tasks first.\n"
            "- Respect deadlines; overdue and today deadlines first.\n"
            "- Sort by priority high > medium > low.\n"
            "- Fit into the available workday and include breaks appropriately; skip blocked tasks.\n"
            "- Provide clear ordering via `priority_rank` starting from 1.\n"
            "- Use ISO 8601 timestamps with timezone if you set start/end times.\n\n"
            "Input JSON with tasks:\n"
            f"{json.dumps(task_dump, ensure_ascii=False, indent=2)}\n\n"
            "Return ONLY compact JSON in this schema (no extra text):\n"
            "{\n"
            '  \"plan_generated_at\": \"<ISO datetime>\",\n'
            '  \"timezone\": \"<tz like UTC or Europe/Kyiv>\",\n'
            "  \"tasks\": [\n"
            "    {\n"
            "      \"task_id\": <int>,\n"
            "      \"priority_rank\": <int starting from 1>,\n"
            "      \"duration_minutes\": <int>,\n"
            "      \"planned_start\": \"<ISO datetime or null>\",\n"
            "      \"planned_end\": \"<ISO datetime or null>\",\n"
            "      \"note\": \"<optional comment>\"\n"
            "    }\n"
            "  ]\n"
            "}"
        )

    def _parse_plan(self, raw_text: str) -> GeminiPlan:
        def _parse_dt(value: Optional[str]) -> Optional[datetime]:
            if value is None:
                return None
            try:
                return datetime.fromisoformat(value.replace("Z", "+00:00"))
            except Exception as exc:  # pragma: no cover - defensive
                raise GeminiPlannerError(f"Невалідний datetime формат: {value}") from exc

        try:
            data = json.loads(raw_text)
        except json.JSONDecodeError as exc:
            raise GeminiPlannerError(f"Gemini returned non-JSON response: {exc}") from exc

        try:
            generated_at = _parse_dt(data.get("plan_generated_at")) or datetime.utcnow()
            timezone = data.get("timezone") or "UTC"
            plan_items = []
            for item in data.get("tasks", []):
                plan_items.append(
                    PlanItem(
                        task_id=int(item["task_id"]),
                        priority_rank=int(item["priority_rank"]),
                        duration_minutes=item.get("duration_minutes"),
                        planned_start=_parse_dt(item.get("planned_start")),
                        planned_end=_parse_dt(item.get("planned_end")),
                        note=item.get("note"),
                    )
                )
            return GeminiPlan(plan_generated_at=generated_at, timezone=timezone, tasks=plan_items)
        except Exception as exc:
            raise GeminiPlannerError(f"Failed to parse Gemini plan: {exc}") from exc

    def generate_plan(
        self,
        tasks: Iterable[Task],
        timezone: str = "UTC",
        workday_hours: int = 8,
        long_break_minutes: int = 60,
        short_break_minutes: int = 15,
    ) -> GeminiPlan:
        """
        Call Gemini to generate a plan.
        """
        prompt = self._build_prompt(
            tasks,
            timezone=timezone,
            workday_hours=workday_hours,
            long_break_minutes=long_break_minutes,
            short_break_minutes=short_break_minutes,
        )
        url = GEMINI_ENDPOINT.format(model=self.model)
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        try:
            response = requests.post(
                url,
                params={"key": self.api_key},
                json=payload,
                timeout=30,
                headers={"Content-Type": "application/json"},
            )
        except requests.RequestException as exc:
            raise GeminiPlannerError(f"Gemini request failed: {exc}") from exc

        if not response.ok:
            raise GeminiPlannerError(
                f"Gemini responded with {response.status_code}: {response.text}"
            )

        data = response.json()
        text = (
            data.get("candidates", [{}])[0]
            .get("content", {})
            .get("parts", [{}])[0]
            .get("text")
        )
        if not text:
            raise GeminiPlannerError("Gemini response missing text content")

        return self._parse_plan(text)
