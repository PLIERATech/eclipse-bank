import nextcord as nxc
from nextcord.ext import commands
from const import *
from modules import *

command = "/Total-balance"

class TotalBalance(commands.Cog):
    def __init__(self, client):
        self.client = client
        
    @nxc.slash_command(guild_ids=server_id, name="totalbalance", description="The amount of money stored on the server", default_member_permissions=nxc.Permissions(administrator=True))
    async def totalBalance(
        self, 
        inter: nxc.Interaction
    ):
        admin = inter.user
        admin_nick = inter.user.display_name
        admin_id = inter.user.id

        # Проверка прав staff
        if not await verify_staff(inter, admin, command):
            return
        
        await inter.response.defer(ephemeral=True)
        
        total_balance = supabase.rpc("get_total_balance").execute()

        embed=emb_total_balance(total_balance.data)
        await inter.send(embed=embed, ephemeral=True)

def setup(client):
    client.add_cog(TotalBalance(client))