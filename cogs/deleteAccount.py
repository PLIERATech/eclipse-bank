import nextcord as nxc
from nextcord.ext import commands
from const import *
from modules import *
from db import *

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
        member_id = member.id

        # Проверка прав staff
        if not await verify_staff(inter, admin, command):
            return
        
        await inter.response.defer(ephemeral=True)
        Check_delete = await deleteAccount(inter.guild, member)       
        
        # Проверка имеется ли аккаунт у пользователя
        if not await verify_deleteAccount(inter, Check_delete[0]):
            return
        
        embed=emb_account_wasDeleted()
        await inter.send(embed=embed, ephemeral=True)

        #Аудит действия
        member_audit = inter.guild.get_channel(bank_audit_channel)
        embed_aud_deleteAccount = emb_aud_deleteAccount(member_id, admin_id)
        await member_audit.send(embed=embed_aud_deleteAccount)       

def setup(client):
    client.add_cog(DelClient(client))