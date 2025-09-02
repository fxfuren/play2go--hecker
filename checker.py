import logging
import json
import httpx
from config import API_URL, TARIFF_FILTERS

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
}

LOG_JSON_TRUNCATE = 4000

async def fetch_tariffs():
    """Запрос к API с имитацией браузера и следованием редиректам.
    Логируем статус, content-type, длину и фрагмент тела ответа.
    """
    async with httpx.AsyncClient(headers=HEADERS, timeout=15, follow_redirects=True) as client:
        resp = await client.get(API_URL)
        # логируем базовую информацию о ответе
        logger.info("HTTP %s %s", resp.status_code, resp.url)
        logger.info("Response headers: %s", {
            k: resp.headers[k] for k in ("content-type", "content-length") if k in resp.headers
        })

        # Попытка распарсить JSON — если не JSON, логируем текст (тоже обрезаем)
        text = resp.text
        content_len = len(text or "")
        logger.info("Response body length: %d bytes", content_len)

        try:
            data = resp.json()
            # подготовим красиво отформатированный json-фрагмент для лога
            pretty = json.dumps(data, ensure_ascii=False, indent=2)
            if len(pretty) > LOG_JSON_TRUNCATE:
                pretty_shown = pretty[:LOG_JSON_TRUNCATE] + "\n... (truncated)"
            else:
                pretty_shown = pretty
            logger.debug("Response JSON (truncated):\n%s", pretty_shown)

            # краткая сводка: сколько элементов и сколько доступно
            if isinstance(data, list):
                total = len(data)
                avail = sum(1 for t in data if t.get("availability"))
                logger.info("Parsed JSON: list with %d items, %d available", total, avail)
            else:
                logger.info("Parsed JSON of type %s", type(data))

            return data

        except ValueError:
            # не JSON — логируем текст (с обрезкой)
            if content_len > LOG_JSON_TRUNCATE:
                logger.debug("Response text (truncated): %s", text[:LOG_JSON_TRUNCATE] + "\n... (truncated)")
            else:
                logger.debug("Response text: %s", text)
            # пробрасываем ошибку дальше, чтобы вызывающий код её обработал
            resp.raise_for_status()
            return None  # на случай, если выше не сработало

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
