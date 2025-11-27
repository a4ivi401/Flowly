# Flowly — AI-планувальник задач

FastAPI + React застосунок для управління особистими задачами з AI-оптимізацією розкладу через Gemini. Працює з MySQL, має окремий модуль планувальника і готовий UI на Vite/shadcn.

## Що вміє
- CRUD задач із пріоритетом, тривалістю та дедлайнами.
- Генерація оптимізованого плану дня через Gemini (fallback — детермінований порядок).
- React-інтерфейс із табами “Мої задачі” та “План на день”.
- Health-чек, тест БД, нормалізація легасі статусів.

## Стек
- Backend: FastAPI, SQLAlchemy, Pydantic v2, PyMySQL, Uvicorn.
- Планувальник: окремий модуль `backend/planing_engine` (Pydantic, Requests, Gemini API).
- Frontend: React 18, Vite, React Query, Tailwind + shadcn/ui, React Router.
- DB: MySQL 8.x.

## Структура репозиторію
- `backend/` — FastAPI-сервіс, підключення до MySQL, планувальник через `PlanningService`.
- `backend/planing_engine/` — правила планування, клієнт Gemini, юніт-тести.
- `frontend/` — Vite/React SPA.
- `docs/` — документація (огляд, backend, frontend, ops, API).
- `.env.example` — приклад налаштувань БД для бекенду.

## Швидкий старт (локально)
Передумови: Python 3.12+, Node 18+, MySQL 8.x, Gemini API key.

```bash
# 1) База та змінні
cp .env.example .env   # заповніть доступи до MySQL
export GEMINI_API_KEY=<your_key>  # або додайте у backend/.env

# 2) Backend
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn backend.main:app --reload

# 3) Frontend (у новій консолі)
cd frontend
cp .env.example .env   # за потреби оновіть VITE_API_BASE_URL
npm install
npm run dev
```
Перевірка: `GET http://localhost:8000/health`, UI зазвичай на `http://localhost:5173`.

## Ключові змінні середовища
- Backend БД: `BACKEND_DB_HOST`, `BACKEND_DB_PORT`, `BACKEND_DB_USER`, `BACKEND_DB_PASSWORD`, `BACKEND_DB_NAME`.
- Планувальник: `GEMINI_API_KEY` (обовʼязково), `GEMINI_MODEL` (опційно).
- Frontend: `VITE_API_BASE_URL` (адреса бекенду; дефолт — `/api` або `http://localhost:8000`).

## Корисні команди
- Backend тести планувальника: `python -m unittest discover -s planing_engine/tests` (з каталогу `backend`).
- Frontend: `npm run lint`, `npm run build`, `npm run preview`.

## Документація
- Огляд, бекенд, фронтенд, операції: `docs/README.md`.
- API/ендпоінти: `docs/API.md`, `docs/ENDPOINTS.md`.
- Підключення до БД: `docs/database_connect_docs.md`.
- Алгоритм планування: `backend/planing_engine/README.md` та `backend/planing_engine/rules.md`.

## Виробничі нотатки
- Обмежте CORS у `backend/main.py` під свої домени.
- Зберігайте `GEMINI_API_KEY` у менеджері секретів, не в репозиторії.
- Збирайте фронтенд (`npm run build`) і сервитьте статичні файли за проксі до бекенду.
