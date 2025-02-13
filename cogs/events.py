from nextcord.ext import commands
import nextcord as nxc
from const import *
from modules import *

class Events(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Бот запущен как {self.client.user}")

        # Регистрируем View, чтобы оно работало после перезапуска
        self.client.add_view(CardSelectView())
        print("Persistent View зарегистрирован.")

        cards_data = supabase.table("cards").select("select_menu_id, owner").execute()

        for card in cards_data.data:
            select_menu_id = card["select_menu_id"]
            owner_id = card["owner"]

            client_data = supabase.table("clients").select("channels").eq("dsc_id", owner_id).execute()
            if client_data.data:
                channels = client_data.data[0]["channels"]
                channels_list = list(map(int, channels.strip("[]").split(",")))
                channel_id = channels_list[1]
                channel = self.client.get_channel(channel_id)

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

def setup(client):
    client.add_cog(Events(client))
