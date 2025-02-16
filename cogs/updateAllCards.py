import nextcord as nxc
from nextcord.ext import commands
from const import *
from modules import *
import asyncio
import json

command = "/updateAllCards"

class UpdateAllCards(commands.Cog):
    def __init__(self, client):
        self.client = client

    @nxc.slash_command(guild_ids=server_id, name="updateallcards", description="Обновить информацию обо всех созданных картах")
    async def updateAllCards(self, inter: nxc.Interaction):
        admin = inter.user
        if not await verify_staff(inter, admin, command):
            return

        await inter.response.defer(ephemeral=True)
        self.client.add_view(CardSelectView())

        cards_data = supabase.table("cards").select("select_menu_id, owner, number, members, type, name, clients(channels, nickname)").execute()
        total = len(cards_data.data)
        if total == 0:
            return await inter.send("⚠ Нет карт для обновления.", ephemeral=True)

        progress_bar = "                    "
        percent = 0
        embed1 = emb_updateAllCards_processbar(progress_bar, percent)
        progress_message = await inter.send(embed=embed1, ephemeral=True)

        for index, card in enumerate(cards_data.data, start=1):
            select_menu_id = card["select_menu_id"]
            owner_id = card["owner"]
            number = card["number"]
            type = card["type"]
            name = card["name"]
            members = card["members"]
            full_number = f"{suffixes.get(type, type)}{number}"
            card_type_rus = type_translate.get(type, type)

            client_data = card.get("clients")
            if not client_data:
                print(f"❌ Клиент {owner_id} не найден в таблице clients.")
                continue

            owner_name = client_data["nickname"]
            channels_list = list(map(int, client_data["channels"].strip("[]").split(",")))
            channel_id = channels_list[1]
            channel = self.client.get_channel(channel_id)

            if not channel:
                print(f"❌ Канал {channel_id} не найден.")
                continue

            try:
                message = await channel.fetch_message(select_menu_id)
                if not message:
                    print(f"⚠ Сообщение {select_menu_id} не найдено.")
                    continue

                existing_embeds = message.embeds
                if not existing_embeds:
                    print(f"⚠ У сообщения {select_menu_id} нет эмбедов.")
                    continue

                card_embed = existing_embeds[0]

                # Проверяем изображение перед обновлением
                old_image_url = card_embed.image.url if card_embed.image else None
                if not old_image_url:
                    print(f"⚠ Изображение отсутствует у карты {select_menu_id}, возможно, Discord его удалил.")

                color = card_embed.color

                # Создаём новый эмбед
                new_card_embed = e_cards(color, full_number, card_type_rus, name, image=None)

                # Восстанавливаем изображение
                if old_image_url:
                    new_card_embed.set_image(url=old_image_url)
                else:
                    print(f"⚠ Картинка для {select_menu_id} не была установлена.")

                if isinstance(members, str):
                    members = json.loads(members)
                # Создаём второй эмбед
                card_embed_user = e_cards_users(inter, color, owner_name, members)

                # Добавляем небольшую задержку перед обновлением
                await asyncio.sleep(0.2)

                # Обновляем сообщение
                await message.edit(embeds=[new_card_embed, card_embed_user], attachments=[])

                # Проверяем изображение после обновления
                updated_message = await channel.fetch_message(select_menu_id)
                updated_embed = updated_message.embeds[0] if updated_message.embeds else None
                updated_image_url = updated_embed.image.url if updated_embed and updated_embed.image else None

                if not updated_image_url:
                    print(f"❌ Изображение пропало после обновления {select_menu_id}!")

            except nxc.NotFound:
                print(f"❌ Сообщение {select_menu_id} не найдено в {channel.name}, удаляем из базы.")
                supabase.table("cards").delete().eq("select_menu_id", select_menu_id).execute()
            except nxc.HTTPException as e:
                print(f"❌ Ошибка при обновлении {select_menu_id}: {e}")

            percent = int((index / total) * 100)
            progress_bar = "▓" * (percent // 5) + "░" * (20 - (percent // 5))
            embed1 = emb_updateAllCards_processbar(progress_bar, percent)
            await progress_message.edit(embed=embed1)

        embed2 = emb_updateAllCards()
        await progress_message.edit(embed=embed2)

def setup(client):
    client.add_cog(UpdateAllCards(client))
