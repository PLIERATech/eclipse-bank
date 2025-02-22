from nextcord.ui import View, Select
import nextcord as nxc
from const import *
from .verify import *

class MyInvoiceView(View):
    def __init__(self):
        super().__init__(timeout=None)  # Ставим timeout=None, чтобы кнопки оставались активными







#@ ---------------------------------------------------------------------------------------------------------------------------------
#@                                                     Подтвердить счёт                                                             
#@ ---------------------------------------------------------------------------------------------------------------------------------
    @nxc.ui.button(label="Оплатить", style=nxc.ButtonStyle.green, custom_id="pay_button")
    async def open_modal(self, button: nxc.ui.Button, inter: nxc.Interaction):
        class MyModal(nxc.ui.Modal):
            def __init__(self):
                super().__init__(title="Подтвердить выставленный счёт")

                self.card_number = nxc.ui.TextInput(label="Номер карты для списывания", placeholder="Введите номер своей карты...", required=True, min_length=5, max_length=5)
                self.add_item(self.card_number)

                self.comment = nxc.ui.TextInput(label="Комментарий", placeholder="Опционально...", required=False, style=nxc.TextInputStyle.paragraph, max_length=100 )
                self.add_item(self.comment)

            async def callback(self, inter: nxc.Interaction):
                await inter.response.defer(ephemeral=True)
                
                user_card = self.card_number.value.strip()
                message = inter.message
                channel = inter.channel

                # Проверка является ли номер карты цифрами
                if not await verify_card_int(inter, user_card):
                    return

                invoice_data = supabase.table("invoice").select("own_dsc_id, own_number, memb_dsc_id, banker_message_id, count, type, cards(type, balance, members, clients(channels))").eq("memb_message_id", message.id).execute()


                # Проверка является ли карта с выставленного счёта действительной
                if not await verify_invoice_card(inter, invoice_data, message):
                    return

                member_id = invoice_data.data[0]["memb_dsc_id"]
                member = await inter.client.fetch_user(member_id)

                check_card = supabase.rpc("check_user_card", {"user_id": member_id, "number_value": user_card}).execute()

                if not check_card.data:
                    await inter.send(f"Вы написали не существующий номер или не владелец / пользователь данной карты", ephemeral=True)
                    return

                member_card_type = check_card.data[0]["type"]
                member_card_number = check_card.data[0]["number"]
                member_card_balance = check_card.data[0]["balance"]
                member_card_members = check_card.data[0]["members"]
                member_card_owner_transaction_channel_id = check_card.data[0]["owner_transactions"]
                member_full_number = f"{suffixes.get(member_card_type, member_card_type)}{member_card_number}"

                if not isinstance(member_card_members, dict):  # Проверяем, если это не словарь (jsonb)
                    member_card_members = {}

                invoice_card_own_id = invoice_data.data[0]["own_dsc_id"]
                invoice_card_own = await inter.client.fetch_user(invoice_card_own_id)
                invoice_count = invoice_data.data[0]["count"]
                invoice_type = invoice_data.data[0]["type"]
                invoice_cards_data = invoice_data.data[0].get("cards")
                invoice_card_type = invoice_cards_data["type"]
                invoice_card_balance = invoice_cards_data["balance"]
                invoice_card_members = invoice_cards_data["members"]
                invoice_clients_data = invoice_cards_data.get("clients")
                invoice_owner_transaction_channel_id = list(map(int, invoice_clients_data["channels"].strip("[]").split(",")))[0]

                if not isinstance(invoice_card_members, dict):
                    invoice_card_members = {}

                # 🔹 Проверяем, хватает ли денег
                if member_card_balance < invoice_count:
                    await inter.send("❌ Ошибка: **недостаточно средств**!", ephemeral=True)
                    return

                await inter.send(f"✅ **Счёт подтверждён!**", ephemeral=True)

                if invoice_type == "member":
                    invoice_card_number = invoice_data.data[0]["own_number"]
                    invoice_full_number = f"{suffixes.get(invoice_card_type, invoice_card_type)}{invoice_card_number}"

                    # 🔹 Обновляем баланс в базе данных
                    supabase.table("cards").update({"balance": member_card_balance - invoice_count}).eq("number", member_card_number).execute()
                    supabase.table("cards").update({"balance": invoice_card_balance + invoice_count}).eq("number", invoice_card_number).execute()

                    # Отправка сообщений в каналы транзакций
                    member_message_text = f"**Счёт оплачен {member.mention}**\n💳 Откуда `{member_full_number}`\n📤 Кому `{invoice_full_number}`\n💰 Сумма `{invoice_count} алм.`\n📝 Комментарий: `{self.comment.value or '—'}`\n Запросивший: `{invoice_card_own.mention}`"
                    invoice_message_text = f"**Счёт оплачен  {member.mention}**\n💳 От `{member_full_number}`\n📤 Куда `{invoice_full_number}`\n💰 Сумма `{invoice_count} алм.`\n📝 Комментарий: `{self.comment.value or '—'}`\n Запросивший: `{invoice_card_own.mention}`"
                    member_owner_transaction_channel = inter.client.get_channel(member_card_owner_transaction_channel_id)
                    invoice_owner_transaction_channel = inter.client.get_channel(invoice_owner_transaction_channel_id)
                    await member_owner_transaction_channel.send(member_message_text)
                    await invoice_owner_transaction_channel.send(invoice_message_text)

                    # Отправка сообщений в каналы транзакций пользователей
                    for user_id, data in member_card_members.items():
                        channel_id_transactions_member = data.get("id_transactions_channel")
                        channel_transactions_member = inter.client.get_channel(channel_id_transactions_member)
                        await channel_transactions_member.send(member_message_text)

                    for user_id, data in invoice_card_members.items():
                        channel_id_transactions_invoice = data.get("id_transactions_channel")
                        channel_transactions_invoicer = inter.client.get_channel(channel_id_transactions_invoice)
                        await channel_transactions_invoicer.send(invoice_message_text)

                elif invoice_type == "banker":
                    banker_message_id = invoice_data.data[0]["banker_message_id"]
                    banker_invoice_channel = inter.client.get_channel(banker_invoice_channel_id)
                    banker_invoice_message = await banker_invoice_channel.fetch_message(banker_message_id)

                    # 🔹 Обновляем баланс в базе данных
                    supabase.table("cards").update({"balance": member_card_balance - invoice_count}).eq("number", member_card_number).execute()

                    # Отправка сообщений в каналы транзакций
                    member_message_text = f"**Счёт оплачен {member.mention}**\n💳 Откуда `{member_full_number}`\n📤 Действие: `снятие наличных`\n💰 Сумма `{invoice_count} алм.`\n📝 Комментарий: `{self.comment.value or '—'}`\n Банкир: `{invoice_card_own.mention}`"
                    member_owner_transaction_channel = inter.client.get_channel(member_card_owner_transaction_channel_id)
                    await member_owner_transaction_channel.send(member_message_text)

                    # Отправка сообщений в каналы транзакций пользователей
                    for user_id, data in member_card_members.items():
                        channel_id_transactions_member = data.get("id_transactions_channel")
                        channel_transactions_member = inter.client.get_channel(channel_id_transactions_member)
                        await channel_transactions_member.send(member_message_text)

                    await banker_invoice_message.edit(f"**Счёт оплачен {member.mention}**\n📤 Действие: `снятие наличных`\n💰 Сумма `{invoice_count} алм.`", view=None)

                supabase.table("invoice").delete().eq("memb_message_id", message.id).execute()
                await message.edit("✅ Счёт подтверждён!", view=None)
                

        await inter.response.send_modal(MyModal())



#@ ---------------------------------------------------------------------------------------------------------------------------------
#@                                                         Отказаться                                                               
#@ ---------------------------------------------------------------------------------------------------------------------------------

    @nxc.ui.button(label="Отказаться", style=nxc.ButtonStyle.red, custom_id="decline_button")
    async def disable_button(self, button: nxc.ui.Button, inter: nxc.Interaction):
        await inter.response.defer(ephemeral=True)
        
        message = inter.message
        channel = inter.channel

        invoice_data = supabase.table("invoice").select("own_dsc_id, own_number, memb_dsc_id, banker_message_id, count, type, cards(type, members, clients(channels))").eq("memb_message_id", message.id).execute()

        # Проверка является ли карта с выставленного счёта действительной
        if not await verify_invoice_card(inter, invoice_data, message):
            return

        member_id = invoice_data.data[0]["memb_dsc_id"]
        member = await inter.client.fetch_user(member_id)

        invoice_card_own_id = invoice_data.data[0]["own_dsc_id"]
        invoice_card_own = await inter.client.fetch_user(invoice_card_own_id)
        invoice_card_number = invoice_data.data[0]["own_number"]
        invoice_count = invoice_data.data[0]["count"]
        invoice_type = invoice_data.data[0]["type"]
        invoice_cards_data = invoice_data.data[0].get("cards")
        invoice_card_type = invoice_cards_data["type"]
        invoice_card_members = invoice_cards_data["members"]
        invoice_clients_data = invoice_cards_data.get("clients")
        invoice_owner_transaction_channel_id = list(map(int, invoice_clients_data["channels"].strip("[]").split(",")))[0]
        invoice_full_number = f"{suffixes.get(invoice_card_type, invoice_card_type)}{invoice_card_number}"

        if not isinstance(invoice_card_members, dict):
            invoice_card_members = {}

        await inter.send(f"✅ **Счёт отменён!**", ephemeral=True)

        if invoice_type == "member":
            # Отправка сообщений в каналы транзакций
            invoice_message_text = f"**Счёт выставленный {member.mention} на сумму `{invoice_count} алм.` отменён**"
            invoice_owner_transaction_channel = inter.client.get_channel(invoice_owner_transaction_channel_id)
            await invoice_owner_transaction_channel.send(invoice_message_text)

            # Отправка сообщений в каналы транзакций пользователей
            for user_id, data in invoice_card_members.items():
                channel_id_transactions_invoice = data.get("id_transactions_channel")
                channel_transactions_invoicer = inter.client.get_channel(channel_id_transactions_invoice)
                await channel_transactions_invoicer.send(invoice_message_text)
                
        elif invoice_type == "banker":
            banker_message_id = invoice_data.data[0]["banker_message_id"]
            banker_invoice_channel = inter.client.get_channel(banker_invoice_channel_id)
            banker_invoice_message = await banker_invoice_channel.fetch_message(banker_message_id)

            # Отправка сообщений в каналы транзакций
            await banker_invoice_message.edit(f"**Счёт выставленный {member.mention} на сумму `{invoice_count} алм.` отменён**", view=None)

        supabase.table("invoice").delete().eq("memb_message_id", message.id).execute()
        await message.edit("✅ Счёт отменён!", view=None)

















class BankerInvoiceView(View):
    def __init__(self):
        super().__init__(timeout=None)  # Ставим timeout=None, чтобы кнопки оставались активными

#@ ---------------------------------------------------------------------------------------------------------------------------------
#@                                                           Отменить                                                               
#@ ---------------------------------------------------------------------------------------------------------------------------------

    @nxc.ui.button(label="Отменить", style=nxc.ButtonStyle.red, custom_id="cancel_button")
    async def disable_button(self, button: nxc.ui.Button, inter: nxc.Interaction):
        await inter.response.defer(ephemeral=True)
        
        message = inter.message
        channel = inter.channel
        member = inter.user
        member_id = member.id

        invoice_data = supabase.table("invoice").select("own_dsc_id, memb_message_id, memb_channel_id, count, type").eq("banker_message_id", message.id).execute()

        # Не найдены данные
        if not await verify_found_data(inter, invoice_data):
            return

        banker_invoice_start_id = invoice_data.data[0]["own_dsc_id"]

        # Проверка прав на отмену счёта определенного банкира
        if not await verify_invoice_banker_cancel(inter, member_id, banker_invoice_start_id, member):
            return

        member_message_id = invoice_data.data[0]["memb_message_id"]
        member_channel_id = invoice_data.data[0]["memb_channel_id"]
        member_channel = inter.client.get_channel(member_channel_id)
        member_message = await member_channel.fetch_message(member_message_id)
        invoice_count = invoice_data.data[0]["count"]
        invoice_type = invoice_data.data[0]["type"]

        await inter.send(f"❌ **Счёт отменён!**", ephemeral=True)

        # Отправка сообщений в каналы транзакций
        await member_message.edit(f"**Счёт выставленный банкиром {member.mention} на сумму `{invoice_count} алм.` отменён**", view=None)

        supabase.table("invoice").delete().eq("memb_message_id", message.id).execute()
        await message.edit(f"❌ Счёт отменён банкиром {member.mention}", view=None)
