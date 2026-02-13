import logging
from database import init_db
from main import bot

# Loginfo to see errors
logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    print("--- The bot is launching... ---")

    try:
        # 1. Create Tables for DB if not exist
        print("Checking the database...")
        init_db()

        # 2. Bot running
        print("The bot has been successfully launched and is ready to go!")
        bot.polling(none_stop=True)

    except Exception as e:
        print(f"An error occurred during startup: {e}")