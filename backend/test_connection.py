import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import test_connection, create_tables

if __name__ == "__main__":
    print("Тестування підключення до БД...")
    print(f"База даних: ai_time_manager")
    print(f"Хост: 68.183.79.39")

    if test_connection():
        print("Тест підключення пройдений!")

        print("Створення таблиць...")
        create_tables()
        print("Всі перевірки пройдені успішно!")
    else:
        print("Тест підключення не пройдений!")
        print("Перевірте:")
        print("   - Доступ до хоста 68.183.79.39:3306")
        print("   - Коректність логіна/пароля")
        print("   - Наявніст    ь бази даних 'ai_time_manager'")