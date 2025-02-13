import nextcord as nxc
from nextcord.ext import commands
from const import *
from modules import *

command = "/принять"
type = "banker"

ignore_members = [436507782263603200]
# ignore_members = [436507782263603200, 187208294161448960]

class Admit(commands.Cog):
    def __init__(self, client):
        self.client = client
        
    @nxc.slash_command(guild_ids=server_id, name="принять", description="принять банкира на работу")
    async def admit(self, inter: nxc.Interaction, member: nxc.Member):

        user_id = inter.user.id
        admin = inter.user.display_name
        member_nick = member.display_name
        member_id = member.id
        guild = inter.guild

        #Проверка прав staff
        if not any(role.id in (staff_role) for role in inter.user.roles):
            status="No Permissions"
            await inter.response.send_message("❗ У вас недостаточно прав для использования данной команды.", ephemeral=True)
            PermsLog(admin, user_id, command, status)
            return
        
        #Проверка не является ли пользователь уже банкир
        if any(role.id in (banker_role) for role in member.roles):
            status="isBanker"
            await inter.response.send_message("❗ Данный пользователь уже является банкиром.", ephemeral=True)
            PermsLog(admin, user_id, command, status)
            return

        #Создается клиент
        await createAccount(guild, member)
        if not member_id in ignore_members:
            supabase.table("clients").update({"count_cards": 3}).eq("dsc_id", member_id).execute()

        #Выдается карточка банкира
        full_number = create_card(admin, "Зарплатная", member_nick, type, member_id, "red", do_random=True, adm_number="0")

        #// Действие        
        invite(member_id)

        banker_role_add = inter.guild.get_role(banker_role_id)

        await member.add_roles(banker_role_add)
        
        status="Success"
        PermsLog(admin, user_id, command, status)


def setup(client):
    client.add_cog(Admit(client))