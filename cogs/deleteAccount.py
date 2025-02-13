import nextcord as nxc
from nextcord.ext import commands
from const import *
from modules import *

command = "/удалить"

class DelClient(commands.Cog):
    def __init__(self, client):
        self.client = client
        
    @nxc.slash_command(guild_ids=server_id, name="удалить", description="Удалить счёт Eclipse Bank ")
    async def delClient(self, inter: nxc.Interaction, owner: nxc.Member):

        guild = inter.guild
        
        await deleteAccount(guild, owner)

        await inter.response.send_message("ok", ephemeral=True)

def setup(client):
    client.add_cog(DelClient(client))