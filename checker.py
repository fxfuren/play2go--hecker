import httpx
from config import API_URL, TARIFF_FILTERS

async def fetch_tariffs():
    async with httpx.AsyncClient(timeout=15) as client:
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
