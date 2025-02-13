from nextcord.ext import commands
import nextcord as nxc
from const import *
from modules import *

class Events(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_raw_message_delete(self, payload):
        message_id = payload.message_id
        print(f"Удаление сообщения {message_id} зафиксировано!")

        request = supabase.table("cards").select().eq("select_menu_id", message_id).execute()

        if request.data:
            supabase.table("cards").delete().eq("select_menu_id", message_id).execute()
            print("Карта успешно удалена")
        else:
            print("Удалённое сообщение не было банковской картой")
    
def setup(client):
    client.add_cog(Events(client))