"""
# Planning Engine Rules

## 1. Input Scope (Фильтрация задач)
- Status: TODO или IN_PROGRESS
- Blocking: is_blocked = False
- Start Date: отсутствует или <= текущей даты
- Exclusions: теги 'someday', 'on_hold' игнорируются

## 2. Ranking Strategy (Сортировка)
Waterfall sort (по убыванию важности):
1. **Overdue & Today Deadlines** (дедлайн < завтра)
2. **Priority**: High > Medium > Low
3. **Estimated Effort**: Shortest Job First
4. **Created At**: старые задачи выше

## 3. Constraints (Лимиты)
- Total Daily Capacity: 8 часов (480 минут)
- Buffer: 10% (48 минут)
- Effective Planning Time: 432 минуты

## 4. Allocation Algorithm (Greedy)
1. Отсортированный список кандидатов
2. Remaining_Time = 432 мин
3. Для каждой задачи:
   - Если duration <= Remaining_Time → добавить
   - Иначе → пропустить (gap-filling)

## 5. Edge Cases
- Задача > 432 мин → добавляется с Warning
- Нет задач → "All clear for today"
- Pinned задачи → всегда первыми
"""