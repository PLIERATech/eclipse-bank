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

        # 🔹 Проверяем, существует ли карта получателя
        if not card_data.data:
            await inter.send("❌ Ошибка: карта **не найдена**!", ephemeral=True)
            return

        card_type = card_data.data[0]["type"]
        card_balance = card_data.data[0]["balance"]
        card_members = card_data.data[0]["members"]
        card_client_data = card_data.data[0].get("clients")
        card_owner_transaction_channel_id = list(map(int, card_client_data["channels"].strip("[]").split(",")))[0]
        card_full_number = f"{suffixes.get(card_type, card_type)}{number}"

        if not isinstance(card_members, dict):  # Проверяем, если это не словарь (jsonb)
            card_members = {}

        cr1 = commission_replenish.get("1")
        cr2 = commission_replenish.get("2")
        cr3 = commission_replenish.get("3")

        if 1 < count <= cr1:
            commission = 1
            total_amount = count - commission
        elif cr1 < count <= cr2:
            commission = 2
            total_amount = count - commission
        elif cr2 < count <= cr3:
            commission = 3
            total_amount = count - commission
        else:
            commission = 4
            total_amount = count - commission

        await inter.send(
            f"✅ **Пополнение выполнено!**\n💳 карта `{card_full_number}`\n📤 Сумма `{count} алм.`\n📤 Комиссия `{commission} алм.`\n💰 Итого `{total_amount} алм.`\n📝 Комментарий: `{description or '—'}`\n Банкир: `{banker_nick}`",
            ephemeral=True
        )

        # 🔹 Обновляем баланс в базе данных
        supabase.rpc("add_balance", {"card_number": "00000", "amount": commission}).execute()
        supabase.table("cards").update({"balance": card_balance + total_amount}).eq("number", number).execute()

        # Отправка сообщений в каналы транзакций
        ceo_message_text = f"**Пополнение карты**\n💳 карта `{card_full_number}`\n📤 Сумма `{count} алм.`\n📤 Комиссия `{commission} алм.`\n💰 Итого `{total_amount} алм.`\n📝 Комментарий: `{description or '—'}`\n Банкир: `{banker_nick}`"
        card_message_text = f"**Пополнение карты**\n💳 карта `{card_full_number}`\n📤 Сумма `{count} алм.`\n📤 Комиссия `{commission} алм.`\n💰 Итого `{total_amount} алм.`\n📝 Комментарий: `{description or '—'}`\n Банкир: `{banker_nick}`"
        ceo_owner_transaction_channel = inter.client.get_channel(bank_card_transaction)
        card_owner_transaction_channel = inter.client.get_channel(card_owner_transaction_channel_id)
        await ceo_owner_transaction_channel.send(ceo_message_text)
        await card_owner_transaction_channel.send(card_message_text)

        for user_id, data in card_members.items():
            channel_id_transactions_card = data.get("id_transactions_channel")
            channel_transactions_card = inter.client.get_channel(channel_id_transactions_card)
            await channel_transactions_card.send(card_message_text)


def setup(client):
    client.add_cog(ReplenishMoney(client))