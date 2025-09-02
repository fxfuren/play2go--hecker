import asyncio
import logging
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN, CHAT_ID, CHECK_INTERVAL, LOG_FILE
from checker import fetch_tariffs, filter_tariffs, format_tariff

# --- Настройка логирования ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

last_available = set()

async def check_tariffs():
    global last_available
    while True:
        try:
            logging.info("Отправляем запрос к API...")
            data = await fetch_tariffs()
            filtered = filter_tariffs(data)

            available_now = {t["id"]: t for t in filtered if t["availability"]}

            new_ids = set(available_now.keys()) - set(last_available)
            if new_ids:
                msg = "🚀 Появились новые тарифы:\n\n" + "\n\n".join(
										format_tariff(available_now[i]) for i in new_ids
								) + "\n\n🔗 GitHub: https://github.com/fxfuren"
                await bot.send_message(CHAT_ID, msg)
                logging.info(f"Отправлено уведомление о {len(new_ids)} новых тарифах")

            last_available = available_now.keys()

        except Exception as e:
            logging.error(f"Ошибка при проверке тарифов: {e}")

        await asyncio.sleep(CHECK_INTERVAL)

async def run_bot():
    # Сообщаем в чат, что бот стартовал
    try:
        await bot.send_message(CHAT_ID, "🟢 Play2Go Tariff Bot запущен. Начинается логирование тарифов.")
        logging.info("Бот запущен, уведомление отправлено.")
    except Exception as e:
        logging.error(f"Не удалось отправить стартовое сообщение: {e}")

    asyncio.create_task(check_tariffs())
    await dp.start_polling(bot)
