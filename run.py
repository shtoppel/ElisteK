import logging
from database import init_db
from main import bot

# Loginfo to see errors
logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    print("--- Бот запускается... ---")

    try:
        # 1. Create Tables for DB if not exist
        print("Проверка базы данных...")
        init_db()

        # 2. Bot running
        print("Бот успешно запущен и готов к работе!")
        bot.polling(none_stop=True)

    except Exception as e:
        print(f"Произошла ошибка при запуске: {e}")