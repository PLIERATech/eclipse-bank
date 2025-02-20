from nextcord.ext import commands
import nextcord as nxc
from datetime import datetime
from const import *
from modules import *

class Events(commands.Cog):
    def __init__(self, client):
        self.client = client

    # Бот присоединился на сервер
    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        if guild.id not in server_id:
            print(f"Выход из {guild.name} ({guild.id}) — сервер не в списке разрешённых!")
            await guild.leave()

    # Игрок присоединился на сервер
    @commands.Cog.listener()
    async def on_member_join(self, member):
        client_info = supabase.table("clients").select("account, channels").eq("dsc_id", member.id).execute()

        if client_info.data:
            prdx_nick = get_prdx_nickname(member.id)
            supabase.table("clients").update({"nickname": prdx_nick}).eq("dsc_id", member.id).execute()
            guild = member.guild
            role = guild.get_role(client_role_id)
            await member.add_roles(role)
            category_id = client_info.data[0]['account']
            category = self.client.get_channel(category_id)
            channel_transactions_id = list(map(int, client_info.data[0]["channels"].strip("[]").split(",")))[0]
            channel_transactions = self.client.get_channel(channel_transactions_id)
            channel_card_id = list(map(int, client_info.data[0]["channels"].strip("[]").split(",")))[1]
            channel_card = self.client.get_channel(channel_card_id)
            await category.set_permissions(member, overwrite=nxc.PermissionOverwrite(view_channel=True, read_messages=True, read_message_history=True))
            await channel_transactions.set_permissions(member, overwrite=nxc.PermissionOverwrite(view_channel=True, read_message_history=True, read_messages=True, send_messages=False))
            await channel_card.set_permissions(member, overwrite=nxc.PermissionOverwrite(view_channel=True, read_message_history=True, read_messages=True, send_messages=False))
            print(f"Клиент {member.display_name} вернулся на сервер и вернул роль {role.name} с правами на каналы.")
            supabase.table("clients").update({"status": "active","freeze_date": None}).eq("dsc_id", member.id).execute()


    # Игрок вышел с сервера
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        client_info = supabase.table("clients").select("account, nickname, status").eq("dsc_id", member.id).execute()

        if client_info.data:
            client_nick = client_info.data[0]['account']
            today_date = datetime.now().strftime("%Y-%m-%d")
            print(f"Клиент {member.name} вышел из сервера, его ник {client_nick} и его аккаунт заморожен с {today_date}")
            supabase.table("clients").update({"status": "freeze","freeze_date": today_date}).eq("dsc_id", member.id).execute()


    # Игрок обновил про себя информацию (поменял ник)
    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if before.display_name != after.display_name:
            client_info = supabase.table("clients").select("account, channels").eq("dsc_id", after.id).execute()
            if client_info.data:
                prdx_nick = get_prdx_nickname(after.id)
                supabase.table("clients").update({"nickname": prdx_nick}).eq("dsc_id", after.id).execute()


    # Было удалено сообщение в категориях игроков
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

                await del_img_in_channel(self.client, full_number)
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
                    card_embed_user = e_cards_users(channel_owner.guild, color, owner_name, members)
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





