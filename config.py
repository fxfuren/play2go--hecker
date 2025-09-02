import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = int(os.getenv("CHAT_ID"))
API_URL = os.getenv("API_URL", "https://play2go.cloud/api/servicesvm/tariffsvm")
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", 300))

# Список фильтров по тарифам (например ["LC", "HI-LOAD"])
TARIFF_FILTERS = [
    f.strip() for f in os.getenv("TARIFF_FILTERS", "").split(",") if f.strip()
]
