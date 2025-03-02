import nextcord as nxc
from nextcord.ext import commands
from const import *
from modules import *
from db import *

command = "/создать"

class NewCard(commands.Cog):
    def __init__(self, client):
        self.client = client
        
    @nxc.slash_command(guild_ids=server_id, name="создать", description="Создать карту Eclipse Bank")
    async def newCard(
        self, 
        inter: nxc.Interaction, 
        member: nxc.Member, 
        type: str = nxc.SlashOption(name="card_type", description="Choose 1", required=True, choices=bankerCardType), 
        color: str= nxc.SlashOption(name="card_color", description="Choose 1", required=True,choices=choice_color)
    ):
        
        oneLog(f"{inter.user.display_name} написал команду {command}")

        banker_id = inter.user.id
        banker_name = inter.user.display_name
        member_name = member.display_name
        member_id = member.id
        guild = inter.guild
        card_type_rus = type_translate.get(type, type)

        # Проверка прав banker
        if not await verify_this_banker(inter, command, inter.user, True):
            return

        # Проверка находится ли человек на сервере\
        if not await verify_user_in_server(inter, member):
            return

#// Действие

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
        count = 4
        commission = 2
        salary = 2

        await inter.response.defer(ephemeral=True)

        #=Создание клиента
        await createAccount(guild, member, banker_id)

        # Проверка на исчерпание лимита создания карт
        if not await verify_count_cards(inter, member_id, command):
            return

        #=Создание карты
        check_create_card = await create_card(banker_name, member_name, member_name, type, member_id, color, True, "0", "0")
        # Проверка получилось ли создать карту
        if not await verify_create_card(inter, check_create_card[1]):
            return
        
        full_number = check_create_card[0]
        await next_create_card(inter, member, full_number, card_type_rus, color, member_name)

        status="Success"
        PermsLog(banker_name, banker_id, command, status)

        # Отправка сообщений в каналы транзакций
        embed_replenish_ceo = emb_new_card_ceo(full_number, count, commission, banker_id)
        ceo_owner_card_channel = inter.client.get_channel(ceo_card_channel)
        ceo_owner_transaction_channel = ceo_owner_card_channel.get_thread(ceo_transaction_channel)
        await ceo_owner_transaction_channel.send(embed=embed_replenish_ceo)

        embed_replenish_banker = emb_new_card_banker(banker_card_full_number, salary)
        banker_card_channel = inter.client.get_channel(banker_card_channel_id)
        banker_transaction_channel = banker_card_channel.get_thread(banker_tranaction_channel_id)
        await banker_transaction_channel.send(embed=embed_replenish_banker)

        db_rpc("add_balance", {"card_number": "00000", "amount": commission}).execute()
        db_cursor("cards").update({"balance": banker_card_balance + salary}).eq("number", banker_card_number).execute()

        #Аудит действия
        member_audit = inter.guild.get_channel(bank_audit_channel)
        title_emb, message_emb, color_emb = get_message_with_title(
            53, (), (full_number, member_id, banker_id))
        embed_aud_createCard = emb_auto(title_emb, message_emb, color_emb)
        await member_audit.send(embed=embed_aud_createCard)

        banker_audit = inter.guild.get_channel(banker_invoice_channel_id)
        embed_banker_aud = emb_banker_chat_new_card(banker_id, member_id, full_number, banker_card_full_number, commission, salary)
        await banker_audit.send(embed=embed_banker_aud)

        oneLog(f"{command} написанная {inter.user.display_name} успешно выполнена")


def setup(client):
    client.add_cog(NewCard(client))