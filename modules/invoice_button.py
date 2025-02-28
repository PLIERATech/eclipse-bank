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

                invoice_data = db_cursor("invoice").select("own_dsc_id, own_number, memb_dsc_id, banker_message_id, count, type_invoice, cards.type, cards.balance, cards.members, clients.account, clients.transactions").eq("memb_message_id", message.id).execute()


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
                member_card_owner_card_channel_id = check_card.data[0]["owner_account"]
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
                invoice_owner_card_channel_id = invoice_data.data[0]["account"]
                invoice_owner_transaction_channel_id = invoice_data.data[0]["transactions"]

                if not isinstance(invoice_card_members, dict):
                    invoice_card_members = {}

                # Проверяем, хватает ли денег
                if member_card_balance < invoice_count:
                    title_emb, message_emb, color_emb = get_message_with_title(
                        30, (), ())
                    embed_insufficient_funds = emb_auto(title_emb, message_emb, color_emb)
                    await inter.send(embed=embed_insufficient_funds, ephemeral=True)
                    return

                if invoice_type == "member":
                    invoice_card_number = invoice_data.data[0]["own_number"]
                    invoice_full_number = f"{suffixes.get(invoice_card_type, invoice_card_type)}{invoice_card_number}"

                    if invoice_full_number == member_full_number:
                        title_emb, message_emb, color_emb = get_message_with_title(
                            29, (), ())
                        embed_no_self_transfer = emb_auto(title_emb, message_emb, color_emb)
                        await inter.send(embed=embed_no_self_transfer, ephemeral=True)
                        return

                    # Отправка сообщений в каналы транзакций
                    embed_member_pay_button = emb_member_pay_button(member_id, member_full_number, invoice_full_number, invoice_count, self.comment.value, invoice_card_own_id)
                    member_card_owner_card_channel = inter.client.get_channel(member_card_owner_card_channel_id)
                    member_owner_transaction_channel = member_card_owner_card_channel.get_thread(member_card_owner_transaction_channel_id)
                    await member_owner_transaction_channel.send(embed=embed_member_pay_button)

                    embed_invoice_pay_button = emb_invoice_pay_button(member_id, member_full_number, invoice_full_number, invoice_count, self.comment.value, invoice_card_own_id)
                    invoice_owner_card_channel = inter.client.get_channel(invoice_owner_card_channel_id)
                    invoice_owner_transaction_channel = invoice_owner_card_channel.get_thread(invoice_owner_transaction_channel_id)
                    await invoice_owner_transaction_channel.send(embed=embed_invoice_pay_button)

                    # Отправка сообщений в каналы транзакций пользователей
                    for user_id, data in member_card_members.items():
                        channel_id_card_member = data.get("id_channel")
                        channel_id_transactions_member = data.get("id_transactions_channel")
                        channel_card_member = inter.client.get_channel(channel_id_card_member)
                        channel_transactions_member = channel_card_member.get_thread(channel_id_transactions_member)
                        await channel_transactions_member.send(embed=embed_member_pay_button)

                    for user_id, data in invoice_card_members.items():
                        channel_id_card_invoice = data.get("id_channel")
                        channel_id_transactions_invoice = data.get("id_transactions_channel")
                        channel_card_invoice = inter.client.get_channel(channel_id_card_invoice)
                        channel_transactions_invoicer = channel_card_invoice.get_thread(channel_id_transactions_invoice)
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
                        channel_id_card_member = data.get("id_channel")
                        channel_id_transactions_member = data.get("id_transactions_channel")
                        channel_card_member = inter.client.get_channel(channel_id_card_member)
                        channel_transactions_member = channel_card_member.get_thread(channel_id_transactions_member)
                        await channel_transactions_member.send(embed=embed_member_pay_button_banker)

                     # Обновляем баланс в базе данных
                    db_cursor("cards").update({"balance": member_card_balance - invoice_count}).eq("number", member_card_number).execute()

                    embed_banker_invoice_message = emb_banker_invoice_message(member_id, invoice_count, invoice_card_own_id)
                    await banker_invoice_message.edit(embed=embed_banker_invoice_message, view=None)

                    embed_aud_invoice_pay = emb_aud_invoice_pay_banker(member_id, invoice_card_own_id, member_full_number, invoice_count, self.comment.value)


                title_emb, message_emb, color_emb = get_message_with_title(
                    77, (), ())
                embed_comp_pay_button = emb_auto(title_emb, message_emb, color_emb)
                await inter.send(embed=embed_comp_pay_button, ephemeral=True)

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

        invoice_data = db_cursor("invoice").select("own_dsc_id, own_number, memb_dsc_id, banker_message_id, count, type_invoice, cards.type, cards.members, clients.account, clients.transactions").eq("memb_message_id", message.id).execute()

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
        invoice_owner_card_channel_id = invoice_data.data[0]["account"]
        invoice_owner_transaction_channel_id = invoice_data.data[0]["transactions"]
        invoice_full_number = f"{suffixes.get(invoice_card_type, invoice_card_type)}{invoice_card_number}"

        if not isinstance(invoice_card_members, dict):
            invoice_card_members = {}

        title_emb, message_emb, color_emb = get_message_with_title(
            24, (), ())
        embed_comp_decline_button = emb_auto(title_emb, message_emb, color_emb)
        await inter.send(embed=embed_comp_decline_button, ephemeral=True)

        if invoice_type == "member":
            # Отправка сообщений в каналы транзакций

            title_emb, message_emb, color_emb = get_message_with_title(
                25, (), (member_id, invoice_count))
            embed_msg_decline_button = emb_auto(title_emb, message_emb, color_emb)
            invoice_owner_card_channel = inter.client.get_channel(invoice_owner_card_channel_id)
            invoice_owner_transaction_channel = invoice_owner_card_channel.get_thread(invoice_owner_transaction_channel_id)
            await invoice_owner_transaction_channel.send(embed=embed_msg_decline_button)

            # Отправка сообщений в каналы транзакций пользователей
            for user_id, data in invoice_card_members.items():
                channel_id_card_invoice = data.get("id_channel")
                channel_id_transactions_invoice = data.get("id_transactions_channel")
                channel_card_invoice = inter.client.get_channel(channel_id_card_invoice)
                channel_transactions_invoicer = channel_card_invoice.get_thread(channel_id_transactions_invoice)
                await channel_transactions_invoicer.send(embed=embed_msg_decline_button)
                
            title_emb, message_emb, color_emb = get_message_with_title(
                64, (), (member_id, invoice_card_own_id, invoice_count))
            embed_aud_invoice_decline = emb_auto(title_emb, message_emb, color_emb)

        elif invoice_type == "banker":
            banker_message_id = invoice_data.data[0]["banker_message_id"]
            banker_invoice_channel = inter.client.get_channel(banker_invoice_channel_id)
            banker_invoice_message = await banker_invoice_channel.fetch_message(banker_message_id)

            # Отправка сообщений в каналы транзакций
            title_emb, message_emb, color_emb = get_message_with_title(
                25, (), (member_id, invoice_count))
            embed_msg_decline_button = emb_auto(title_emb, message_emb, color_emb)
            await banker_invoice_message.edit(embed=embed_msg_decline_button, view=None)

            title_emb, message_emb, color_emb = get_message_with_title(
                65, (), (member_id, invoice_card_own_id, invoice_count))
            embed_aud_invoice_decline = emb_auto(title_emb, message_emb, color_emb)

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

        invoice_data = db_cursor("invoice").select("own_dsc_id, memb_dsc_id, memb_message_id, memb_card_channel_id, memb_transaction_channel_id, count").eq("banker_message_id", message.id).execute()

        # Не найдены данные
        if not await verify_found_data(inter, invoice_data):
            return

        banker_invoice_start_id = invoice_data.data[0]["own_dsc_id"]
        member_id = invoice_data.data[0]["memb_dsc_id"]

        # Проверка прав на отмену счёта определенного банкира
        if not await verify_invoice_banker_cancel(inter, banker_id, banker_invoice_start_id, banker):
            return

        member_message_id = invoice_data.data[0]["memb_message_id"]
        member_card_channel_id = invoice_data.data[0]["memb_card_channel_id"]
        member_transaction_channel_id = invoice_data.data[0]["memb_transaction_channel_id"]
        member_card_channel = inter.client.get_channel(member_card_channel_id)
        member_transaction_channel = member_card_channel.get_thread(member_transaction_channel_id)
        member_message = await member_transaction_channel.fetch_message(member_message_id)
        invoice_count = invoice_data.data[0]["count"]

        title_emb, message_emb, color_emb = get_message_with_title(
            26, (), ())
        embed_comp_cancel_button = emb_auto(title_emb, message_emb, color_emb)
        await inter.send(embed=embed_comp_cancel_button, ephemeral=True)

        # Отправка сообщений в каналы транзакций
        title_emb, message_emb, color_emb = get_message_with_title(
            27, (), (banker_id, invoice_count))
        embed_edit_member_cancel_button = emb_auto(title_emb, message_emb, color_emb)
        await member_message.edit(embed=embed_edit_member_cancel_button, view=None)

        db_cursor("invoice").delete().eq("memb_message_id", message.id).execute()
        title_emb, message_emb, color_emb = get_message_with_title(
            28, (), (banker_id))
        embed_edit_bancer_cancel_button = emb_auto(title_emb, message_emb, color_emb)
        await message.edit(embed=embed_edit_bancer_cancel_button, view=None)

        #Аудит действия
        member_audit = inter.guild.get_channel(bank_audit_channel)

        title_emb, message_emb, color_emb = get_message_with_title(
            66, (), (banker_id, member_id, invoice_count))
        embed_aud_invoice_cancel_banker = emb_auto(title_emb, message_emb, color_emb)    
        await member_audit.send(embed=embed_aud_invoice_cancel_banker)