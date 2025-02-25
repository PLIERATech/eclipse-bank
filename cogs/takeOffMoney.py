import nextcord as nxc
from nextcord.ext import commands
from const import *
from modules import *
from db import *

command = "/Изъять-деньги"

class TakeOffMoney(commands.Cog):
    def __init__(self, client):
        self.client = client
        
    @nxc.slash_command(guild_ids=server_id, name="изъять-деньги", description="изъять деньги с карты", default_member_permissions=nxc.Permissions(administrator=True))
    async def takeOffMoney(
        self, 
        inter: nxc.Interaction, 
        number: int = nxc.SlashOption(name="номер-карты", description="Номер карты", max_value=99999), 
        count: int = nxc.SlashOption(name="сумма", description="Сумма обналичивания", min_value=1, max_value=1000000), 
        description: str = nxc.SlashOption(name="комментарий", description="комментарий банкира", max_length=50)
    ):
        admin = inter.user
        admin_nick = inter.user.display_name
        admin_id = inter.user.id

        # Проверка прав staff
        if not await verify_staff(inter, admin, command):
            return

        await inter.response.defer(ephemeral=True)
        
        # дописывает 0 в начало если длина числа < 5
        number = f"{number:05}"

        card_data = db_cursor("cards").select("type, balance, members, clients.channels").eq("number", number).execute()

        # Проверяем, существует ли карта получателя
        if not await verify_found_card(inter, card_data):
            return

        card_type = card_data.data[0]["type"]
        card_balance = card_data.data[0]["balance"]
        card_members = card_data.data[0]["members"]
        card_owner_transaction_channel_id = list(map(int, card_data.data[0]["channels"].strip("[]").split(",")))[0]
        card_full_number = f"{suffixes.get(card_type, card_type)}{number}"


        embed_comp_take_off_money = emb_comp_take_off_money(card_full_number, count, description)
        await inter.send(embed=embed_comp_take_off_money, ephemeral=True)

        if not isinstance(card_members, dict):  # Проверяем, если это не словарь (jsonb)
            card_members = {}

        # 🔹 Обновляем баланс в базе данных
        db_cursor("cards").update({"balance": card_balance - count}).eq("number", number).execute()

        # Отправка сообщений в каналы транзакций
        embed_take_off_money = emb_take_off_money(admin_id, card_full_number, count, description)
        card_owner_transaction_channel = inter.client.get_channel(card_owner_transaction_channel_id)
        await card_owner_transaction_channel.send(embed=embed_take_off_money)

        for user_id, data in card_members.items():
            channel_id_transactions_card = data.get("id_transactions_channel")
            channel_transactions_card = inter.client.get_channel(channel_id_transactions_card)
            await channel_transactions_card.send(embed=embed_take_off_money)

        #Аудит действия
        member_audit = inter.guild.get_channel(bank_audit_channel)
        embed_aud_takeOffMoney = emb_aud_takeOffMoney(admin_id, card_full_number, count, description)
        await member_audit.send(embed=embed_aud_takeOffMoney)

def setup(client):
    client.add_cog(TakeOffMoney(client))