import logging
import re
import time

from requests.exceptions import RequestException
from telebot.apihelper import ApiTelegramException

from app.bot import bot
from app.db.schema import init_db


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)


def _extract_retry_after(exc: Exception) -> int | None:
    """Extract retry delay from Telegram 429 error text."""
    message = str(exc)
    match = re.search(r"retry after\s+(\d+)", message, re.IGNORECASE)
    if match:
        return int(match.group(1))
    return None


def run_bot_forever() -> None:
    backoff = 2
    max_backoff = 60

    while True:
        try:
            logging.info("Starting bot polling")
            bot.polling(none_stop=True, timeout=30, long_polling_timeout=20)
            backoff = 2

        except ApiTelegramException as exc:
            retry_after = _extract_retry_after(exc)
            sleep_for = retry_after if retry_after is not None else backoff
            logging.exception("Telegram API error: %s", exc)
            logging.warning("Will restart polling in %s seconds", sleep_for)
            time.sleep(sleep_for)
            if retry_after is None:
                backoff = min(backoff * 2, max_backoff)

        except (RequestException, TimeoutError) as exc:
            logging.exception("Network error: %s", exc)
            logging.warning("Will restart polling in %s seconds", backoff)
            time.sleep(backoff)
            backoff = min(backoff * 2, max_backoff)

        except Exception as exc:
            logging.exception("Unexpected error: %s", exc)
            logging.warning("Will restart polling in %s seconds", backoff)
            time.sleep(backoff)
            backoff = min(backoff * 2, max_backoff)


if __name__ == "__main__":
    logging.info("--- The bot is launching... ---")
    logging.info("Checking the database...")
    init_db()
    logging.info("The bot has been successfully launched and is ready to go!")
    run_bot_forever()
