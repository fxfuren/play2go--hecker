import asyncio
import logging
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN, CHAT_ID, CHECK_INTERVAL, LOG_FILE
from checker import fetch_tariffs, filter_tariffs, format_tariff

logger = logging.getLogger(__name__)

# --- Настройка логирования (только если ещё не настроено) ---
root_logger = logging.getLogger()
if not root_logger.handlers:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(LOG_FILE),
            logging.StreamHandler()
        ]
    )
# теперь используем logger
logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

last_available = set()
_check_task = None  # глобальная переменная для контроля единственности задачи


async def check_tariffs():
    global last_available
    while True:
        try:
            logger.info("Отправляем запрос к API...")
            data = await fetch_tariffs()
            filtered = filter_tariffs(data)

            available_now = {t["id"]: t for t in filtered if t["availability"]}

            new_ids = set(available_now.keys()) - set(last_available)
            if new_ids:
                msg = "🚀 Появились новые тарифы:\n\n" + "\n\n".join(
                    format_tariff(available_now[i]) for i in new_ids
                ) + "\n\n🔗 GitHub: https://github.com/fxfuren"
                await bot.send_message(CHAT_ID, msg)
                logger.info(f"Отправлено уведомление о {len(new_ids)} новых тарифах")

            # сохраняем как set для корректного сравнения в следующей итерации
            last_available = set(available_now.keys())

        except Exception as e:
            logger.exception(f"Ошибка при проверке тарифов: {e}")

        await asyncio.sleep(CHECK_INTERVAL)


async def run_bot():
    global _check_task

    # Сообщаем в чат, что бот стартовал
    try:
        await bot.send_message(CHAT_ID, "🟢 Play2Go Tariff Bot запущен. Начинается логирование тарифов.")
        logger.info("Бот запущен, уведомление отправлено.")
    except Exception as e:
        logger.error(f"Не удалось отправить стартовое сообщение: {e}")

    # Запускаем фоновую задачу ТОЛЬКО если она ещё не запущена
    if _check_task is None or _check_task.done():
        _check_task = asyncio.create_task(check_tariffs())
        logger.info("Фоновая задача check_tariffs запущена.")
    else:
        logger.info("Фоновая задача уже запущена, новая не создаётся.")

    await dp.start_polling(bot)
