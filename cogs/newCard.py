import nextcord as nxc
from nextcord.ext import commands
from const import *
from log_functions import *
from modules import *
import asyncio
import os

command = "/создать"

TYPE_TRANSLATION = {
    "private": "Личная",
    "team": "Общины",
    "banker": "Банкира"
}

class NewCard(commands.Cog):
    def __init__(self, client):
        self.client = client
        
    @nxc.slash_command(guild_ids=server_id, name="создать", description="Создать карту Eclipse Bank")
    async def newCard(self, inter: nxc.Interaction, owner: nxc.Member, type: str = nxc.SlashOption(
        name="card_type",
        description="Choose 1",
        required=True,
        choices=["private", "team"]
    ), color: str= nxc.SlashOption(
        name="card_color",
        description="Choose 1",
        required=True,
        choices=["black", "white", "red", "orange", "yellow", "green", "blue", "purple"]
    )):
        banker_id = inter.user.id
        banker = inter.user.display_name
        nickname = inter.user.display_name
        card_name = owner.display_name
        owner_id = owner.id
        guild = inter.guild

        #Проверка прав banker
        if not any(role.id in (banker_role) for role in inter.user.roles):
            status="No Permissions"
            await inter.response.send_message("❗ У вас недостаточно прав для использования данной команды.", ephemeral=True)
            PermsLog(nickname, banker_id, command, status) 
            return
        
#// Действие

        status="Success"
        PermsLog(nickname, banker_id, command, status)

        embed_color = None

        colors = {
            "red": nxc.Colour.from_rgb(182, 79, 81),
            "orange": nxc.Colour.from_rgb(220, 130, 82),
            "yellow": nxc.Colour.from_rgb(223, 186, 66),
            "green": nxc.Colour.from_rgb(146, 182, 79),
            "blue": nxc.Colour.from_rgb(79, 139, 182),
            "purple": nxc.Colour.from_rgb(137, 79, 182),
            "black": nxc.Colour.from_rgb(41, 41, 41),
            "white": nxc.Colour.from_rgb(245, 245, 245)
        }

        await inter.response.defer(ephemeral=True)

        #=Создание клиента
        await createAccount(guild, owner)

        #=Создание карты
        full_number = create_card(banker, card_name, type, owner_id, color, do_random=True, adm_number="0")
        card_type_rus = TYPE_TRANSLATION.get(type, type)
        card_image = f"{full_number}.png"
        embed_color = colors.get(color, color)

        await inter.followup.send(content=f"Карта типа {card_type_rus} с номером {full_number} успешно создана!")
        await asyncio.sleep(2)

        card = nxc.File(f"card_gen/cards/{card_image}", filename=card_image)

        card_embed = nxc.Embed(color=embed_color)
        card_embed.add_field(name="💳 Карта:", value=full_number, inline=True)
        card_embed.add_field(name="🗂️ Тип:", value=card_type_rus, inline=True)
        card_embed.add_field(name="💬 Название", value=card_name, inline=True)
        card_embed.set_image(url=f"attachment://{card_image}")
        card_embed.set_footer(text="Eclipse Bank 2025")

        response = supabase.table("clients").select("*").eq("dsc_id", owner_id).execute()

        channels_response = response.data[0]["channels"]
        channels = list(map(int, channels_response.strip("[]").split(",")))
        cards_channel_id = int(channels[2])
        cards_channel = inter.guild.get_channel(cards_channel_id)

        # Создание Select Menu
        view = nxc.ui.View()
        view.add_item(create_select_menu("card_transaction"))
        view.add_item(create_select_menu("card_settings"))

        # После отправки сообщения с select menu
        message_card = await cards_channel.send(content=f"{owner.mention}", embed=card_embed, file=card, view=view)

        #Получаем только цифры созданной карты / Удаляем все символы, кроме цифр
        card_numbers = full_number.translate(str.maketrans("", "", "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-"))
        supabase.table("cards").update({"select_menu_id": message_card.id}).eq("number", card_numbers).execute()


def setup(client):
    client.add_cog(NewCard(client))