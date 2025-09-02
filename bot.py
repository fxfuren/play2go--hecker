import asyncio
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN, CHAT_ID, CHECK_INTERVAL
from checker import fetch_tariffs, filter_tariffs, format_tariff

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

last_available = set()

async def check_tariffs():
    global last_available
    while True:
        try:
            data = await fetch_tariffs()
            filtered = filter_tariffs(data)

            available_now = {
                t["id"]: t for t in filtered if t["availability"]
            }

            # новые
            new_ids = set(available_now.keys()) - set(last_available)
            if new_ids:
                msg = "🚀 Появились новые тарифы:\n\n" + "\n\n".join(
                    format_tariff(available_now[i]) for i in new_ids
                )
                await bot.send_message(CHAT_ID, msg)

            last_available = available_now.keys()

        except Exception as e:
            print(f"Ошибка: {e}")

        await asyncio.sleep(CHECK_INTERVAL)

async def run_bot():
    asyncio.create_task(check_tariffs())
    await dp.start_polling(bot)
