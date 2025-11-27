# Frontend (React/Vite)

## Призначення
Односторінковий застосунок, що працює з API Flowly: управління задачами та відображення оптимізованого плану на день.

## Вимоги
- Node.js 18+ (nvm рекомендовано)
- npm (або pnpm/yarn за бажанням)

## Змінні середовища
`frontend/.env.example`:
```
VITE_API_BASE_URL=http://localhost:8000
```
Якщо бекенд і фронтенд розгорнуті на різних доменах/портах, вкажіть повний URL. Значення обрізає кінцевий слеш.

## Установка та запуск
```bash
cd frontend
npm install
npm run dev         # дев-сервер з HMR
npm run build       # продакшн-збірка у dist/
npm run preview     # передпрод перегляд збірки
npm run lint        # ESLint
```

## Структура
- `src/App.tsx` — підключає React Router, React Query та провайдери тултіпів/тостів.
- `src/api/client.ts` — клієнт для бекенд-ендпоінтів (CRUD задач, планування, health).
- Сторінки:
  - `pages/Index.tsx` — лендинг з описом продукту.
  - `pages/TasksPage.tsx` — головний інтерфейс задач і плану (таб "Мої задачі" + таб "План на день").
  - `pages/NotFound.tsx` — 404.
- Компоненти:
  - `components/TaskForm.tsx` — створення/редагування задач (react-hook-form + zod).
  - `components/home/*`, `components/layout/Header.tsx` — лендинг.
  - `components/ui/*` — бібліотека shadcn/ui.
- Хуки: `hooks/use-toast.ts`, `hooks/use-mobile.tsx`.

## Інтеграція з API
- Базовий URL береться з `VITE_API_BASE_URL`.
- React Query кешує запити `tasks` та `todayPlan`.
- Підтримані операції: створення/редагування/видалення задач, завершення задачі, виклик `/plan/today`, перегляд `/plan/today/optimized`.

## UI особливості
- Таби для задач та плану; картки задач із відображенням пріоритету, дедлайнів, тривалості.
- Діалоги для перегляду/редагування/видалення, штори (Sheet) для форми.
- Тости (`sonner` + кастомний `use-toast`) для зворотного зв’язку.

## Деплой
- Збірка (`npm run build`) генерує статичний `dist/`.
- Для продакшена проксійть запити `/tasks`, `/plan/*` на бекенд або задайте повний `VITE_API_BASE_URL`.
- Переконайтесь, що CORS на бекенді дозволяє домен фронтенду.
