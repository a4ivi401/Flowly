# Архітектура Flowly

## Огляд
Flowly — це AI-асистент для управління особистими задачами. Стек: FastAPI + SQLAlchemy + MySQL на бекенді, окремий модуль планування з інтеграцією Gemini, фронтенд на React/Vite з shadcn/ui.

## Основні компоненти
- `backend/` — FastAPI-сервіс: CRUD по задачах, ендпоінти планування, підключення до MySQL, логування у `backend/logs/*`.
- `backend/planing_engine/` — окремий модуль з правилами планування дня та клієнтом Gemini. Використовується бекендом через `app.planning_service.PlanningService`.
- `frontend/` — SPA на React/Vite. Працює з API через `src/api/client.ts`, будує UI задач і плану.
- `docs/` — функціональна документація (API, БД, окремі гайдлайни).

## Потік даних
1. **CRUD задач:** фронтенд викликає `/tasks` ендпоінти → FastAPI звертається до MySQL через SQLAlchemy → відповіді нормалізуються (`status_utils`) і віддаються клієнту.
2. **Планування:**
   - `/plan/today` бере задачі, що можна планувати (`crud.get_plannable_tasks`), мапить їх у доменні моделі планувальника.
   - `planing_engine.generate_plan` викликає Gemini (або застосовує детермінований fallback).
   - Результат зберігається у таблиці `planned_tasks` і повертається у відповідь.
   - `/plan/today/optimized` віддає останній збережений план.
3. **Стан/статуси:** у БД зберігаються легасі статуси (`todo/done`), у API — канонічні (`pending/in_progress/completed/cancelled`). Відповідність описано в `app/status_utils.py`.

## Конфігурація та секрети
- Базові змінні для БД: див. `.env.example` та `docs/BACKEND.md`.
- Планувальник потребує `GEMINI_API_KEY` (і опційно `GEMINI_MODEL`) у `backend/.env` або `backend/planing_engine/.env`.
- Фронтенд читає `VITE_API_BASE_URL` (`frontend/.env`).

## Сторонні залежності
- Backend: FastAPI, SQLAlchemy, PyMySQL, Pydantic v2, Requests, python-dotenv.
- Планувальник: Pydantic, Requests, python-dateutil, dotenv.
- Frontend: React 18, Vite 5, React Query, react-hook-form, zod, Tailwind/shadcn-ui, react-router-dom.

## Що ще почитати
- API деталі: `docs/API.md`, `docs/ENDPOINTS.md`.
- БД: `docs/database_connect_docs.md`.
- Алгоритм планування: `backend/planing_engine/README.md` та `backend/planing_engine/rules.md`.
