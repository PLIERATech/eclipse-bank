import nextcord as nxc
from nextcord.ext import commands
from const import *
from log_functions import *

class Admit(commands.Cog):
    def __init__(self, client):
        self.client = client
        
    @nxc.slash_command(guild_ids=server_id, name="принять", description="принять банкира на работу")
    async def admit(self, inter: nxc.Interaction, member: nxc.Member):
        user_id = inter.user.id
        nickname = inter.user.display_name

        #Проверка прав staff
        if not any(role.id in (staff) for role in inter.user.roles):
            status="No Permissions"
            await inter.response.send_message("❗ У вас недостаточно прав для использования данной команды.", ephemeral=True)
            admit_Log(nickname, user_id, status)
            return
        
        #// Действие
        # await inter.response.send_message(f"СОСАЛ? \n {member.mention}", ephemeral=True)

        status="Success"
        admit_Log(nickname, user_id, status)


def setup(client):
    client.add_cog(Admit(client))