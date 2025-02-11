import nextcord as nxc
from nextcord.ext import commands
from const import *
from log_functions import *
from services import *
from api import *
from account import *

command = "/принять"
type = "banker"
class Admit(commands.Cog):
    def __init__(self, client):
        self.client = client
        
    @nxc.slash_command(guild_ids=server_id, name="принять", description="принять банкира на работу")
    async def admit(self, inter: nxc.Interaction, member: nxc.Member):
        user_id = inter.user.id
        admin = inter.user.display_name
        member_nick = member.display_name
        owner_id = member.id
        guild = inter.guild

        #Проверка прав staff
        if not any(role.id in (staff_role) for role in inter.user.roles):
            status="No Permissions"
            await inter.response.send_message("❗ У вас недостаточно прав для использования данной команды.", ephemeral=True)
            PermsLog(admin, user_id, command, status)
            return
        
        #Проверка не является ли пользователь уже банкир
        if not any(role.id in (banker_role) for role in member.roles):
            status="isBanker"
            await inter.response.send_message("❗ Данный пользователь уже является банкиром.", ephemeral=True)
            PermsLog(admin, user_id, command, status)
            return

        #Создается клиент
        await createAccount(guild, member)

        #Выдается карточка банкира
        full_number = create_card(admin, member_nick, type, owner_id)
        
        
        #// Действие        
        invite(member_nick)
        
        status="Success"
        PermsLog(admin, user_id, command, status)


def setup(client):
    client.add_cog(Admit(client))