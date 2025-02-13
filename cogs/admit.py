import nextcord as nxc
from nextcord.ext import commands
from const import *
from modules import *

command = "/принять"
type = "banker"

ignore_members = [436507782263603200]
# ignore_members = [436507782263603200, 187208294161448960]

class Admit(commands.Cog):
    def __init__(self, client):
        self.client = client
        
    @nxc.slash_command(guild_ids=server_id, name="принять", description="принять банкира на работу")
    async def admit(self, inter: nxc.Interaction, member: nxc.Member):

        user_id = inter.user.id
        admin = inter.user.display_name
        member_nick = member.display_name
        member_id = member.id
        guild = inter.guild

        #Проверка прав staff
        if not any(role.id in (staff_role) for role in inter.user.roles):
            status="No Permissions"
            await inter.response.send_message("❗ У вас недостаточно прав для использования данной команды.", ephemeral=True)
            PermsLog(admin, user_id, command, status)
            return
        
        #Проверка не является ли пользователь уже банкир
        if any(role.id in (banker_role) for role in member.roles):
            status="isBanker"
            await inter.response.send_message("❗ Данный пользователь уже является банкиром.", ephemeral=True)
            PermsLog(admin, user_id, command, status)
            return

        await inter.response.defer(ephemeral=True)

        #Создается клиент
        await createAccount(guild, member)
        if not member_id in ignore_members:
            supabase.table("clients").update({"count_cards": 3}).eq("dsc_id", member_id).execute()


        #=Создание карты банкира
        full_number = create_card(admin, "Зарплатная", member_nick, type, member_id, "red", do_random=True, adm_number="0")
        card_type_rus = "Банкира"
        card_image = f"{full_number}.png"

        await inter.followup.send(content=f"Карта типа {card_type_rus} с номером {full_number} успешно создана!")
        await asyncio.sleep(2)

        card = nxc.File(f"card_gen/cards/{card_image}", filename=card_image)

        card_embed = nxc.Embed(color=nxc.Colour.from_rgb(31, 31, 31))
        card_embed.add_field(name="💳 Карта:", value=full_number, inline=True)
        card_embed.add_field(name="🗂️ Тип:", value=card_type_rus, inline=True)
        card_embed.add_field(name="💬 Название", value=member_nick, inline=True)
        card_embed.set_image(url=f"attachment://{card_image}")
        card_embed.set_footer(text="Eclipse Bank 2025")

        response = supabase.table("clients").select("*").eq("dsc_id", member_id).execute()

        channels_response = response.data[0]["channels"]
        channels = list(map(int, channels_response.strip("[]").split(",")))
        cards_channel_id = int(channels[1])
        cards_channel = inter.guild.get_channel(cards_channel_id)

        view = CardSelectView()  # Используем уже готовый View
        
        message_card = await cards_channel.send(content=f"{member.mention}", embed=card_embed, file=card, view=view)

        #Получаем только цифры созданной карты / Удаляем все символы, кроме цифр
        card_numbers = full_number.translate(str.maketrans("", "", "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-"))
        supabase.table("cards").update({"select_menu_id": message_card.id}).eq("number", card_numbers).execute()

        #// Действие        
        invite(member_id)

        banker_role_add = inter.guild.get_role(banker_role_id)

        await member.add_roles(banker_role_add)
        
        status="Success"
        PermsLog(admin, user_id, command, status)


def setup(client):
    client.add_cog(Admit(client))