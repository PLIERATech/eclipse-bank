from nextcord.ext import commands
import nextcord as nxc
from const import *
from modules import *

class Events(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        if guild.id not in server_id:
            print(f"Выход из {guild.name} ({guild.id}) — сервер не в списке разрешённых!")
            await guild.leave()


    @commands.Cog.listener()
    async def on_raw_message_delete(self, payload):
        channel = self.client.get_channel(payload.channel_id)
        message_id = payload.message_id
        
        # Проверяем, есть ли канал и находится ли он в нужном сервере
        if not channel or not channel.guild or channel.guild.id not in server_id:
            return

        # Проверяем, есть ли у канала категория и не нужно ли его игнорировать
        if channel.category and channel.category.id in ignored_categories:
            return

        print(f"Удаление сообщения {message_id} зафиксировано!")

        request_card_member = supabase.rpc("find_message_in_members", {"msg_id": message_id}).execute()

        if request_card_member.data:
            # Проверяем, из какого запроса пришли данные
            query_type = request_card_member.data[0].get('query_type')

            if query_type == 'select_menu_id':
                supabase.table("cards").delete().eq("select_menu_id", message_id).execute()
                type = request_card_member.data[0]['type']
                number = request_card_member.data[0]['number']
                full_number = f"{suffixes.get(type, type)}{number}"
                members = request_card_member.data[0]['members']

                if not isinstance(members, dict):  # Проверяем, если это не словарь (jsonb)
                    members = {}

                for user_id, data in members.items():
                    msg_id = data.get("id_message")
                    channel_member_id = data.get("id_channel")
                    channel_member = self.client.get_channel(channel_member_id)
                    message_member = await channel_member.fetch_message(msg_id)
                    await message_member.delete()

                channel = self.client.get_channel(image_saver_channel)
                async for message in channel.history(limit=None):
                    if full_number in message.content:
                        await message.delete()
                print("Карта успешно удалена")

            elif query_type == 'members':
                members = request_card_member.data[0]['members']
                client_data = request_card_member.data[0].get("clients")
                owner_name = client_data["nickname"]
                channels_list = list(map(int, client_data["channels"].strip("[]").split(",")))
                channel_id = channels_list[1]
                channel_owner = self.client.get_channel(channel_id)
                messege_owner_id = request_card_member.data[0]['select_menu_id']

                if not isinstance(members, dict):  # Проверяем, если это не словарь (jsonb)
                    members = {}

                if request_card_member.data:
                    members = {user_id: data for user_id, data in members.items() if data.get("id_message") != message_id}
                    
                    message_owner = await channel_owner.fetch_message(messege_owner_id)

                    # Обновляем карту
                    existing_embeds = message_owner.embeds
                    color = existing_embeds[1].color
                    card_embed_user = e_cards_users(channel_owner, color, owner_name, members)
                    await message_owner.edit(embeds=[existing_embeds[0], existing_embeds[1], card_embed_user], attachments=[])

                    # Обновляем сообщения всех пользователей
                    for user_id, data in members.items():
                        msg_id = data.get("id_message")
                        channel_id = data.get("id_channel")
                        channel = self.client.get_channel(channel_id)
                        message_users = await channel.fetch_message(msg_id)
                        await message_users.edit(embeds=[existing_embeds[0], existing_embeds[1], card_embed_user], attachments=[])

                    # Обновляем данные в базе данных
                    supabase.table("cards").update({"members": members}).eq("select_menu_id", messege_owner_id).execute()

                    print("Карта от пользователя успешно удалена")


def setup(client):
    client.add_cog(Events(client))





