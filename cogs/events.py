from nextcord.ext import commands
import nextcord as nxc
from datetime import datetime
from const import *
from modules import *
from db import *

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
        client_info = db_cursor("clients").select("account").eq("dsc_id", member.id).execute()

        if client_info.data:
            guild = member.guild
            role = guild.get_role(client_role_id)
            channel_id = client_info.data[0]["account"]
            channel = guild.get_channel(channel_id)

            prdx_nick = get_prdx_nickname(member.id)
            try:
                await channel.edit(name=f"💳ㆍ{prdx_nick}")
            except nxc.HTTPException as e:
                print(f"Ошибка при переименовании канала: {e}")

            db_cursor("clients").update({"nickname": prdx_nick}).eq("dsc_id", member.id).execute()

            await member.add_roles(role)
            channel_card_id = client_info.data[0]['account']
            channel_card = self.client.get_channel(channel_card_id)
            await channel_card.set_permissions(member, overwrite=nxc.PermissionOverwrite(view_channel=True, read_message_history=True, read_messages=True, send_messages=False, send_messages_in_threads=False))
            print(f"Клиент {member.display_name} вернулся на сервер и вернул роль {role.name} с правами на каналы.")
            db_cursor("clients").update({"status": "active","freeze_date": None}).eq("dsc_id", member.id).execute()

            #Аудит действия
            member_audit = guild.get_channel(bank_audit_channel)

            title_emb, message_emb, color_emb = get_message_with_title(
                60, (), (member.id))
            embed_aud_member_join = emb_auto(title_emb, message_emb, color_emb)
            await member_audit.send(embed=embed_aud_member_join)    




    # Игрок вышел с сервера
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        guild = member.guild
        client_info = db_cursor("clients").select("account, nickname, status").eq("dsc_id", member.id).execute()

        if client_info.data:
            client_nick = client_info.data[0]['account']
            today_date = datetime.now().strftime("%Y-%m-%d")
            print(f"Клиент {member.name} вышел из сервера, его ник {client_nick} и его аккаунт заморожен с {today_date}")
            db_cursor("clients").update({"status": "freeze","freeze_date": today_date}).eq("dsc_id", member.id).execute()

            #Аудит действия
            member_audit = guild.get_channel(bank_audit_channel)

            title_emb, message_emb, color_emb = get_message_with_title(
                61, (), (member.id))
            embed_aud_member_remove = emb_auto(title_emb, message_emb, color_emb)
            await member_audit.send(embed=embed_aud_member_remove)    




    # Игрок обновил про себя информацию (поменял ник)
    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if before.display_name != after.display_name:
            client_info = db_cursor("clients").select("account").eq("dsc_id", after.id).execute()
            if client_info.data:
                guild = after.guild
                channel_id = client_info.data[0]["account"]
                channel = guild.get_channel(channel_id)

                prdx_nick = get_prdx_nickname(after.id)
                try:
                    await channel.edit(name=f"💳ㆍ{prdx_nick}")
                except nxc.HTTPException as e:
                    print(f"Ошибка при переименовании канала: {e}")

                db_cursor("clients").update({"nickname": prdx_nick}).eq("dsc_id", after.id).execute()




    # Было удалено сообщение в категориях игроков
    @commands.Cog.listener()
    async def on_raw_message_delete(self, payload):
        channel = self.client.get_channel(payload.channel_id)
        message_id = payload.message_id
        
        # Проверяем, есть ли канал и находится ли он в нужном сервере
        if not channel or not channel.guild or channel.guild.id not in server_id:
            return

        # Проверяем, находится ли канал в нужной категории
        if channel.category_id != cleints_category:
            return 

        # Если канал является веткой, игнорируем его
        if channel.type in [nxc.ChannelType.public_thread, nxc.ChannelType.private_thread]:
            return

        print(f"Удаление сообщения {message_id} зафиксировано!")

        request_card_member = db_rpc("find_message_in_members", {"msg_id": message_id}).execute()

        if request_card_member.data:
            # Проверяем, из какого запроса пришли данные
            query_type = request_card_member.data[0].get('query_type')
            if query_type == 'select_menu_id':
                db_cursor("cards").delete().eq("select_menu_id", message_id).execute()
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
                owner_name = request_card_member.data[0]["nickname"]
                channel_id = request_card_member.data[0]["account"]
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
                    card_embed_user = emb_cards_users(channel_owner.guild, color, owner_name, members)
                    await message_owner.edit(embeds=[existing_embeds[0], existing_embeds[1], card_embed_user], attachments=[])

                    # Обновляем сообщения всех пользователей
                    for user_id, data in members.items():
                        msg_id = data.get("id_message")
                        channel_id = data.get("id_channel")
                        channel = self.client.get_channel(channel_id)
                        message_users = await channel.fetch_message(msg_id)
                        await message_users.edit(embeds=[existing_embeds[0], existing_embeds[1], card_embed_user], attachments=[])

                    # Обновляем данные в базе данных
                    db_cursor("cards").update({"members": members}).eq("select_menu_id", messege_owner_id).execute()

                    print("Карта от пользователя успешно удалена")


def setup(client):
    client.add_cog(Events(client))





