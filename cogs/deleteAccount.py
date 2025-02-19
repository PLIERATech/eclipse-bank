import nextcord as nxc
from nextcord.ext import commands
from const import *
from modules import *

command = "/admDelClient"

class DelClient(commands.Cog):
    def __init__(self, client):
        self.client = client
        
    @nxc.slash_command(guild_ids=server_id, name="admdelclient", description="Delete user", default_member_permissions=nxc.Permissions(administrator=True))
    async def delClient(
        self, 
        inter: nxc.Interaction, 
        member: nxc.Member
    ):
        admin = inter.user
        admin_nick = inter.user.display_name
        admin_id = inter.user.id

        # Проверка прав staff
        if not await verify_staff(inter, admin, command):
            return
        
        await inter.response.defer(ephemeral=True)
        Check_delete = await deleteAccount(inter.guild, member)       
        
        # Проверка имеется ли аккаунт у пользователя
        if not await verify_deleteAccount(inter, Check_delete):
            return
        
        embed=account_wasDeleted()
        await inter.send(embed=embed, ephemeral=True)

def setup(client):
    client.add_cog(DelClient(client))