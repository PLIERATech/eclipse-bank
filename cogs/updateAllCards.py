import nextcord as nxc
from nextcord.ext import commands
from const import *
from modules import *
from db import *

command = "/updateAllCards"

class UpdateAllCards(commands.Cog):
    def __init__(self, client):
        self.client = client

    @nxc.slash_command(guild_ids=server_id, name="updateallcards", description="Update information about all created maps", default_member_permissions=nxc.Permissions(administrator=True))
    async def updateAllCards(self, inter: nxc.Interaction):
        admin = inter.user
        if not await verify_staff(inter, admin, command):
            return

        await inter.response.defer(ephemeral=True)

        cards_data = db_cursor("cards").select("select_menu_id, owner, number, members, type, name, clients.channels, clients.nickname").execute()
        total = len(cards_data.data)

        # Проверка есть ли карты в бд
        if not await verify_total_card_update(inter, total):
            return

        progress_bar = "                    "
        percent = 0
        embed_start = emb_updateAllCards_processbar(progress_bar, percent)
        progress_message = await inter.send(embed=embed_start, ephemeral=True)

        for index, card in enumerate(cards_data.data, start=1):
            select_menu_id = card["select_menu_id"]
            owner_id = card["owner"]
            members = card["members"]
            number = card["number"]
            type = card["type"]
            name = card["name"]
            full_number = f"{suffixes.get(type, type)}{number}"
            card_type_rus = type_translate.get(type, type)

            if not isinstance(members, dict):  # Проверяем, если это не словарь (jsonb)
                members = {}

            owner_name = card["nickname"]
            channels_list = list(map(int, card["channels"].strip("[]").split(",")))
            channel_id = channels_list[1]
            channel = self.client.get_channel(channel_id)

            try:
                message = await channel.fetch_message(select_menu_id)
                if not message:
                    print(f"⚠ Сообщение {select_menu_id} не найдено.")
                    continue

                existing_embeds = message.embeds
                if len(existing_embeds) < 3:
                    print(f"⚠ У сообщения {select_menu_id} нет 3 эмбедов.")
                    continue
                
                second_embed = existing_embeds[1]
                color = existing_embeds[0].color
                new_card_embed = emb_cards(color, full_number, card_type_rus, name) 
                card_embed_user = emb_cards_users(inter.guild, color, owner_name, members)
                await message.edit(embeds=[new_card_embed, second_embed, card_embed_user], attachments=[])

                # Обновляем все сообщения пользователей
                if members:
                    for user_id, data in members.items():
                        msg_id = data.get("id_message")
                        channel_id = data.get("id_channel")
                        channel = inter.client.get_channel(channel_id) 
                        message_users = await channel.fetch_message(msg_id)
                        await message_users.edit(embeds=[new_card_embed, second_embed, card_embed_user], attachments=[], view=CardSelectView())

            except nxc.NotFound:
                print(f"❌ Сообщение {select_menu_id} не найдено в {channel.name}, удаляем из базы.")
                db_cursor("cards").delete().eq("select_menu_id", select_menu_id).execute()
            except nxc.HTTPException as e:
                print(f"❌ Ошибка при обновлении {select_menu_id}: {e}")

            percent = int((index / total) * 100)
            progress_bar = "▓" * (percent // 5) + "░" * (20 - (percent // 5))
            embed_progress = emb_updateAllCards_processbar(progress_bar, percent)
            await progress_message.edit(embed=embed_progress)

        title_emb, message_emb, color_emb = get_message_with_title(
            1, (), ())
        embed_finish = emb_auto(title_emb, message_emb, color_emb)
        await progress_message.edit(embed=embed_finish)

        #Аудит действия
        member_audit = inter.guild.get_channel(bank_audit_channel)

        title_emb, message_emb, color_emb = get_message_with_title(
            62, (), (admin.id))
        embed_aud_updateAllCards = emb_auto(title_emb, message_emb, color_emb)   
        await member_audit.send(embed=embed_aud_updateAllCards)

def setup(client):
    client.add_cog(UpdateAllCards(client))
