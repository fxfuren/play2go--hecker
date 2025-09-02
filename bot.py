import asyncio
import logging
import json
from pathlib import Path
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN, CHAT_ID, CHECK_INTERVAL, LOG_FILE

from checker import fetch_tariffs, filter_tariffs, format_tariff

logger = logging.getLogger(__name__)

# --- Настройка логирования ---
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
logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

STATUS_FILE = Path("status.json")
last_status = {}  # ключ: уникальный тариф, значение: availability
_check_task = None


def tariff_key(t):
    """Уникальный идентификатор тарифа для отслеживания"""
    return f"{t['id']}-{t['name']}-{t['location_name']}"


def load_status():
    global last_status
    if STATUS_FILE.exists():
        try:
            with STATUS_FILE.open("r", encoding="utf-8") as f:
                last_status = json.load(f)
            logger.info("Загружено состояние из файла status.json")
        except Exception as e:
            logger.error(f"Не удалось загрузить status.json: {e}")
            last_status = {}
    else:
        last_status = {}


def save_status():
    try:
        with STATUS_FILE.open("w", encoding="utf-8") as f:
            json.dump(last_status, f, ensure_ascii=False, indent=2)
        logger.debug("Состояние успешно сохранено в status.json")
    except Exception as e:
        logger.error(f"Ошибка при сохранении status.json: {e}")


async def check_tariffs():
    global last_status
    while True:
        try:
            logger.info("Отправляем запрос к API...")
            data = await fetch_tariffs()
            filtered = filter_tariffs(data)

            current_status = {tariff_key(t): t["availability"] for t in filtered}

            messages = []
            for key, avail in current_status.items():
                prev_avail = last_status.get(key)
                t = next(t for t in filtered if tariff_key(t) == key)

                if prev_avail is None and avail:
                    # новый тариф доступен
                    messages.append(f"🚀 Новый тариф доступен:\n{format_tariff(t)}")
                elif prev_avail is not None and prev_avail != avail:
                    # изменился статус
                    status_str = "✅ доступен" if avail else "❌ недоступен"
                    messages.append(f"⚡ Изменился статус тарифа {status_str}:\n{format_tariff(t)}")

            if messages:
                msg = "\n\n".join(messages) + "\n\n🔗 GitHub: https://github.com/fxfuren"
                await bot.send_message(CHAT_ID, msg)
                logger.info(f"Отправлено уведомление о {len(messages)} изменениях/новых тарифах")

            last_status = current_status
            save_status()

        except Exception as e:
            logger.exception(f"Ошибка при проверке тарифов: {e}")

        await asyncio.sleep(CHECK_INTERVAL)


async def run_bot():
    global _check_task
    load_status()

    # Сообщаем в чат, что бот стартовал
    try:
        await bot.send_message(CHAT_ID, "🟢 Play2Go Tariff Bot запущен. Начинается логирование тарифов.")
        logger.info("Бот запущен, уведомление отправлено.")
    except Exception as e:
        logger.error(f"Не удалось отправить стартовое сообщение: {e}")

    if _check_task is None or _check_task.done():
        _check_task = asyncio.create_task(check_tariffs())
        logger.info("Фоновая задача check_tariffs запущена.")
    else:
        logger.info("Фоновая задача уже запущена, новая не создаётся.")

    await dp.start_polling(bot)
