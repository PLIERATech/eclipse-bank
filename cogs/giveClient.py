import nextcord as nxc
from nextcord.ext import commands
from const import *
from modules import *
from db import *

command = "/выдать-клиента"

class SetClient(commands.Cog):
    def __init__(self, client):
        self.client = client
        
    @nxc.slash_command(guild_ids=server_id, name="выдать-клиента", description="Сделать клиентом Eclipse Bank")
    async def setClient(
        self, 
        inter: nxc.Interaction, 
        member: nxc.Member
    ):
        banker_id = inter.user.id
        banker_name = inter.user.display_name
        member_name = member.display_name
        member_id = member.id
        guild = inter.guild

        # Проверка прав banker
        if not await verify_this_banker(inter, command, inter.user, True):
            return

        # Проверка находится ли человек на сервере\
        if not await verify_user_in_server(inter, member):
            return

#// Действие

        await inter.response.defer(ephemeral=True)

        #=Создание клиента
        answer_account = await createAccount(guild, member, banker_id)

        # Проверка состан ли уже аккаунт
        if not answer_account:
            title_emb, message_emb, color_emb = get_message_with_title(
                79, (), (member_id))
            embed_answer_account = emb_auto(title_emb, message_emb, color_emb)
            await inter.send(embed=embed_answer_account, ephemeral=True)
            return

        title_emb, message_emb, color_emb = get_message_with_title(
            80, (), (member_id))
        embed_set_account = emb_auto(title_emb, message_emb, color_emb)
        await inter.send(embed=embed_set_account, ephemeral=True)

def setup(client):
    client.add_cog(SetClient(client))