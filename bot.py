# Здесь идёт импорт библиотек
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

@bot.event
async def on_ready():
    await connect_db()
    await create_titles_table()
    '''
    Это обработчик события, в данном случае будет вызван лишь раз, по иному это
    декоратор
    '''
    print(f"✅ Бот запущен как {bot.user}")
    try:
        await bot.sync_commands(guild_id=GUILD_ID)
        print("✅ Команды успешно синхронизированы.")
    except Exception as e:
        print(f"Ошибка при синхронизации: {e}")


@bot.slash_command(description="Создать новый тайтл в этом канале", guild_ids=[GUILD_ID])
async def create_title(
    inter: disnake.ApplicationCommandInteraction,
    название: str,
    куратор: disnake.Member
):
    '''
        Создаёт новый тайтл (проект) в текущем канале.

        Параметры:
            inter (disnake.ApplicationCommandInteraction): взаимодействие от пользователя
            название (str): название тайтла
            куратор (disnake.Member): участник Discord, назначаемый куратором

        Возвращаемое значение:
            Отправляет embed-сообщение с названием тайтла и куратором,
            создаёт ветку "Материалы: <название>", сохраняет данные в БД.
        '''
    if not any(role.name == "Администратор" for role in inter.author.roles): # Менять вот тут
        await inter.response.send_message("❌ У вас нет прав для создания тайтлов.", ephemeral=True)
        return

    await insert_title(inter.channel.id, название, куратор.id)

    embed = disnake.Embed(
        title=f"📘 {название}",
        description=f"Куратор: {куратор.mention}",
        color=disnake.Color.blue()
    )

    message = await inter.channel.send("✅ Тайтл создан!", embed=embed)
    await message.create_thread(name=f"Материалы: {название}", auto_archive_duration=1440)

    await inter.response.send_message("✅ Тайтл успешно зарегистрирован в этом канале.", ephemeral=True)


@bot.slash_command(description="Обновить роль участника тайтла", guild_ids=[GUILD_ID])
async def role_for_worker(
    inter: disnake.ApplicationCommandInteraction,
    роль: str = commands.Param(choices=["переводчик", "редактор", "клинер", "тайпер", "бета-ридер"]),
    участник: disnake.Member = commands.Param(name="участник")
):
    '''
        Обновляет роль участника в тайтле (проекте), прикреплённом к текущему каналу.

        Параметры:
            inter (disnake.ApplicationCommandInteraction): взаимодействие от пользователя
            роль (str): роль участника (выбирается из списка: переводчик, редактор, клинер, тайпер, бета-ридер)
            участник (disnake.Member): участник Discord-сервера, которому назначается выбранная роль

        Возвращаемое значение:
            Отправляет подтверждение об обновлении роли участника. Только куратор тайтла может обновлять роли.
        '''
    title_data = await get_title(inter.channel.id)

    if not title_data:
        await inter.response.send_message("❌ В этом канале не прикреплён тайтл.", ephemeral=True)
        return

    if inter.author.id != title_data["curator_id"]:
        await inter.response.send_message("❌ Только куратор может изменять состав работников.", ephemeral=True)
        return

    role_map = {
        "переводчик": "translator_id",
        "редактор": "editor_id",
        "клинер": "cleaner_id",
        "тайпер": "typer_id",
        "бета-ридер": "beta_reader_id"
    }

    column_name = role_map[роль]
    await update_worker(inter.channel.id, column_name, участник.id)

    await inter.response.send_message(f"✅ Роль **{роль}** обновлена. Теперь это {участник.mention}")


@bot.slash_command(description="Показать информацию о текущем тайтле", guild_ids=[GUILD_ID])
async def title_info(inter: disnake.ApplicationCommandInteraction):
    '''
        Показывает информацию о тайтле, прикреплённом к текущему каналу.

        Параметры:
            inter (disnake.ApplicationCommandInteraction): взаимодействие от пользователя

        Возвращаемое значение:
            Отправляет embed-сообщение с данными о тайтле:
            - название
            - куратор
            - участники по ролям (переводчик, редактор, клинер, тайпер, бета-ридер)

            Если в текущем канале не прикреплён тайтл, выводит сообщение об ошибке.
        '''
    title_data = await get_title(inter.channel.id)

    if not title_data:
        await inter.response.send_message("❌ В этом канале не прикреплён тайтл.", ephemeral=True)
        return

    embed = disnake.Embed(
        title=f"📘 {title_data['title']}",
        color=disnake.Color.green()
    )
    embed.add_field(name="Куратор", value=f"<@{title_data['curator_id']}>", inline=False)

    roles = {
        "переводчик": "translator_id",
        "редактор": "editor_id",
        "клинер": "cleaner_id",
        "тайпер": "typer_id",
        "бета-ридер": "beta_reader_id"
    }

    for name_ru, column in roles.items():
        uid = title_data.get(column)
        текст = f"<@{uid}>" if uid else "не назначен"
        embed.add_field(name=name_ru.capitalize(), value=текст, inline=True)

    await inter.response.send_message(embed=embed)



if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
