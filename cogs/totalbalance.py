import nextcord as nxc
from nextcord.ext import commands
from const import *
from modules import *
from db import *

command = "/Total-balance"

class TotalBalance(commands.Cog):
    def __init__(self, client):
        self.client = client
        
    @nxc.slash_command(guild_ids=server_id, name="totalbalance", description="The amount of money stored on the server", default_member_permissions=nxc.Permissions(administrator=True))
    async def totalBalance(
        self, 
        inter: nxc.Interaction
    ):
        
        oneLog(f"{inter.user.display_name} написал команду {command}")

        admin = inter.user
        admin_nick = inter.user.display_name
        admin_id = inter.user.id

        # Проверка прав staff
        if not await verify_staff(inter, admin, command):
            return
        
        await inter.response.defer(ephemeral=True)
        
        total_balance = db_rpc("get_total_balance", {}).execute()

        total = total_balance.data[0]["get_total_balance"]
        title_emb, message_emb, color_emb = get_message_with_title(
            2, (), (total, total // 9, total - (total // 9 * 9)))
        embed = emb_auto(title_emb, message_emb, color_emb)
        await inter.send(embed=embed, ephemeral=True)

        oneLog(f"{command} написанная {inter.user.display_name} успешно выполнена")


def setup(client):
    client.add_cog(TotalBalance(client))