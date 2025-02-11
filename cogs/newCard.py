import nextcord as nxc
from nextcord.ext import commands
from const import *
from log_functions import *
from services import *
from account import *

command = "/создать"

TYPE_TRANSLATION = {
    "Private": "Личная",
    "Team": "Общины",
    "Banker": "Банкира"
}

class NewCard(commands.Cog):
    def __init__(self, client):
        self.client = client
        
    @nxc.slash_command(guild_ids=server_id, name="создать", description="Создать карту Eclipse Bank")
    async def newCard(self, inter: nxc.Interaction, owner: nxc.Member, type: str = nxc.SlashOption(
        name="card_type",
        description="Choose 1",
        required=True,
        choices=["private", "team"]
    )):
        banker_id = inter.user.id
        banker = inter.user.display_name
        nickname = inter.user.display_name
        card_name = owner.display_name
        owner_id = owner.id
        guild = inter.guild

        #Проверка прав banker
        if not any(role.id in (banker_role) for role in inter.user.roles):
            status="No Permissions"
            await inter.response.send_message("❗ У вас недостаточно прав для использования данной команды.", ephemeral=True)
            PermsLog(nickname, banker_id, command, status) 
            return
        
#// Действие

        status="Success"
        PermsLog(nickname, banker_id, command, status)

        #=Создание карты
        full_number = create_card(banker, card_name, type, owner_id)
        card_type_rus = TYPE_TRANSLATION.get(type, type)
        await inter.response.send_message(f"Карта типа {card_type_rus} с номером {full_number} успешно создана!", ephemeral=True)
        #=Создание клиента
        await createAccount(guild, owner)



def setup(client):
    client.add_cog(NewCard(client))