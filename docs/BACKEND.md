# Backend (FastAPI + MySQL)

## Призначення
HTTP API для задач та планування дня. Використовує FastAPI, SQLAlchemy та MySQL; інтегрується з Gemini через внутрішній модуль `planing_engine`.

## Вимоги
- Python 3.12+
- MySQL 8.x (база `ai_time_manager`)
- Віртуальне середовище (рекомендовано)
- `GEMINI_API_KEY` для роботи планувальника

## Змінні середовища
Приклад у корені: `.env.example`. Ключові значення:
```
BACKEND_DB_HOST=127.0.0.1
BACKEND_DB_PORT=3306
BACKEND_DB_USER=ai_user
BACKEND_DB_PASSWORD=ai_password
BACKEND_DB_NAME=ai_time_manager

# Планувальник (Gemini)
GEMINI_API_KEY=<your_key>
GEMINI_MODEL=gemini-2.5-flash   # опційно
```
Файли перевірки: `backend/.env`, `backend/planing_engine/.env` (завантажуються автоматично у `PlanningService`).

## Установка залежностей
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # або Scripts\\activate у Windows
pip install -r requirements.txt
```

## Запуск локально
```bash
# у віртуальному середовищі
uvicorn backend.main:app --reload
```
- Старт ініціалізує підключення до БД, створює таблиці (`tasks`, `planned_tasks`).
- Логування пишеться у `backend/logs/flowly_<timestamp>_running.log`.
- CORS зараз відкритий (`allow_origins=["*"]`); для продакшена вкажіть конкретні домени у `main.py`.

## Модулі
- `backend/main.py` — FastAPI додаток, реєструє ендпоінти.
- `backend/app/`:
  - `models.py` — ORM-моделі `Task`, `PlannedTask`, енум `TaskStatus`.
  - `schemas.py` — Pydantic-схеми для API.
  - `crud.py` — операції з БД (CRUD, фільтри, плановані задачі).
  - `planning_service.py` — місток до `planing_engine` і Gemini.
  - `status_utils.py` — нормалізація статусів (легасі ↔ канонічні).
  - `database.py` — engine + session + create_tables.
- `backend/planing_engine/` — правила планування, клієнт Gemini, юніт-тести (див. окремий README).

## API
- Швидкий огляд: `docs/ENDPOINTS.md`.
- Детальний опис/приклади: `docs/API.md`.
- Health-чек: `GET /health`, базовий ping: `GET /`.

## Тестування
```bash
# Юніт-тести планувальника
cd backend
python -m unittest discover -s planing_engine/tests
```
(залежності планувальника беруться з `backend/planing_engine/requirements.txt`, вони вже перекриваються основним `requirements.txt`).

## Типові проблеми
- **Немає `GEMINI_API_KEY`:** `/plan/today` повертає 500. Додайте ключ у `.env`.
- **Помилки MySQL:** перевірте доступи та назву бази, переконайтесь у підтримці `pymysql`.
- **Порожній `planned_tasks`:** таблиця створюється автоматично; при видаленні задач `crud.delete_task` чистить зв’язки.
