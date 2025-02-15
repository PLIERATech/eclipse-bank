import nextcord as nxc
from nextcord.ext import commands
from const import *
from modules import *
import asyncio

command = "/admCreate"

class AdmCreate(commands.Cog):
    def __init__(self, client):
        self.client = client
        
    @nxc.slash_command(guild_ids=server_id, name="admcreate", description="Admin Unit Creation")
    async def admcreate(
        self, inter: nxc.Interaction, 
        member: nxc.Member, 
        number: int, 
        name: str, 
        type: str = nxc.SlashOption(name="card_type", description="Choose 1", required=True, choices=admCardTypes), 
        color: str= nxc.SlashOption(name="card_color", description="Choose 1", required=True, choices=choice_color)
    ):
        # Вспомогательные параметры
        admin = inter.user
        admin_id = inter.user.id
        admin_nickname = inter.user.display_name
        member_id = member.id       
        member_nickname = member.display_name

        card_type_rus = type_translate.get(type, type)
        if type == "💎 CEO": color = "💎 CEO"

        # Проверка прав staff
        if not await verify_staff(inter, admin, command):
            return
        
        # Проверка находится ли человек на сервере
        if not await verify_user_in_server(inter, member):
            return

        # Проверка написания числа
        if not await verify_number_lenght(inter, number):
            return
        number = f"{number:05}"

        # Проверка занятости номера карты
        if not await verify_num_is_claimed(inter, number):
            return


#// Действие

        await inter.response.defer(ephemeral=True)

        #=Создание клиента
        await createAccount(inter.guild, member)

        # Проверка на исчерпание лимита создания карт
        if not verify_count_cards(inter, member_id, command):
            return

        #=Создание карты
        check_create_card = create_card(admin_nickname, name, member_nickname, type, member_id, color, False, number, "0")
        # Проверка получилось ли создать карту
        if not await verify_create_card(inter, check_create_card[1]):
            return
        
        full_number = check_create_card[0]
        await next_create_card(inter, member, full_number, card_type_rus, color, name)

        status="Success"
        PermsLog(admin_nickname, admin_id, command, status)


def setup(client):
    client.add_cog(AdmCreate(client))