from nextcord.ui import View, Select
import nextcord as nxc
from const import *
from .verify import *
from db import *

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

                invoice_data = db_cursor("invoice").select("own_dsc_id, own_number, memb_dsc_id, banker_message_id, count, type_invoice, cards.type, cards.balance, cards.members, clients.channels").eq("memb_message_id", message.id).execute()


                # Проверка является ли карта с выставленного счёта действительной
                if not await verify_invoice_card(inter, invoice_data, message):
                    return

                member_id = invoice_data.data[0]["memb_dsc_id"]

                check_card = db_rpc("check_user_card", {"user_id": member_id, "number_value": user_card}).execute()

                # Проверка нашло ли карту (не правильная, либо не владелец данной карты)
                if not await verify_select_pay_button(inter, check_card):
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
                invoice_count = invoice_data.data[0]["count"]
                invoice_type = invoice_data.data[0]["type_invoice"]
                invoice_card_type = invoice_data.data[0]["type"]
                invoice_card_balance = invoice_data.data[0]["balance"]
                invoice_card_members = invoice_data.data[0]["members"]
                invoice_owner_transaction_channel_id = list(map(int, invoice_data.data[0]["channels"].strip("[]").split(",")))[0]

                if not isinstance(invoice_card_members, dict):
                    invoice_card_members = {}

                # Проверяем, хватает ли денег
                if member_card_balance < invoice_count:
                    embed_insufficient_funds = emb_insufficient_funds()
                    await inter.send(embed=embed_insufficient_funds, ephemeral=True)
                    return

                embed_comp_pay_button = emb_comp_pay_button()
                await inter.send(embed=embed_comp_pay_button, ephemeral=True)

                if invoice_type == "member":
                    invoice_card_number = invoice_data.data[0]["own_number"]
                    invoice_full_number = f"{suffixes.get(invoice_card_type, invoice_card_type)}{invoice_card_number}"

                    # Отправка сообщений в каналы транзакций
                    embed_member_pay_button = emb_member_pay_button(member_id, member_full_number, invoice_full_number, invoice_count, self.comment.value, invoice_card_own_id)
                    embed_invoice_pay_button = emb_invoice_pay_button(member_id, member_full_number, invoice_full_number, invoice_count, self.comment.value, invoice_card_own_id)
                    member_owner_transaction_channel = inter.client.get_channel(member_card_owner_transaction_channel_id)
                    invoice_owner_transaction_channel = inter.client.get_channel(invoice_owner_transaction_channel_id)
                    await member_owner_transaction_channel.send(embed=embed_member_pay_button)
                    await invoice_owner_transaction_channel.send(embed=embed_invoice_pay_button)

                    # Отправка сообщений в каналы транзакций пользователей
                    for user_id, data in member_card_members.items():
                        channel_id_transactions_member = data.get("id_transactions_channel")
                        channel_transactions_member = inter.client.get_channel(channel_id_transactions_member)
                        await channel_transactions_member.send(embed=embed_member_pay_button)

                    for user_id, data in invoice_card_members.items():
                        channel_id_transactions_invoice = data.get("id_transactions_channel")
                        channel_transactions_invoicer = inter.client.get_channel(channel_id_transactions_invoice)
                        await channel_transactions_invoicer.send(embed=embed_invoice_pay_button)

                    # Обновляем баланс в базе данных
                    db_cursor("cards").update({"balance": member_card_balance - invoice_count}).eq("number", member_card_number).execute()
                    db_cursor("cards").update({"balance": invoice_card_balance + invoice_count}).eq("number", invoice_card_number).execute()

                    embed_aud_invoice_pay = emb_aud_invoice_pay_member(member_id, invoice_card_own_id, member_full_number, invoice_full_number, invoice_count, self.comment.value)

                elif invoice_type == "banker":
                    banker_message_id = invoice_data.data[0]["banker_message_id"]
                    banker_invoice_channel = inter.client.get_channel(banker_invoice_channel_id)
                    banker_invoice_message = await banker_invoice_channel.fetch_message(banker_message_id)

                    # Отправка сообщений в каналы транзакций
                    embed_member_pay_button_banker = emb_member_pay_button_banker(member_id, member_full_number, invoice_count, self.comment.value, invoice_card_own_id)
                    member_owner_transaction_channel = inter.client.get_channel(member_card_owner_transaction_channel_id)
                    await member_owner_transaction_channel.send(embed=embed_member_pay_button_banker)

                    # Отправка сообщений в каналы транзакций пользователей
                    for user_id, data in member_card_members.items():
                        channel_id_transactions_member = data.get("id_transactions_channel")
                        channel_transactions_member = inter.client.get_channel(channel_id_transactions_member)
                        await channel_transactions_member.send(embed=embed_member_pay_button_banker)

                     # Обновляем баланс в базе данных
                    db_cursor("cards").update({"balance": member_card_balance - invoice_count}).eq("number", member_card_number).execute()

                    embed_banker_invoice_message = emb_banker_invoice_message(member_id, invoice_count, invoice_card_own_id)
                    await banker_invoice_message.edit(embed=embed_banker_invoice_message, view=None)

                    embed_aud_invoice_pay = emb_aud_invoice_pay_banker(member_id, invoice_card_own_id, member_full_number, invoice_count, self.comment.value)

                db_cursor("invoice").delete().eq("memb_message_id", message.id).execute()
                await message.edit("✅ Счёт подтверждён!", view=None)

                #Аудит действия
                member_audit = inter.guild.get_channel(bank_audit_channel)
                await member_audit.send(embed=embed_aud_invoice_pay)
                

        await inter.response.send_modal(MyModal())



#@ ---------------------------------------------------------------------------------------------------------------------------------
#@                                                         Отказаться                                                               
#@ ---------------------------------------------------------------------------------------------------------------------------------

    @nxc.ui.button(label="Отказаться", style=nxc.ButtonStyle.red, custom_id="decline_button")
    async def disable_button(self, button: nxc.ui.Button, inter: nxc.Interaction):
        await inter.response.defer(ephemeral=True)
        
        message = inter.message
        channel = inter.channel

        invoice_data = db_cursor("invoice").select("own_dsc_id, own_number, memb_dsc_id, banker_message_id, count, type_invoice, cards.type, cards.members, clients.channels").eq("memb_message_id", message.id).execute()

        # Проверка является ли карта с выставленного счёта действительной
        if not await verify_invoice_card(inter, invoice_data, message):
            return

        member_id = invoice_data.data[0]["memb_dsc_id"]

        invoice_card_own_id = invoice_data.data[0]["own_dsc_id"]
        invoice_card_number = invoice_data.data[0]["own_number"]
        invoice_count = invoice_data.data[0]["count"]
        invoice_type = invoice_data.data[0]["type_invoice"]
        invoice_card_type = invoice_data.data[0]["type"]
        invoice_card_members = invoice_data.data[0]["members"]
        invoice_owner_transaction_channel_id = list(map(int, invoice_data.data[0]["channels"].strip("[]").split(",")))[0]
        invoice_full_number = f"{suffixes.get(invoice_card_type, invoice_card_type)}{invoice_card_number}"

        if not isinstance(invoice_card_members, dict):
            invoice_card_members = {}

        embed_comp_decline_button = emb_comp_decline_button()
        await inter.send(embed=embed_comp_decline_button, ephemeral=True)

        if invoice_type == "member":
            # Отправка сообщений в каналы транзакций

            embed_msg_decline_button = emb_msg_decline_button(member_id, invoice_count)
            invoice_owner_transaction_channel = inter.client.get_channel(invoice_owner_transaction_channel_id)
            await invoice_owner_transaction_channel.send(embed=embed_msg_decline_button)

            # Отправка сообщений в каналы транзакций пользователей
            for user_id, data in invoice_card_members.items():
                channel_id_transactions_invoice = data.get("id_transactions_channel")
                channel_transactions_invoicer = inter.client.get_channel(channel_id_transactions_invoice)
                await channel_transactions_invoicer.send(embed=embed_msg_decline_button)
                
            embed_aud_invoice_decline = emb_aud_invoice_decline_member(member_id, invoice_card_own_id, invoice_count)


        elif invoice_type == "banker":
            banker_message_id = invoice_data.data[0]["banker_message_id"]
            banker_invoice_channel = inter.client.get_channel(banker_invoice_channel_id)
            banker_invoice_message = await banker_invoice_channel.fetch_message(banker_message_id)

            # Отправка сообщений в каналы транзакций
            await banker_invoice_message.edit(embed=embed_msg_decline_button, view=None)

            embed_aud_invoice_decline = emb_aud_invoice_decline_banker(member_id, invoice_card_own_id, invoice_count)

        db_cursor("invoice").delete().eq("memb_message_id", message.id).execute()
        await message.edit(embed=embed_comp_decline_button, view=None)

        #Аудит действия
        member_audit = inter.guild.get_channel(bank_audit_channel)
        await member_audit.send(embed=embed_aud_invoice_decline)


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
        banker = inter.user
        banker_id = banker.id

        invoice_data = db_cursor("invoice").select("own_dsc_id, memb_dsc_id, memb_message_id, memb_channel_id, count").eq("banker_message_id", message.id).execute()

        # Не найдены данные
        if not await verify_found_data(inter, invoice_data):
            return

        banker_invoice_start_id = invoice_data.data[0]["own_dsc_id"]
        member_id = invoice_data.data[0]["memb_dsc_id"]

        # Проверка прав на отмену счёта определенного банкира
        if not await verify_invoice_banker_cancel(inter, banker_id, banker_invoice_start_id, banker):
            return

        member_message_id = invoice_data.data[0]["memb_message_id"]
        member_channel_id = invoice_data.data[0]["memb_channel_id"]
        member_channel = inter.client.get_channel(member_channel_id)
        member_message = await member_channel.fetch_message(member_message_id)
        invoice_count = invoice_data.data[0]["count"]

        embed_comp_cancel_button = emb_comp_cancel_button()
        await inter.send(embed=embed_comp_cancel_button, ephemeral=True)

        # Отправка сообщений в каналы транзакций
        embed_edit_member_cancel_button = emb_edit_member_cancel_button(banker_id, invoice_count)
        await member_message.edit(embed=embed_edit_member_cancel_button, view=None)

        db_cursor("invoice").delete().eq("memb_message_id", message.id).execute()
        embed_edit_bancer_cancel_button = emb_edit_bancer_cancel_button(banker_id)
        await message.edit(embed=embed_edit_bancer_cancel_button, view=None)

        #Аудит действия
        member_audit = inter.guild.get_channel(bank_audit_channel)
        embed_aud_invoice_cancel_banker = emb_aud_invoice_cancel_banker(banker_id, member_id, invoice_count)
        await member_audit.send(embed=embed_aud_invoice_cancel_banker)