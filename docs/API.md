# Flowly API — документація для фронтенду

Документ описує, як фронтенду інтегруватися з бекендом Flowly (FastAPI + MySQL). Усі приклади наведено для локального запуску; змінюйте базову адресу залежно від середовища.

## Швидкий старт
- Стек: FastAPI, SQLAlchemy, MySQL.
- Базовий URL (локально): `http://localhost:8000`.
- Запуск: `uvicorn backend.main:app --reload`.
- Вимоги: Python 3.12+, активна MySQL. Депенденсі див. `backend/requirements.txt`.
- Таблиці створюються автоматично на старті (`create_tables()` у `backend/app/database.py`).

### Змінні середовища (`.env`)
```
BACKEND_DB_HOST=localhost
BACKEND_DB_PORT=3306
BACKEND_DB_USER=root
BACKEND_DB_PASSWORD=your_password
BACKEND_DB_NAME=ai_time_manager
```
За замовчуванням використовується MySQL, підключення логуються у консоль (включено `echo=True`).

### Перевірка доступності
- `GET /health` — статус сервера та БД, повертає `{ status, database, mysql_version, message }`, 500 при проблемах з БД.
- `GET /` — вітальне повідомлення та версія API.
- `GET /test-db` — простий запит до БД: `{ status, current_time, tables_in_database, message }`.

## Модель даних Task
Таблиця `tasks` (`backend/app/models.py`):
- `id` (int) — первинний ключ.
- `title` (str, 1–255) — назва, обовʼязкове.
- `description` (str | null) — опис.
- `priority` (int, 1–5) — 1 = найвищий.
- `duration_minutes` (int | null, >=1) — тривалість у хвилинах.
- `deadline` (datetime | null) — дедлайн, ISO 8601.
- `status` (enum) — `pending | in_progress | completed | cancelled`.
- `created_at`, `updated_at` — серверний час (`func.now()`).

### Валідація (Pydantic, `backend/app/schemas.py`)
- `title`: обовʼязкове, 1–255 символів.
- `priority`: від 1 до 5.
- `duration_minutes`: якщо передано, то >= 1.
- `deadline`: ISO datetime.
- `status`: одне зі значень `TaskStatus`.

## Заголовки та формати
- Контент: `Content-Type: application/json`.
- Час: ISO 8601, напр. `2024-05-01T12:00:00Z`.
- Авторизація: немає (усі ендпоінти публічні).

## Огляд ендпоінтів
| Метод | Шлях | Призначення |
| --- | --- | --- |
| GET | `/health` | Перевірка сервера і БД |
| GET | `/` | Вітання + версія API |
| GET | `/test-db` | Тест БД (поточний час, кількість таблиць) |
| POST | `/tasks/` | Створити задачу |
| GET | `/tasks/` | Список задач з фільтрами `status`, `priority`, пагінація `skip`, `limit` |
| GET | `/tasks/{task_id}` | Отримати задачу за ID |
| PUT | `/tasks/{task_id}` | Оновити задачу (часткове) |
| DELETE | `/tasks/{task_id}` | Видалити задачу |
| GET | `/tasks/priority/{priority}` | Задачі з конкретним пріоритетом (1–5) |
| GET | `/tasks/status/overdue` | Прострочені задачі (дедлайн у минулому, не `completed`) |

## Деталі ендпоінтів

### POST `/tasks/`
Створити нову задачу.
- Тіло:
```json
{
  "title": "Write docs",
  "description": "Backend → frontend guide",
  "priority": 2,
  "duration_minutes": 60,
  "deadline": "2024-05-01T12:00:00Z",
  "status": "pending"
}
```
- Відповідь 200:
```json
{
  "id": 42,
  "title": "Write docs",
  "description": "Backend → frontend guide",
  "priority": 2,
  "duration_minutes": 60,
  "deadline": "2024-05-01T12:00:00Z",
  "status": "pending",
  "created_at": "2024-04-25T10:00:00Z",
  "updated_at": "2024-04-25T10:00:00Z"
}
```

### GET `/tasks/`
Список задач з фільтрами та пагінацією.
- Параметри: `skip` (int, default 0), `limit` (int, default 100), `status` (optional), `priority` (optional).
- Сортування: `created_at` DESC.
- Відповідь 200: масив Task.
- Приклад: `/tasks/?status=in_progress&priority=1&skip=0&limit=20`.

### GET `/tasks/{task_id}`
- Відповідь 200: Task.
- 404, якщо не знайдено.

### PUT `/tasks/{task_id}`
Часткове оновлення будь-яких полів (`title`, `description`, `priority`, `duration_minutes`, `deadline`, `status`).
- Тіло (приклад): `{ "status": "completed", "priority": 3 }`
- Відповідь 200: оновлений Task.
- 404, якщо не знайдено.

### DELETE `/tasks/{task_id}`
- Відповідь 200: `{ "ok": true }`
- 404, якщо не знайдено.

### GET `/tasks/priority/{priority}`
- Аргумент `priority`: 1–5, інакше 400.
- Параметри: `skip`, `limit`.
- Сортування: `created_at` DESC.
- Відповідь: масив Task.

### GET `/tasks/status/overdue`
- Логіка: `deadline < now()` і `status != completed`.
- Параметри: `skip`, `limit`.
- Сортування: `deadline` ASC.
- Відповідь: масив Task.

## Коди відповіді та помилки
- 200 — успішно (повертаються дані або `{ "ok": true }` для DELETE).
- 400 — некоректні параметри (наприклад, пріоритет не в діапазоні 1–5).
- 404 — ресурс не знайдено (`task_id` відсутній).
- 500 — проблеми з БД або інші неочікувані помилки (деталь у `detail`).

## Приклади запитів (curl / fetch)

```bash
# Список задач зі статусом in_progress
curl "http://localhost:8000/tasks/?status=in_progress&skip=0&limit=20"

# Створити задачу
curl -X POST "http://localhost:8000/tasks/" \
  -H "Content-Type: application/json" \
  -d '{"title":"Focus block","description":"Deep work on feature X","priority":1,"duration_minutes":90,"deadline":"2024-05-02T09:00:00Z","status":"pending"}'

# Оновити статус
curl -X PUT "http://localhost:8000/tasks/42" \
  -H "Content-Type: application/json" \
  -d '{"status":"completed"}'

# Видалити задачу
curl -X DELETE "http://localhost:8000/tasks/42"
```

```ts
// fetch: отримати задачі
const res = await fetch("/tasks/?status=in_progress&skip=0&limit=20");
const tasks = await res.json();

// axios: створити задачу
await axios.post("/tasks/", {
  title: "Focus block",
  description: "Deep work on feature X",
  priority: 1,
  duration_minutes: 90,
  deadline: "2024-05-02T09:00:00Z",
  status: "pending",
});
```

## Особливості для фронтенду
- **CORS**: не налаштовано явно; при роздільному походженні фронта і бекенда додайте CORS middleware або проксі.
- **Час/таймзона**: використовуйте ISO 8601; бекенд порівнює дедлайни з серверним часом (`func.now()`).
- **Перерахування статусів**: приймає лише `pending | in_progress | completed | cancelled`.
- **Сортування**: `/tasks/` — за `created_at` DESC; `/tasks/status/overdue` — за `deadline` ASC.
- **Поля з null**: `description`, `duration_minutes`, `deadline` можуть бути `null`; враховуйте при рендері.
- **Відсутність авторизації**: усі ендпоінти відкриті, додайте захист/токен при продакшн-деплої.

## Діагностика
- Увімкнено логування SQL (`echo=True` у `create_engine`).
- Стартап виводить повідомлення про підключення до БД та створення таблиць.
- Для швидкої перевірки роботи БД використовуйте `GET /health` або `GET /test-db`.

## Запуск локально (рекомендація)
1) Створіть `.env` з параметрами підключення до MySQL.  
2) Встановіть залежності: `pip install -r backend/requirements.txt`.  
3) Запустіть: `uvicorn backend.main:app --reload`.  
4) Перевірте: `curl http://localhost:8000/health`.  

Готово: можна викликати ендпоінти з фронтенду.
