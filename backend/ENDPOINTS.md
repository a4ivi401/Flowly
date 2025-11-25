# Flowly Backend API (FastAPI)

Базова URL: `http://<host>:8000`

## Service/Health
- `GET /` – простий ping сервера, повертає повідомлення та версію.
- `GET /health` – перевірка роботи API та БД; повертає статус, підключення до БД, версію MySQL.
- `GET /test-db` – тестовий запит до БД (поточний час, кількість таблиць).

## Planning
- `POST /plan/today`  
  Запускає планування через Gemini і зберігає впорядкований план у `planned_tasks`.  
  Тіло (JSON, усі поля опційні):
  ```json
  {
    "timezone": "Europe/Kyiv",
    "workday_hours": 8,
    "long_break_minutes": 60,
    "short_break_minutes": 15
  }
  ```
  Відповідь `200 OK`:
  ```json
  {
    "generated_at": "<ISO datetime (серверний час)>",
    "timezone": "Europe/Kyiv",
    "tasks": [
      {
        "task_id": 7,
        "priority_rank": 1,
        "planned_start": "2025-11-25T09:00:00",
        "planned_end": "2025-11-25T09:30:00",
        "duration_minutes": 30,
        "note": null,
        "task": {
          "id": 7,
          "title": "...",
          "description": "...",
          "priority": 2,
          "duration_minutes": 30,
          "deadline": "...",
          "status": "pending",
          "created_at": "...",
          "updated_at": "..."
        }
      }
    ]
  }
  ```
  Помилки: `500` (нема `GEMINI_API_KEY`), `502` (помилка виклику Gemini).

## Tasks CRUD
- `POST /tasks/` – створити задачу. Тіло `TaskCreate`:
  ```json
  {
    "title": "Task title",
    "description": "Optional",
    "priority": 1,
    "duration_minutes": 30,
    "deadline": "2025-11-30T12:00:00",
    "status": "pending"
  }
  ```
- `GET /tasks/` – список задач, опційні query `skip`, `limit`, `status`, `priority`. Повертає впорядковано за планом (якщо є), інакше за датою створення.
- `GET /tasks/{task_id}` – отримати задачу.
- `PUT /tasks/{task_id}` – оновити задачу (тіло `TaskUpdate`, усі поля опційні).
- `DELETE /tasks/{task_id}` – видалити задачу.
- `GET /tasks/priority/{priority}` – задачі за пріоритетом.
- `GET /tasks/status/overdue` – прострочені задачі (дедлайн < now і статус не completed).

## Статуси/пріоритети
- `status`: `pending`, `in_progress`, `completed`, `cancelled`, а також легасі `todo`, `done` (нормалізуються).
- `priority`: числа 1–5 (1 = найвищий) у БД; у планері приводяться до high/medium/low.
