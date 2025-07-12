import disnake
from disnake.ext import commands
import os
from dotenv import load_dotenv
from db import connect_db, create_titles_table, insert_title, update_worker, get_title


load_dotenv()

GUILD_ID = int(os.getenv("GUILD_ID"))
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

intents = disnake.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.InteractionBot(intents=intents)

# Временное хранилище тайтлов (пока без БД)
titles = {}

@bot.event
async def on_ready():
    await connect_db()
    await create_titles_table()
    print(f"✅ Бот запущен как {bot.user}")
    try:
        await bot.sync_commands(guild_id=GUILD_ID)
        print("✅ Команды успешно синхронизированы.")
    except Exception as e:
        print(f"Ошибка при синхронизации: {e}")


@bot.slash_command(description="Создать новый тайтл в этом канале", guild_ids=[GUILD_ID])
async def создать_тайтл(
    inter: disnake.ApplicationCommandInteraction,
    название: str,
    куратор: disnake.Member
):
    # Роль с правами к созданию (по желанию менять)
    if not any(role.name == "Администратор" for role in inter.author.roles):
        await inter.response.send_message("❌ У вас нет прав для создания тайтлов.", ephemeral=True)
        return

    # Сохраняем тайтл в БД
    await insert_title(inter.channel.id, название, куратор.id)

    embed = disnake.Embed(
        title=f"📘 {название}",
        description=f"Куратор: {куратор.mention}",
        color=disnake.Color.blue()
    )

    # Отправляем embed и сохраняем сообщение
    message = await inter.channel.send("✅ Тайтл создан!", embed=embed)

    # Создаём ветку (тред) от embed-сообщения
    await message.create_thread(
        name=f"Материалы: {название}",
        auto_archive_duration=1440  # 24 часа
    )

    await inter.response.send_message("✅ Тайтл успешно зарегистрирован в этом канале.", ephemeral=True)



@bot.slash_command(description="Обновить роль участника тайтла", guild_ids=[GUILD_ID])
async def обновить_работника(
    inter: disnake.ApplicationCommandInteraction,
    роль: str = commands.Param(choices=["переводчик", "редактор", "клинер", "тайпер", "бета-ридер"]),
    участник: disnake.Member = commands.Param(name="участник")
):
    # Получаем тайтл из базы
    title_data = await get_title(inter.channel.id)

    if not title_data:
        await inter.response.send_message("❌ В этом канале не прикреплён тайтл.", ephemeral=True)
        return

    if inter.author.id != title_data["куратор"]:
        await inter.response.send_message("❌ Только куратор может изменять состав работников.", ephemeral=True)
        return

    # Обновляем работника в базе
    await update_worker(inter.channel.id, роль, участник.id)

    await inter.response.send_message(f"✅ Роль **{роль}** обновлена. Теперь это {участник.mention}")


@bot.slash_command(description="Показать информацию о текущем тайтле", guild_ids=[GUILD_ID])
async def тайтл_инфо(inter: disnake.ApplicationCommandInteraction):
    # Получаем тайтл из БД
    title_data = await get_title(inter.channel.id)

    if not title_data:
        await inter.response.send_message("❌ В этом канале не прикреплён тайтл.", ephemeral=True)
        return

    embed = disnake.Embed(
        title=f"📘 {title_data['название']}",
        color=disnake.Color.green()
    )
    embed.add_field(name="Куратор", value=f"<@{title_data['куратор']}>", inline=False)

    for роль in ["переводчик", "редактор", "клинер", "тайпер", "бета-ридер"]:
        участник_id = title_data.get(роль)
        текст = f"<@{участник_id}>" if участник_id else "не назначен"
        embed.add_field(name=роль.capitalize(), value=текст, inline=True)

    await inter.response.send_message(embed=embed)


if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
