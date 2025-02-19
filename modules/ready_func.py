from nextcord.ext import commands
import nextcord as nxc
from const import *
from .select_menu import *
from .log_functions import *

async def start_persistent_view(bot):
    # Регистрируем View, чтобы оно работало после перезапуска
    bot.add_view(CardSelectView())
    print("Persistent View зарегистрирован.")

    # Выход из сервера, если бот добавлен на неразрешённый сервер
    for guild in bot.guilds:
        if guild.id not in server_id:
            print(f"Выход из {guild.name} ({guild.id}) — сервер не в списке разрешённых!")
            await guild.leave()

    # Получаем все карты
    cards_data = supabase.table("cards").select("select_menu_id, owner, members, clients(channels)").execute()

    for card in cards_data.data:
        select_menu_id = card["select_menu_id"]
        owner_id = card["owner"]
        members = card["members"]

        if not isinstance(members, dict):  # Проверяем, если это не словарь (jsonb)
            members = {}

        client_data = card.get("clients")  # Данные уже получены с JOIN
        if client_data:
            channels = client_data["channels"]
            channels_list = list(map(int, channels.strip("[]").split(",")))
            channel_id = channels_list[1]
            channel = bot.get_channel(channel_id)

            if channel:
                try:
                    message_owner = await channel.fetch_message(select_menu_id)  # Проверяем, что карта существует
                except nxc.NotFound:
                    supabase.table("cards").delete().eq("select_menu_id", select_menu_id).execute()
                    print(f"Удалена карта {select_menu_id} (сообщение отсутствует)")
                    continue
            else:
                print(f"Канал с ID {channel_id} не найден.")
                continue

            # Проверяем, есть ли сообщения участников и удаляем отсутствующих
            members_to_delete = []

            for user_id, data in members.items():
                msg_id = data.get("id_message")
                channel_id = data.get("id_channel")
                channel = bot.get_channel(channel_id)

                if channel:
                    try:
                        await channel.fetch_message(msg_id)  # Проверяем сообщение участника
                    except nxc.NotFound:
                        members_to_delete.append(user_id)  # Помечаем на удаление
                else:
                    members_to_delete.append(user_id)  # Если канал не найден, тоже удаляем

            # Удаляем участников, чьи сообщения отсутствуют
            for user_id in members_to_delete:
                del members[user_id]

            # Если участники удалены, обновляем embed у владельца и всех остальных
            if members_to_delete:
                existing_embeds = message_owner.embeds
                color = existing_embeds[1].color  # Цвет карты
                owner_name = client_data.get("nickname", "Неизвестный владелец")  # Имя владельца

                # Обновляем embed с пользователями
                card_embed_user = e_cards_users(channel.guild, color, owner_name, members)

                await message_owner.edit(embeds=[existing_embeds[0], existing_embeds[1], card_embed_user], attachments=[])

                # Обновляем сообщения всех оставшихся участников
                for user_id, data in members.items():
                    msg_id = data.get("id_message")
                    channel_id = data.get("id_channel")
                    channel = bot.get_channel(channel_id)

                    if channel:
                        try:
                            message_users = await channel.fetch_message(msg_id)
                            await message_users.edit(embeds=[existing_embeds[0], existing_embeds[1], card_embed_user], attachments=[])
                        except nxc.NotFound:
                            pass

                # Обновляем базу данных
                supabase.table("cards").update({"members": members}).eq("select_menu_id", select_menu_id).execute()
                print(f"Обновлена карта {select_menu_id}: удалены отсутствующие пользователи")
