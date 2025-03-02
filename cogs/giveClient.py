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
        
        oneLog(f"{inter.user.display_name} написал команду {command}")  

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

        banker_data = db_rpc("get_banker_card", {"user_id": banker_id}).execute()

        # Проверяет, есть ли карта у банкира
        if not await verify_found_banker_card(inter, banker_data):
            return
        
        banker_card_type = banker_data.data[0]["type"]
        banker_card_number = banker_data.data[0]["number"]
        banker_card_balance = banker_data.data[0]["balance"]
        banker_card_full_number = f"{suffixes.get(banker_card_type, banker_card_type)}{banker_card_number}"
        banker_card_channel_id = banker_data.data[0]["banker_account"]
        banker_tranaction_channel_id = banker_data.data[0]["banker_transactions"]
        salary = 1

        #=Создание клиента
        answer_account = await createAccount(guild, member, banker_id)

        # Проверка состан ли уже аккаунт
        if not answer_account:
            title_emb, message_emb, color_emb = get_message_with_title(
                79, (), (member_id))
            embed_answer_account = emb_auto(title_emb, message_emb, color_emb)
            await inter.send(embed=embed_answer_account, ephemeral=True)
            return

        # Отправка сообщений в каналы транзакций
        embed_replenish_banker = emb_give_client_banker(banker_card_full_number, salary)
        banker_card_channel = inter.client.get_channel(banker_card_channel_id)
        banker_transaction_channel = banker_card_channel.get_thread(banker_tranaction_channel_id)
        await banker_transaction_channel.send(embed=embed_replenish_banker)

        db_cursor("cards").update({"balance": banker_card_balance + salary}).eq("number", banker_card_number).execute()

        #Аудит дейтсвия
        title_emb, message_emb, color_emb = get_message_with_title(
            80, (), (member_id))
        embed_set_account = emb_auto(title_emb, message_emb, color_emb)
        await inter.send(embed=embed_set_account, ephemeral=True)

        banker_audit = inter.guild.get_channel(banker_invoice_channel_id)
        embed_banker_aud = emb_banker_chat_give_client(banker_id, member_id, banker_card_full_number, salary)
        await banker_audit.send(embed=embed_banker_aud)

        oneLog(f"{command} написанная {inter.user.display_name} успешно выполнена")


def setup(client):
    client.add_cog(SetClient(client))