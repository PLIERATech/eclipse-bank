import nextcord as nxc
from nextcord.ext import commands
from const import *
from modules import *

command = "/принять"

class Admit(commands.Cog):
    def __init__(self, client):
        self.client = client
        
    @nxc.slash_command(guild_ids=server_id, name="принять", description="принять банкира на работу")
    async def admit(
        self, 
        inter: nxc.Interaction, 
        member: nxc.Member
    ):
        
        admin = inter.user
        admin_id = inter.user.id
        admin_nick = inter.user.display_name
        member_nick = member.display_name
        member_id = member.id
        guild = inter.guild
        type = admCardTypes[2]

        # Проверка прав staff
        if not await verify_staff(inter, admin, command):
            return
        
        # Проверка находится ли человек на сервере
        if not await verify_user_in_server(inter, member):
            return

        #Проверка не является ли пользователь уже банкир
        if any(role.id in (banker_role) for role in member.roles):
            status="isBanker"
            embed = user_isBanker()
            await inter.response.send_message(embed=embed, ephemeral=True)
            PermsLog(admin_nick, admin_id, command, status)
            return

        await inter.response.defer(ephemeral=True)

        #Создается клиент
        await createAccount(guild, member)
        if not member_id in ignore_members:
            supabase.table("clients").update({"count_cards": 3}).eq("dsc_id", member_id).execute()


        #=Создание карты банкира
        check_create_card = create_card(admin_nick, "Зарплатная", member_nick, type, member_id, "🔴 Red", True, "0", "0")
        if not check_create_card[1]:
            embed = sb_cardNotCreated()
            await inter.followup.send(embed=embed, ephemeral=True)
            return
        full_number = check_create_card[0]
        card_type_rus = "Банкира"
        card_image = f"{full_number}.png"

        await inter.followup.send(content=f"Карта типа {card_type_rus} с номером {full_number} успешно создана!")
        await asyncio.sleep(2)

        card = nxc.File(f"card_gen/cards/{card_image}", filename=card_image)
        card_embed = e_cards("💸 Banker",full_number,card_type_rus,"Зарплатная",card_image)

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
        invite_team(member_id)

        banker_role_add = inter.guild.get_role(banker_role_id)

        await member.add_roles(banker_role_add)
        
        status="Success"
        PermsLog(admin_nick, admin_id, command, status)


def setup(client):
    client.add_cog(Admit(client))