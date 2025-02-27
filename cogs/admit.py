import nextcord as nxc
from nextcord.ext import commands
from const import *
from modules import *
from db import *

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
        card_type_rus = type_translate.get(type, type)
        color = type

        # Проверка прав staff
        if not await verify_staff(inter, admin, command):
            return
        
        # Проверка находится ли человек на сервере
        if not await verify_user_in_server(inter, member):
            return

        # Проверка не является ли пользователь уже банкир
        if not await verify_dont_banker(inter, member, command):
            return

        await inter.response.defer(ephemeral=True)

        # Создается клиент
        await createAccount(guild, member, admin_id)
        if not member_id in ignore_members:
            db_cursor("clients").update({"count_cards": 4}).eq("dsc_id", member_id).execute()


        #=Создание карты банкира
        check_create_card = await create_card(admin_nick, "Зарплатная", member_nick, type, member_id, color, True, "0", "0")
        
         # Проверка получилось ли создать карту
        if not await verify_create_card(inter, check_create_card[1]):
            return
        
        full_number = check_create_card[0]

        await next_create_card(inter, member, full_number, card_type_rus, color, "Зарплатная")

        #// Действие        
        invite_team(member_id)

        banker_role_add = inter.guild.get_role(banker_role_id)

        await member.add_roles(banker_role_add)
        
        status="Success"
        PermsLog(admin_nick, admin_id, command, status)

        #Аудит действия
        member_audit = inter.guild.get_channel(bank_audit_channel)
        title_emb, message_emb, color_emb = get_message_with_title(
            54, (), (member_id, full_number, admin_id))
        embed_aud_admitBanker = emb_auto(title_emb, message_emb, color_emb)
        await member_audit.send(embed=embed_aud_admitBanker)        


def setup(client):
    client.add_cog(Admit(client))