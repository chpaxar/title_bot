# Discord Title Bot

# Discord-бот для управления тайтлами и участниками.

## Как запустить

# 1. Клонируйте репозиторий:
git clone https://github.com/chpaxar/title_bot.git
cd title_bot

# 2. Заполните .env:
DISCORD_TOKEN=ваш_токен
GUILD_ID=ID_вашего_сервера
DATABASE_URL=postgresql://user:pass@db:5432/titlebot

# 3. Запустите Docker:
docker-compose up --build

# 4. Бот автоматически создаст таблицу и подключится к
# PostgreSQL.
