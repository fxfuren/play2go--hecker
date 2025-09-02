import httpx
from config import API_URL, TARIFF_FILTERS

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
}

async def fetch_tariffs():
    """Запрос к API с имитацией браузера"""
    async with httpx.AsyncClient(headers=HEADERS, timeout=15) as client:
        r = await client.get(API_URL)
        r.raise_for_status()
        return r.json()

def filter_tariffs(data):
    """Фильтрация по ключевым словам из конфигурации"""
    return [
        t for t in data
        if any(keyword in t["name"] for keyword in TARIFF_FILTERS)
    ]

def format_tariff(tariff: dict) -> str:
    return (
        f"{tariff['name']} ({tariff['location_name']})\n"
        f"💵 {tariff['cost_rub']}₽ | {tariff['cost_eur']}€\n"
        f"🖥 CPU: {tariff['cpu']} | RAM: {tariff['ram']//1024}GB | "
        f"Disk: {tariff['disk']//1024}GB\n"
        f"🌐 Net: {tariff['internet_speed']} Mbps"
    )
