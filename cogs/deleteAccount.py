import nextcord as nxc
from nextcord.ext import commands
from const import *
from modules import *

command = "/удалить"

class DelClient(commands.Cog):
    def __init__(self, client):
        self.client = client
        
    @nxc.slash_command(guild_ids=server_id, name="удалить", description="Удалить счёт Eclipse Bank ")
    async def delClient(
        self, 
        inter: nxc.Interaction, 
        owner: nxc.Member
    ):
        admin = inter.user
        admin_nick = inter.user.display_name
        admin_id = inter.user.id

        # Проверка прав staff
        if not await verify_staff(inter, admin, command):
            return

        Check_delete = await deleteAccount(inter.guild, owner)       
        
        # Проверка имеется ли аккаунт у пользователя
        if await verify_deleteAccount(inter, Check_delete):
            return
        
        embed=account_wasDeleted()
        await inter.response.send_message(embed=embed, ephemeral=True)

def setup(client):
    client.add_cog(DelClient(client))