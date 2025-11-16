# Claude Telegram Bot

Telegram бот-прокси для Claude API. Сохраняет контекст, ограничивает доступ по username.

## Быстрый старт

### 1. Настройка

```bash
# Установка
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Конфиг
cp .env.example .env
nano .env  # Заполни токены
```

`.env`:
```env
TELEGRAM_BOT_TOKEN=your_bot_token          # От @BotFather
ANTHROPIC_API_KEY=your_anthropic_api_key   # С console.anthropic.com
ALLOWED_USERNAMES=username1,username2       # Без @
```

### 2. Запуск

```bash
# Проверка конфига
python check_config.py

# Локально
python bot.py

# На сервере (автоматом)
./deploy.sh
```

## Команды бота

- `/start` - начало работы
- `/clear` - очистить контекст
- `/enable_context` - включить контекст (по умолчанию)
- `/disable_context` - отключить контекст (каждое сообщение отдельно)
- `/system_prompt <текст>` - установить системный промпт
- `/reset_system_prompt` - сбросить промпт
- `/info` - информация о модели и текущей сессии
- `/help` - справка

## Деплой на VPS

```bash
# Скопируй файлы на сервер
scp -r * root@server:/root/claude-telegram/

# Скопируй .env (он скрытый, * его не копирует)
scp .env root@server:/root/claude-telegram/

# На сервере
cd /root/claude-telegram
./deploy.sh
```

**deploy.sh** автоматом:
- Установит зависимости
- Настроит systemd
- Запустит бота

### Управление

```bash
sudo systemctl status claude-telegram-bot    # Статус
sudo systemctl restart claude-telegram-bot   # Рестарт
sudo journalctl -u claude-telegram-bot -f    # Логи
```

### Изменение конфига

```bash
# Редактируй .env
nano ~/claude-telegram/.env

# Перезапусти бота
sudo systemctl restart claude-telegram-bot

# Проверь логи
sudo journalctl -u claude-telegram-bot -f
```

## Docker

```bash
docker compose up -d      # Запуск
docker compose logs -f    # Логи
docker compose down       # Стоп
```

## Архитектура

```
bot.py             - Telegram бот (команды, авторизация)
claude_client.py   - Claude API + управление контекстом
config.py          - Конфиг из .env
```

**Фичи:**
- Контекст в памяти (на пользователя)
- Авторизация по whitelist username
- Автосплит длинных ответов
- Type hints, docstrings
- Логирование

## Стоимость

- VPS: $5/мес (DigitalOcean, Linode, Vultr)
- Claude API: ~$9/1k сообщений
- **Итого:** ~$14/мес

## Лицензия

MIT
