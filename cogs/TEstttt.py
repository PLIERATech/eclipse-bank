import nextcord as nxc
from nextcord.ext import commands
from const import *

class CheckMember(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nxc.slash_command(guild_ids=server_id, name="check", description="Проверяет, есть ли указанный пользователь на сервере")
    async def check(self, inter: nxc.Interaction, member: nxc.Member = None):

        guild = inter.guild
        
        if guild.get_member(member.id):
            await inter.response.send_message(f"✅ {member.mention} найден на сервере!", ephemeral=True)
        else:
            await inter.response.send_message("❌ Этот пользователь **не находится** на сервере!", ephemeral=True)


def setup(bot):
    bot.add_cog(CheckMember(bot))
