# Операції та запуск

## Швидкий сценарій локального запуску
1) Створіть `.env` у корені з параметрами БД (див. `.env.example`).  
2) Запустіть MySQL і створіть базу `ai_time_manager` під вказаним користувачем.  
3) Backend:
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn backend.main:app --reload
```
4) Frontend:
```bash
cd frontend
cp .env.example .env    # за потреби змініть VITE_API_BASE_URL
npm install
npm run dev
```
5) Перевірте `GET http://localhost:8000/health` і відкрийте `http://localhost:5173` (за замовчуванням Vite).

## Продакшн/стейджинг рекомендації
- Застосуйте пул підключень MySQL відповідно до навантаження (`engine` у `database.py` вже має pre_ping + recycle).
- Обмежте CORS у `backend/main.py` списком довірених доменів.
- Збережіть `GEMINI_API_KEY` у менеджері секретів (не в репозиторії).
- Підніміть бекенд за `uvicorn` або `gunicorn` за проксі (Nginx/Traefik).
- Фронтенд деплойте як статичний `dist/` на CDN/статичний хостинг; налаштуйте проксі `/api` або повний `VITE_API_BASE_URL`.

## Моніторинг та діагностика
- Health: `GET /health` (перевірка БД та версії MySQL).
- Тест БД: `GET /test-db`.
- Логи: `backend/logs/flowly_<timestamp>_running.log` + консоль.
- Планування: 500 без `GEMINI_API_KEY`; 502 при помилці Gemini (див. повідомлення).

## Обслуговування БД
- Таблиці створюються автоматично при старті (`create_tables()`), міграції не використовуються.
- При видаленні задач пов’язані записи `planned_tasks` чистяться автоматично.
- Індекси: `title`, `priority`, `status`, `deadline`, `created_at`, `planned_tasks.priority_rank`.

## Інше
- `docker-compose.yml` наразі порожній; за потреби додайте сервіси MySQL, бекенд, фронтенд.
- Періодично запускайте `npm run lint` для фронтенду та `python -m unittest ...` для планувальника.
