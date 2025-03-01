import nextcord as nxc
from nextcord.ext import commands
from const import *
from modules import *
from db import *

command = "/создать"

class NewCard(commands.Cog):
    def __init__(self, client):
        self.client = client
        
    @nxc.slash_command(guild_ids=server_id, name="создать", description="Создать карту Eclipse Bank")
    async def newCard(
        self, 
        inter: nxc.Interaction, 
        member: nxc.Member, 
        type: str = nxc.SlashOption(name="card_type", description="Choose 1", required=True, choices=bankerCardType), 
        color: str= nxc.SlashOption(name="card_color", description="Choose 1", required=True,choices=choice_color)
    ):
        
        oneLog(f"{inter.user.display_name} написал команду {command}")

        banker_id = inter.user.id
        banker_name = inter.user.display_name
        member_name = member.display_name
        member_id = member.id
        guild = inter.guild
        card_type_rus = type_translate.get(type, type)

        # Проверка прав banker
        if not await verify_this_banker(inter, command, inter.user, True):
            return

        # Проверка находится ли человек на сервере\
        if not await verify_user_in_server(inter, member):
            return

#// Действие

        await inter.response.defer(ephemeral=True)

        #=Создание клиента
        await createAccount(guild, member, banker_id)

        # Проверка на исчерпание лимита создания карт
        if not await verify_count_cards(inter, member_id, command):
            return

        #=Создание карты
        check_create_card = await create_card(banker_name, member_name, member_name, type, member_id, color, True, "0", "0")
        # Проверка получилось ли создать карту
        if not await verify_create_card(inter, check_create_card[1]):
            return
        
        full_number = check_create_card[0]
        await next_create_card(inter, member, full_number, card_type_rus, color, member_name)

        status="Success"
        PermsLog(banker_name, banker_id, command, status)

        #Аудит действия
        member_audit = inter.guild.get_channel(bank_audit_channel)
        title_emb, message_emb, color_emb = get_message_with_title(
            53, (), (full_number, member_id, banker_id))
        embed_aud_createCard = emb_auto(title_emb, message_emb, color_emb)
        await member_audit.send(embed=embed_aud_createCard)

        oneLog(f"{command} написанная {inter.user.display_name} успешно выполнена")


def setup(client):
    client.add_cog(NewCard(client))