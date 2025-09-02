# Play2Go Tariff Bot 🚀

Простой Telegram-бот для отслеживания доступности тарифов Play2Go по ключевым фильтрам (например LC и HI-LOAD).

Бот уведомляет в Telegram, когда выбранные тарифы становятся доступными.

---

## 📦 Структура проекта

```
play2go_bot/
├── bot.py           # Логика Telegram-бота
├── checker.py       # Функции работы с API и фильтрации тарифов
├── config.py        # Конфигурация из .env
├── main.py          # Точка входа
├── logs/            # Папка для логов
├── requirements.txt
├── .env             # Секреты и настройки
├── Dockerfile
├── docker-compose.yml
└── README.md
```

---

## ⚙️ Установка и запуск

### Локально

1. Установить зависимости:

```bash
pip install -r requirements.txt
```

2. Создать `.env` с переменными:

```env
BOT_TOKEN=твой_токен_бота
CHAT_ID=твой_chat_id
API_URL=https://play2go.cloud/api/servicesvm/tariffsvm
CHECK_INTERVAL=300
TARIFF_FILTERS=LC,HI-LOAD
```

3. Запуск:

```bash
docker compose up
```

## ⚡ Конфигурация

Все настройки хранятся в `.env`:

| Переменная       | Описание                                                    |
| ---------------- | ----------------------------------------------------------- |
| `BOT_TOKEN`      | Токен Telegram-бота                                         |
| `CHAT_ID`        | ID чата для отправки сообщений                              |
| `API_URL`        | URL API тарифов                                             |
| `CHECK_INTERVAL` | Интервал проверки в секундах                                |
| `TARIFF_FILTERS` | Список ключевых слов для фильтрации тарифов (через запятую) |
