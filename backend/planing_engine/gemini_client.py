import json
import logging
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable, List, Optional

import requests
from dotenv import load_dotenv

from planing_engine.models import Task

# Load local .env if present
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
    Wrapper around Gemini API for daily planning.
    Expects JSON-only responses for predictable parsing.
    """

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise GeminiPlannerError("GEMINI_API_KEY is not set")
        raw_model = model or os.getenv("GEMINI_MODEL") or "gemini-2.5-flash"
        # ensure we don't end up with models/models/...
        self.model = raw_model.removeprefix("models/")

    def _build_prompt(
        self,
        tasks: Iterable[Task],
        timezone: str,
        workday_hours: int,
        long_break_minutes: int,
        short_break_minutes: int,
    ) -> str:
        """Compose deterministic prompt for Gemini."""
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
            "You are an expert time-management assistant. Build an optimized daily plan using good timeboxing.\n"
            f"Timezone: {timezone}. Workday hours: {workday_hours}. Long break: {long_break_minutes} minutes. Short break: {short_break_minutes} minutes.\n"
            "Rules: pinned tasks first; overdue/today deadlines first; priority high>medium>low; skip blocked; ensure total duration fits the day including breaks; add short notes only if useful.\n"
            "Input tasks JSON:\n"
            f"{json.dumps(task_dump, ensure_ascii=False, indent=2)}\n\n"
            "Return ONLY JSON in this exact schema (no extra text):\n"
            "{\n"
            '  \"plan_generated_at\": \"<ISO datetime>\",\n'
            '  \"timezone\": \"<string>\",\n'
            "  \"tasks\": [\n"
            "    {\n"
            "      \"task_id\": <int>,\n"
            "      \"priority_rank\": <int starting at 1>,\n"
            "      \"duration_minutes\": <int>,\n"
            "      \"planned_start\": \"<ISO datetime or null>\",\n"
            "      \"planned_end\": \"<ISO datetime or null>\",\n"
            "      \"note\": \"<optional string>\"\n"
            "    }\n"
            "  ]\n"
            "}"
        )

    def _parse_plan(self, raw_text: str) -> GeminiPlan:
        logger = logging.getLogger(__name__)

        def _extract_json(text: str) -> dict:
            try:
                return json.loads(text)
            except json.JSONDecodeError:
                # Спроба вирізати перший JSON-блок
                start = text.find("{")
                end = text.rfind("}")
                if start != -1 and end != -1 and end > start:
                    snippet = text[start : end + 1]
                    return json.loads(snippet)
                raise

        def _parse_dt(value: Optional[str]) -> Optional[datetime]:
            if value is None:
                return None
            try:
                return datetime.fromisoformat(value.replace("Z", "+00:00"))
            except Exception as exc:
                raise GeminiPlannerError(f"Invalid datetime format: {value}") from exc

        try:
            logger.debug("Gemini raw text: %s", raw_text)
            data = _extract_json(raw_text)
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
            if not plan_items:
                raise GeminiPlannerError("Gemini plan is empty")
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
        """Call Gemini to generate a plan."""
        logger = logging.getLogger(__name__)
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

        logger.info("Gemini request ok: model=%s status=%s", self.model, response.status_code)
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
