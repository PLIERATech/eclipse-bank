import nextcord as nxc
from nextcord.ext import commands
from const import *
from modules import *
import asyncio

command = "/admCreate"

TYPE_TRANSLATION = {
    "personal": "Личная",
    "team": "Общины",
    "banker": "Банкира",
    "cio": "CIO"
}

class AdmCreate(commands.Cog):
    def __init__(self, client):
        self.client = client
        
    @nxc.slash_command(guild_ids=server_id, name="admcreate", description="Admin Unit Creation")
    async def admcreate(self, inter: nxc.Interaction, owner: nxc.Member, number: int, name: str, type: str = nxc.SlashOption(name="card_type",description="Choose 1",required=True,choices=["personal", "team", "banker", "cio"]), color: str= nxc.SlashOption(name="card_color",description="Choose 1",required=True,choices=["black", "white", "red", "orange", "yellow", "green", "blue", "purple"])):
        
        admin = inter.user
        admin_id = inter.user.id
        admin_nickname = inter.user.display_name
        
        card_name = owner.display_name
        owner_id = owner.id

        guild = inter.guild

        #Проверка прав staff
        if not any(role.id in (staff_role) for role in admin.roles):
            status="No Permissions"
            await inter.response.send_message("❗ У вас недостаточно прав для использования данной команды.", ephemeral=True)
            PermsLog(admin_nickname, admin_id, command, status) 
            return
        
        number_str = str(number)
        if number < 0 or number > 99999:
            await inter.response.send_message("Параметр `number` должен быть числом из ровно 5 цифр.", ephemeral=True)
            return
        number_str = f"{number:05}"

        #Проверка занят ли номер карты
        response = supabase.table("cards").select("number").execute()
        numbers_list = [item["number"] for item in response.data]
        if number_str in numbers_list:
            await inter.response.send_message("Данный номер карты уже занят.", ephemeral=True)
            return


#// Действие

        status="Success"
        PermsLog(admin_nickname, admin_id, command, status)

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
        full_number = create_card(admin_nickname, name, card_name, type, owner_id, color, do_random=False, adm_number=number_str)
        card_type_rus = TYPE_TRANSLATION.get(type, type)
        card_image = f"{full_number}.png"
        embed_color = colors.get(color, color)
        if type == "cio": embed_color = nxc.Colour.from_rgb(5, 170, 156)
        await inter.followup.send(content=f"Карта типа {card_type_rus} с номером {full_number} успешно создана!")
        await asyncio.sleep(2)

        card = nxc.File(f"card_gen/cards/{card_image}", filename=card_image)

        card_embed = nxc.Embed(color=embed_color)
        card_embed.add_field(name="💳 Карта:", value=full_number, inline=True)
        card_embed.add_field(name="🗂️ Тип:", value=card_type_rus, inline=True)
        card_embed.add_field(name="💬 Название", value=name, inline=True)
        card_embed.set_image(url=f"attachment://{card_image}")
        card_embed.set_footer(text="Eclipse Bank 2025")

        response = supabase.table("clients").select("*").eq("dsc_id", owner_id).execute()

        channels_response = response.data[0]["channels"]
        channels = list(map(int, channels_response.strip("[]").split(",")))
        cards_channel_id = int(channels[1])
        cards_channel = inter.guild.get_channel(cards_channel_id)

        view = CardSelectView()  # Используем уже готовый View
        
        message_card = await cards_channel.send(content=f"{owner.mention}", embed=card_embed, file=card, view=view)

        #Получаем только цифры созданной карты / Удаляем все символы, кроме цифр
        card_numbers = full_number.translate(str.maketrans("", "", "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-"))
        supabase.table("cards").update({"select_menu_id": message_card.id}).eq("number", card_numbers).execute()


def setup(client):
    client.add_cog(AdmCreate(client))