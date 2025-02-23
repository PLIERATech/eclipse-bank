import nextcord as nxc
from nextcord.ext import commands
from const import *
from modules import *

command = "/Пополнить"

class ReplenishMoney(commands.Cog):
    def __init__(self, client):
        self.client = client
        
    @nxc.slash_command(guild_ids=server_id, name="пополнить", description="пополнить баланс карты")
    async def replenishMoney(
        self, 
        inter: nxc.Interaction, 
        number: int = nxc.SlashOption(name="номер-карты", description="Номер карты", max_value=99999), 
        count: int = nxc.SlashOption(name="сумма", description="Сумма взноса", min_value=2, max_value=1000000), 
        description: str = nxc.SlashOption(name="комментарий", description="комментарий банкира", max_length=50)
    ):
        banker = inter.user
        banker_nick = inter.user.display_name
        banker_id = inter.user.id

        # Проверка прав banker
        if not await verify_this_banker(inter, command, inter.user, True):
            return
        
        # Проверка прав на взаимодействие с картой CEO-00000
        if not await verify_ceo_card(inter, banker, number):
            return

        # дописывает 0 в начало если длина числа < 5
        number = f"{number:05}"

        card_data = supabase.table("cards").select("type, balance, members, clients(channels)").eq("number", number).execute()

        # Проверяем, существует ли карта получателя
        if not await verify_found_card(inter, card_data):
            return

        card_type = card_data.data[0]["type"]
        card_balance = card_data.data[0]["balance"]
        card_members = card_data.data[0]["members"]
        card_client_data = card_data.data[0].get("clients")
        card_owner_transaction_channel_id = list(map(int, card_client_data["channels"].strip("[]").split(",")))[0]
        card_full_number = f"{suffixes.get(card_type, card_type)}{number}"

        if not isinstance(card_members, dict):  # Проверяем, если это не словарь (jsonb)
            card_members = {}
        
        banker_data = supabase.rpc("get_banker_card", {"user_id": banker_id}).execute()

        # Проверяет, есть ли карта у банкира
        if not await verify_found_banker_card(inter, banker_data):
            return
        
        banker_card_type = banker_data.data[0]["type"]
        banker_card_number = banker_data.data[0]["number"]
        banker_card_balance = banker_data.data[0]["balance"]
        banker_card_full_number = f"{suffixes.get(banker_card_type, banker_card_type)}{banker_card_number}"
        banker_tranaction_channel_id = banker_data.data[0]["banker_transactions"]

        cr1 = commission_replenish.get("1")
        cr2 = commission_replenish.get("2")
        cr3 = commission_replenish.get("3")

        if 1 < count <= cr1:
            commission = 0
            salary = 1
        elif cr1 < count <= cr2:
            commission = 1
            salary = 1
        elif cr2 < count <= cr3:
            commission = 2
            salary = 1
        else:
            commission = 2
            salary = 2

        total_amount = count - commission - salary

        embed_comp_replenish = emb_comp_replenish(card_full_number, count, commission, salary, total_amount, description, banker_id)
        await inter.send(embed=embed_comp_replenish, ephemeral=True)

        # Отправка сообщений в каналы транзакций
        embed_replenish_ceo = emb_replenish_ceo(card_full_number, count, commission, salary, total_amount, description, banker_id)
        ceo_owner_transaction_channel = inter.client.get_channel(bank_card_transaction)
        await ceo_owner_transaction_channel.send(embed=embed_replenish_ceo)

        embed_replenish_banker = emb_replenish_banker(banker_card_full_number, salary)
        banker_owner_transaction_channel = inter.client.get_channel(banker_tranaction_channel_id)
        await banker_owner_transaction_channel.send(embed=embed_replenish_banker)

        embed_replenish_user = emb_replenish_user(card_full_number, count, commission, salary, total_amount, description, banker_id)
        card_owner_transaction_channel = inter.client.get_channel(card_owner_transaction_channel_id)
        await card_owner_transaction_channel.send(embed=embed_replenish_user)

        for user_id, data in card_members.items():
            channel_id_transactions_card = data.get("id_transactions_channel")
            channel_transactions_card = inter.client.get_channel(channel_id_transactions_card)
            await channel_transactions_card.send(embed=embed_replenish_user)

        # Обновляем баланс в базе данных
        supabase.rpc("add_balance", {"card_number": "00000", "amount": commission}).execute()
        supabase.table("cards").update({"balance": banker_card_balance + salary}).eq("number", banker_card_number).execute()
        supabase.table("cards").update({"balance": card_balance + total_amount}).eq("number", number).execute()

        #Аудит действия
        member_audit = inter.guild.get_channel(bank_audit_channel)
        embed_aud_replenishMoney = emb_aud_replenishMoney(banker_id, card_full_number, banker_card_full_number, commission, salary, total_amount, description)
        await member_audit.send(embed=embed_aud_replenishMoney)


def setup(client):
    client.add_cog(ReplenishMoney(client))