# Discord Title Bot

# Discord-бот для управления тайтлами и участниками.

## Как запустить

# 1. Скачиваете архив и извлекаете все в желаемую папку

# 2. Измените .env:
DISCORD_TOKEN=ваш_токен

GUILD_ID=ID_вашего_сервера
'''Ссылку не менять'''
DATABASE_URL=postgresql://user:pass@db:5432/titlebot

# 3. Запустите Docker через консоль папки:
docker-compose up --build

# 4. Бот автоматически создаст таблицу и подключится к
# PostgreSQL в самом Docker'е.
