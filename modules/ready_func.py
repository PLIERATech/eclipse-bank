from nextcord.ext import commands
import nextcord as nxc
from const import *
from .select_menu import *
from .log_functions import *

async def start_persistent_view(bot):
# Регистрируем View, чтобы оно работало после перезапуска
        bot.add_view(CardSelectView())
        print("Persistent View зарегистрирован.")

        cards_data = supabase.table("cards").select("select_menu_id, owner, clients(channels)").execute()

        for card in cards_data.data:
            select_menu_id = card["select_menu_id"]
            owner_id = card["owner"]

            client_data = card.get("clients")  # Данные уже получены с JOIN
            if client_data:
                channels = client_data["channels"]
                channels_list = list(map(int, channels.strip("[]").split(",")))
                channel_id = channels_list[1]
                channel = bot.get_channel(channel_id)

                if channel:
                    try:
                        await channel.fetch_message(select_menu_id)  # Проверяем, что сообщение существует
                        print(f"Сообщение с ID {select_menu_id} найдено в канале {channel.name}.")
                    except nxc.NotFound:
                        print(f"Сообщение с ID {select_menu_id} не найдено в канале {channel.name}.")
                        supabase.table("cards").delete().eq("select_menu_id", select_menu_id).execute()
                else:
                    print(f"Канал с ID {channel_id} не найден.")
            else:
                print(f"Клиент с ID {owner_id} не найден в таблице clients.")