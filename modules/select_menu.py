from nextcord.ui import View, Select
import nextcord as nxc
from const import *
from .log_functions import *
from .embeds import *
from .verify import *
from card_gen import *
from .invoice_button import *
import asyncio
from db import *

class CardSelectView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @nxc.ui.select(
        custom_id="card_transaction",
        placeholder="Действия с картой",
        options=[
            nxc.SelectOption(label="Баланс", value="sm_checkBalance"),
            nxc.SelectOption(label="Перевод", value="sm_transfer"),
            nxc.SelectOption(label="Выставить счёт", value="sm_invoice"),
        ],
    )

    async def card_transaction_callback(self, select: Select, inter: nxc.Interaction):
        # Получаем основные данные из Interaction
        user = inter.user
        message = inter.message  # Сообщение, на котором нажали кнопку
        channel = inter.channel  # Канал, где это сообщение

        # Создаем словарь с действиями и их соответствующими обработчиками
        action_sm = {
            "sm_checkBalance": sm_check_balance,
            "sm_transfer": sm_transfer,
            "sm_invoice": sm_invoice,
        }

        handler = action_sm.get(select.values[0], sm_unknown)
        await handler(inter, user, message, channel)

        await inter.message.edit(view=CardSelectView())  # Сбрасываем выбор


    @nxc.ui.select(
        custom_id="card_settings",
        placeholder="Настройки",
        options=[
            nxc.SelectOption(label="Поменять название", value="sm_changeName"),
            nxc.SelectOption(label="Добавить пользователя", value="sm_addUser"),
            nxc.SelectOption(label="Удалить пользователя", value="sm_delUser"),
            nxc.SelectOption(label="Передать карту", value="sm_transferOwner"),
            nxc.SelectOption(label="Удалить карту", value="sm_deleteCard"),
        ],
    )
    async def card_settings_callback(self, select: Select, inter: nxc.Interaction):
        user = inter.user  # Кто воспользовался
        message = inter.message  # Сообщение, на котором нажали кнопку
        channel = inter.channel  # Канал, где это сообщение


        action_sm = {
            "sm_changeName": sm_change_name,
            "sm_addUser": sm_add_user,
            "sm_delUser": sm_del_user,
            "sm_transferOwner": sm_transfer_owner,
            "sm_deleteCard": sm_delete_card,
        }

        handler = action_sm.get(select.values[0], sm_unknown)
        await handler(inter, user, message, channel)

        await inter.message.edit(view=CardSelectView())  # Сбрасываем выбор




#- =================================================================================================================================
#-                                                                                                                                  
#-                                                     Действия с картой                                                            
#-                                                                                                                                  
#- =================================================================================================================================

#@ ---------------------------------------------------------------------------------------------------------------------------------
#@                                                      Проверить баланс                                                            
#@ ---------------------------------------------------------------------------------------------------------------------------------

async def sm_check_balance(inter, user, message, channel):
    await inter.response.defer(ephemeral=True)
    response_card = db_rpc("find_balance", {"msg_id": message.id}).execute()

    # Проверка на имеются ли данные
    if not await verify_found_data(inter, response_card):
        return

    balance = response_card.data[0]['balance']
    type = response_card.data[0]['type']
    number = response_card.data[0]['number']
    full_number = f"{suffixes.get(type, type)}{number}"


    embed = emb_check_balance(full_number, balance)
    await inter.send(embed=embed, ephemeral=True) 



#@ ---------------------------------------------------------------------------------------------------------------------------------
#@                                                      Перевод средств                                                             
#@ ---------------------------------------------------------------------------------------------------------------------------------

async def sm_transfer(inter, user, message, channel):
    """Вызывает модальное окно для перевода средств"""

    class TransferModal(nxc.ui.Modal):
        def __init__(self):
            super().__init__(title="Перевод средств")

            self.card_number = nxc.ui.TextInput(label="Номер карты получателя", placeholder="Введите номер...", required=True, min_length=5, max_length=5)
            self.add_item(self.card_number)

            self.amount = nxc.ui.TextInput(label="Сумма перевода", placeholder="Введите сумму...", required=True)
            self.add_item(self.amount)

            self.comment = nxc.ui.TextInput(label="Комментарий", placeholder="Опционально...", required=False, style=nxc.TextInputStyle.paragraph, max_length=100 )
            self.add_item(self.comment)



        async def callback(self, inter: nxc.Interaction):
            await inter.response.defer(ephemeral=True)
            """Обрабатывает данные после отправки формы"""
            receiver_card = self.card_number.value.strip()
            amount_text = self.amount.value

            # Проверка является ли номер карты цифрами
            if not await verify_card_int(inter, receiver_card):
                return

            # Проверка на целое число
            if not await verify_an_integer(inter, amount_text):
                return
            amount = int(amount_text)
            

            receiver_data = db_cursor("cards").select("type, balance, members, clients.channels").eq("number", receiver_card).execute()

            # Проверяем, существует ли карта получателя   
            if not await verify_found_card(inter, receiver_data):
                return

            receiver_type = receiver_data.data[0]["type"]
            receiver_balance = receiver_data.data[0]["balance"]
            receiver_members = receiver_data.data[0]["members"]
            receiver_owner_transaction_channel_id = list(map(int, receiver_data.data[0]["channels"].strip("[]").split(",")))[0]
            receiver_full_number = f"{suffixes.get(receiver_type, receiver_type)}{receiver_card}"

            if not isinstance(receiver_members, dict):  # Проверяем, если это не словарь (jsonb)
                receiver_members = {}

            # Определяем карту отправителя через message.id

            sender_data = db_rpc("find_card_in_message", {"msg_id": message.id}).execute()
            sender_type = sender_data.data[0]["type"]
            sender_card = sender_data.data[0]["number"]
            sender_balance = sender_data.data[0]["balance"]
            sender_members = sender_data.data[0]["members"]
            sender_owner_transaction_channel_id = sender_data.data[0]["owner_transactions"]
            sender_full_number = f"{suffixes.get(sender_type, sender_type)}{sender_card}"

            if not isinstance(sender_members, dict):  # Проверяем, если это не словарь (jsonb)
                sender_members = {}

            if sender_card == receiver_card:
                embed_no_self_transfer = emb_no_self_transfer()
                await inter.send(embed=embed_no_self_transfer, ephemeral=True)
                return

            # Проверяем, хватает ли денег
            if sender_balance < amount:
                embed_insufficient_funds = emb_insufficient_funds()
                await inter.send(embed=embed_insufficient_funds, ephemeral=True)
                return

            #Сообщение о выполнении
            embed_complete_transfer = emb_comp_transfer(sender_full_number, receiver_full_number, amount, self.comment.value)
            await inter.send(embed=embed_complete_transfer, ephemeral=True)

            # Отправка сообщений в каналы транзакций
            embed_sender = emb_transfer_sender(sender_full_number, receiver_full_number, amount, self.comment.value)
            embed_receimer = emb_transfer_receimer(sender_full_number, receiver_full_number, amount, self.comment.value)
            sender_owner_transaction_channel = inter.client.get_channel(sender_owner_transaction_channel_id)
            receiver_owner_transaction_channel = inter.client.get_channel(receiver_owner_transaction_channel_id)
            await sender_owner_transaction_channel.send(embed=embed_sender)
            await receiver_owner_transaction_channel.send(embed=embed_receimer)

            # Отправка сообщений в каналы транзакций пользователей
            for user_id, data in sender_members.items():
                channel_id_transactions_sender = data.get("id_transactions_channel")
                channel_transactions_sender = inter.client.get_channel(channel_id_transactions_sender)
                await channel_transactions_sender.send(embed=embed_sender)

            for user_id, data in receiver_members.items():
                channel_id_transactions_receiver = data.get("id_transactions_channel")
                channel_transactions_receiver = inter.client.get_channel(channel_id_transactions_receiver)
                await channel_transactions_receiver.send(embed=embed_receimer)

            # 🔹 Обновляем баланс в базе данных
            db_cursor("cards").update({"balance": sender_balance - amount}).eq("number", sender_card).execute()
            db_cursor("cards").update({"balance": receiver_balance + amount}).eq("number", receiver_card).execute()

            #Аудит действия
            member_audit = inter.guild.get_channel(bank_audit_channel)
            embed_aud_transfer = emb_aud_transfer(user.id, sender_full_number, receiver_full_number, amount, self.comment.value)
            await member_audit.send(embed=embed_aud_transfer)

    # 🔹 Показываем форму пользователю
    model = TransferModal()
    await inter.response.send_modal(model)



#@ ---------------------------------------------------------------------------------------------------------------------------------
#@                                                       Выставить счёт                                                             
#@ ---------------------------------------------------------------------------------------------------------------------------------

async def sm_invoice(inter, user, message, channel):
    """Вызывает модальное окно для выставления счёта"""
    class InvoiceModal(nxc.ui.Modal):
        def __init__(self):
            super().__init__(title="Выставить счёт")

            self.nickname_input = nxc.ui.TextInput(label="Никнейм пользователя", placeholder="Введите никнейм...", required=True, min_length=2, max_length=32)
            self.add_item(self.nickname_input)

            self.amount = nxc.ui.TextInput(label="Сумма запроса", placeholder="Введите сумму...", required=True)
            self.add_item(self.amount)

            self.comment = nxc.ui.TextInput(label="Комментарий", placeholder="Опционально...", required=False, style=nxc.TextInputStyle.paragraph, max_length=100 )
            self.add_item(self.comment)


        async def callback(self, inter: nxc.Interaction):
            await inter.response.defer(ephemeral=True)
            """Обрабатывает данные после отправки формы"""
            nickname = self.nickname_input.value.strip()
            amount_text = self.amount.value

            # Проверка на целое число
            if not await verify_an_integer(inter, amount_text):
                return
            amount = int(amount_text)
            
            nick_table = db_cursor("clients").select("dsc_id, channels").eq("nickname", nickname).execute()
            # Проверка является ли введеный никнейм клиентом
            if not await verify_select_menu_client(inter, nick_table, nickname):
                return
            
            nick_dsc_id = nick_table.data[0]["dsc_id"]
            nick_transaction_channel_id = list(map(int, nick_table.data[0]["channels"].strip("[]").split(",")))[0]

            sender_data = db_rpc("find_card_in_message", {"msg_id": message.id}).execute()
            sender_type = sender_data.data[0]["type"]
            sender_card = sender_data.data[0]["number"]
            sender_members = sender_data.data[0]["members"]
            sender_owner_transaction_channel_id = sender_data.data[0]["owner_transactions"]
            sender_full_number = f"{suffixes.get(sender_type, sender_type)}{sender_card}"

            #Сообщение о выполнении
            embed_complete_invoice = emb_comp_invoice(nick_dsc_id, amount, self.comment.value)
            await inter.send(embed=embed_complete_invoice, ephemeral=True)

            # Отправка сообщений в каналы транзакций
            embed_sender = emb_invoice_sender(user.display_name, nickname, amount, self.comment.value)
            embed_nick = emb_invoice_nick(user.id, sender_full_number, amount, self.comment.value)
            sender_owner_transaction_channel = inter.client.get_channel(sender_owner_transaction_channel_id)
            nick_transaction_channel = inter.client.get_channel(nick_transaction_channel_id)
            await sender_owner_transaction_channel.send(embed=embed_sender)
            view=MyInvoiceView() # Кнопочки
            nick_message = await nick_transaction_channel.send(embed=embed_nick, view = view)

            # Отправка сообщений в каналы транзакций пользователей
            for user_id, data in sender_members.items():
                channel_id_transactions_sender = data.get("id_transactions_channel")
                channel_transactions_sender = inter.client.get_channel(channel_id_transactions_sender)
                await channel_transactions_sender.send(embed=embed_sender)

            db_cursor("invoice").insert({
                "own_dsc_id":user.id,
                "own_number":sender_card,
                "memb_dsc_id":nick_dsc_id,
                "memb_message_id":nick_message.id,
                "memb_channel_id":nick_transaction_channel_id,
                "count":amount,
                "type_invoice":"member"
            }).execute()

            #Аудит действия
            member_audit = inter.guild.get_channel(bank_audit_channel)
            embed_aud_invoice = emb_aud_invoice(user.id, nick_dsc_id, amount, self.comment.value)
            await member_audit.send(embed=embed_aud_invoice)


    # 🔹 Показываем форму пользователю
    model = InvoiceModal()
    await inter.response.send_modal(model)








#- =================================================================================================================================
#-                                                                                                                                  
#-                                                      Настройки карты                                                             
#-                                                                                                                                  
#- =================================================================================================================================

#@ ---------------------------------------------------------------------------------------------------------------------------------
#@                                                     Поменять название                                                            
#@ ---------------------------------------------------------------------------------------------------------------------------------

async def sm_change_name(inter, user, message, channel):
    cards_table = db_cursor("cards").select("type, name, number, members").eq("select_menu_id", message.id).execute()

    # Проверка является ли владельцем карты
    if not await verify_select_menu_owner(inter, cards_table):
        return

    type = cards_table.data[0]['type']
    number = cards_table.data[0]['number']
    bdcardname = cards_table.data[0]['name']
    members = cards_table.data[0]['members']
    full_number = f"{suffixes.get(type, type)}{number}"
    card_type_rus = type_translate.get(type, type)
    
    # Проверка является ли карта банковской
    if not await verify_not_banker_card(inter, type):
        return
    
    if not isinstance(members, dict):  # Проверяем, если это не словарь (jsonb)
        members = {}

    class ChangeNameCardModal(nxc.ui.Modal):
        def __init__(self):
            super().__init__(title="Добавление пользователя к карте")

            self.cardname_input = nxc.ui.TextInput(label="Новое название карты", placeholder="Введите название...", required=True, min_length=1, max_length=20)
            self.add_item(self.cardname_input)


        async def callback(self, inter: nxc.Interaction):
            await inter.response.defer(ephemeral=True)

            # Получаем никнейм из поля
            cardname = self.cardname_input.value.strip()

            if cardname == bdcardname:
                embed=emb_same_name()
                await inter.send(embed=embed, ephemeral=True)
                return

            embed_complete=emb_comp_change_name(full_number, cardname)
            await inter.send(embed=embed_complete, ephemeral=True)

            existing_embeds = message.embeds
            color = existing_embeds[1].color
            new_card_embed = emb_cards(color, full_number, card_type_rus, cardname) 
            await message.edit(embeds=[new_card_embed, existing_embeds[1], existing_embeds[2]], attachments=[])

            # Обновляем все сообщения пользователей
            if members:
                for user_id, data in members.items():
                    msg_id = data.get("id_message")
                    channel_id = data.get("id_channel")
                    channel = inter.client.get_channel(channel_id) 
                    message_users = await channel.fetch_message(msg_id)
                    await message_users.edit(embeds=[new_card_embed, existing_embeds[1], existing_embeds[2]], attachments=[])

            db_cursor("cards").update({"name": cardname}).eq("select_menu_id", message.id).execute()

            #Аудит действия
            member_audit = inter.guild.get_channel(bank_audit_channel)
            embed_aud_change_name = emb_aud_change_name(user.id, full_number, bdcardname, cardname)
            await member_audit.send(embed=embed_aud_change_name)

    modal = ChangeNameCardModal()
    await inter.response.send_modal(modal)



#@ ---------------------------------------------------------------------------------------------------------------------------------
#@                                                   Добавить пользователя                                                          
#@ ---------------------------------------------------------------------------------------------------------------------------------

async def sm_add_user(inter, user, message, channel):
    cards_table = db_cursor("cards").select("type, number, members, owner, clients.nickname").eq("select_menu_id", message.id).execute()

    # Проверка является ли владельцем карты
    if not await verify_select_menu_owner(inter, cards_table):
        return

    type = cards_table.data[0]['type']
    number = cards_table.data[0]['number']
    members = cards_table.data[0]['members']
    full_number = f"{suffixes.get(type, type)}{number}"
    owner_name = cards_table.data[0]["nickname"]
    owner_id = cards_table.data[0]['owner'] 

    # Проверка является ли карта банковской
    if not await verify_not_banker_card(inter, type):
        return

    if not isinstance(members, dict):  # Проверяем, если это не словарь (jsonb)
        members = {}

    class AddUserModal(nxc.ui.Modal):
        def __init__(self):
            super().__init__(title="Добавление пользователя к карте")
            self.nickname_input = nxc.ui.TextInput(label="Никнейм пользователя", placeholder="Введите никнейм...", required=True, min_length=2, max_length=32)
            self.add_item(self.nickname_input)


        async def callback(self, inter: nxc.Interaction):
            await inter.response.defer(ephemeral=True)
            nickname = self.nickname_input.value.strip()
            
            nick_table = db_cursor("clients").select("dsc_id, channels").eq("nickname", nickname).execute()
            # Проверка является ли введеный никнейм клиентом
            if not await verify_select_menu_client(inter, nick_table, nickname):
                return

            member_id = nick_table.data[0]['dsc_id']
            if member_id == owner_id:
                embed_self_add_card = emb_self_add_card()
                await inter.send(embed=embed_self_add_card, ephemeral=True)
                return

            # Проверка, добавлен ли пользователь уже
            if str(member_id) in members:
                embed_no_replay_add = emb_no_replay_add(nickname)
                await inter.send(embed = embed_no_replay_add, ephemeral=True)
                return

            # Получаем канал пользователя и его ID
            member_channel_id = list(map(int, nick_table.data[0]["channels"].strip("[]").split(",")))[1]
            member_transactions_channel_id = list(map(int, nick_table.data[0]["channels"].strip("[]").split(",")))[0]
            member_channel = inter.guild.get_channel(member_channel_id)

            existing_embeds = message.embeds
            color = existing_embeds[1].color
            card_embed_user = emb_cards_users(inter.guild, color, owner_name, {})

            view = CardSelectView()  # Используем уже готовый View
            message_member_card = await member_channel.send(content=f"<@{member_id}>", embeds=[existing_embeds[0], existing_embeds[1], card_embed_user], view=view)

            # Добавляем нового пользователя в список
            members[str(member_id)] = {"id_transactions_channel": member_transactions_channel_id, "id_channel": member_channel_id, "id_message": message_member_card.id}

            card_embed_user = emb_cards_users(inter.guild, color, owner_name, members)


            embed_complete_add_user = emb_comp_add_user(member_id, full_number)
            await inter.send(embed=embed_complete_add_user, ephemeral=True)

            await message.edit(embeds=[existing_embeds[0], existing_embeds[1], card_embed_user], attachments=[])

            # Обновляем сообщения всех пользователей 
            for user_id, data in members.items():
                msg_id = data.get("id_message")
                channel_id = data.get("id_channel")
                channel = inter.client.get_channel(channel_id) 
                message_users = await channel.fetch_message(msg_id)
                await message_users.edit(embeds=[existing_embeds[0], existing_embeds[1], card_embed_user], attachments=[])

            db_cursor("cards").update({"members": members}).eq("select_menu_id", message.id).execute()

            #Аудит действия
            member_audit = inter.guild.get_channel(bank_audit_channel)
            embed_aud_add_user_card = emb_aud_add_user_card(user.id, member_id, full_number)
            await member_audit.send(embed=embed_aud_add_user_card)

    modal = AddUserModal()
    await inter.response.send_modal(modal)



#@ ---------------------------------------------------------------------------------------------------------------------------------
#@                                                    Удалить пользователя                                                          
#@ ---------------------------------------------------------------------------------------------------------------------------------

async def sm_del_user(inter, user, message, channel):
    cards_table = db_cursor("cards").select("type, number, members, owner, clients.nickname").eq("select_menu_id", message.id).execute()

    # Проверка является ли владельцем карты
    if not await verify_select_menu_owner(inter, cards_table):
        return

    type = cards_table.data[0]['type']
    number = cards_table.data[0]['number']
    members = cards_table.data[0]['members']  # Это уже jsonb
    full_number = f"{suffixes.get(type, type)}{number}"
    owner_name = cards_table.data[0]["nickname"]
    owner_id = cards_table.data[0]['owner'] 

    # Проверка является ли карта банковской
    if not await verify_not_banker_card(inter, type):
        return

    # Убираем проверку на строку и конвертацию в json
    if not isinstance(members, dict):  # Проверяем, если это не словарь (jsonb)
        members = {}

    class RemoveUserModal(nxc.ui.Modal):
        def __init__(self):
            super().__init__(title="Удаление пользователя с карты")
            self.nickname_input = nxc.ui.TextInput(label="Никнейм пользователя", placeholder="Введите никнейм...", required=True, min_length=2, max_length=32)
            self.add_item(self.nickname_input)


        async def callback(self, inter: nxc.Interaction):
            await inter.response.defer(ephemeral=True)
            nickname = self.nickname_input.value.strip()
        
            nick_table = db_cursor("clients").select("dsc_id, channels").eq("nickname", nickname).execute()
            # Проверка является ли введеный никнейм клиентом
            if not await verify_select_menu_client(inter, nick_table, nickname):
                return

            member_id = nick_table.data[0]['dsc_id']
            if member_id == owner_id:
                embed_self_del_card = emb_self_del_card()
                await inter.send(embed=embed_self_del_card, ephemeral=True)
                return

            # Проверка, есть ли пользователь в списке
            if str(member_id) not in members:
                embed_no_added_in_card = emb_no_added_in_card(member_id)
                await inter.send(embed=embed_no_added_in_card, ephemeral=True)
                return

            channel_member_id = members.get(str(member_id)).get("id_channel")
            message_member_id = members.get(str(member_id)).get("id_message")
            channel_member = inter.guild.get_channel(channel_member_id)
            message_member = await channel_member.fetch_message(message_member_id)
            await message_member.delete()

            # Удаляем пользователя из списка
            del members[str(member_id)]

            # Обновляем карту
            existing_embeds = message.embeds
            color = existing_embeds[1].color
            card_embed_user = emb_cards_users(inter.guild, color, owner_name, members)

            embed_complete_del_user_in_card = emb_comp_del_user_in_card(member_id, full_number)
            await inter.send(embed=embed_complete_del_user_in_card, ephemeral=True)

            await message.edit(embeds=[existing_embeds[0], existing_embeds[1], card_embed_user], attachments=[])

            # Обновляем сообщения всех пользователей
            for user_id, data in members.items():
                msg_id = data.get("id_message")
                channel_id = data.get("id_channel")
                channel = inter.client.get_channel(channel_id)
                message_users = await channel.fetch_message(msg_id)
                await message_users.edit(embeds=[existing_embeds[0], existing_embeds[1], card_embed_user], attachments=[])


            # Обновляем данные в базе данных
            db_cursor("cards").update({"members": members}).eq("select_menu_id", message.id).execute()  # Используем members как jsonb

            #Аудит действия
            member_audit = inter.guild.get_channel(bank_audit_channel)
            embed_aud_del_user_card = emb_aud_del_user_card(user.id, member_id, full_number)
            await member_audit.send(embed=embed_aud_del_user_card)


    modal = RemoveUserModal()
    await inter.response.send_modal(modal)



#@ ---------------------------------------------------------------------------------------------------------------------------------
#@                                                        Передать карту                                                            
#@ ---------------------------------------------------------------------------------------------------------------------------------

async def sm_transfer_owner(inter, user, message, channel):
    cards_table = db_cursor("cards").select("type, number, members, owner, clients.nickname, clients.channels").eq("select_menu_id", message.id).execute()

    # Проверка является ли владельцем карты
    if not await verify_select_menu_owner(inter, cards_table):
        return

    type = cards_table.data[0]['type']
    number = cards_table.data[0]['number']
    members = cards_table.data[0]['members']
    full_number = f"{suffixes.get(type, type)}{number}"
    old_owner_name = cards_table.data[0]["nickname"]
    old_owner_id = cards_table.data[0]['owner'] 
    old_owner_transaction_channel_id = list(map(int, cards_table.data[0]["channels"].strip("[]").split(",")))[0]
    old_owner_card_channel_id = list(map(int, cards_table.data[0]["channels"].strip("[]").split(",")))[1]

    # Проверка является ли карта банковской
    if not await verify_not_banker_card(inter, type):
        return

    # Убираем проверку на строку и конвертацию в json
    if not isinstance(members, dict):  # Проверяем, если это не словарь (jsonb)
        members = {}

    class TransferOwner(nxc.ui.Modal):
        def __init__(self):
            super().__init__(title="Передача карты")
            self.nickname_input = nxc.ui.TextInput(label="Никнейм клиента", placeholder="Введите никнейм...", required=True, min_length=2, max_length=32)
            self.add_item(self.nickname_input)


        async def callback(self, inter: nxc.Interaction):
            await inter.response.defer(ephemeral=True)
            nickname = self.nickname_input.value.strip()
            
            nick_table = db_cursor("clients").select("dsc_id, channels").eq("nickname", nickname).execute()
            # Проверка является ли введеный никнейм клиентом
            if not await verify_select_menu_client(inter, nick_table, nickname):
                return

            member_id = nick_table.data[0]['dsc_id']
            if member_id == old_owner_id:
                embed_self_transfer_owner = emb_self_transfer_owner()
                await inter.send(embed=embed_self_transfer_owner, ephemeral=True)
                return

            if str(member_id) not in members:
                embed_no_added_in_card_transfer = emb_no_added_in_card_transfer(member_id)
                await inter.send(embed=embed_no_added_in_card_transfer, ephemeral=True)
                return
            
            # Проверка на исчерпание лимита создания карт
            command = "Попытка передачи карты"
            if not await verify_count_cards(inter, member_id, command):
                return
            
            # Добавляем прошлого владельца в список пользователей
            members[str(old_owner_id)] = {"id_transactions_channel": old_owner_transaction_channel_id, "id_channel": old_owner_card_channel_id, "id_message": message.id}

            new_owner_message_id = members.get(str(member_id)).get("id_message")
            new_owner_channel_id = members.get(str(member_id)).get("id_channel")

            # Удаляем нового владельца из пользователей
            del members[str(member_id)]

            # Обновляем сообщение нового владельца
            # Генерируется новая карта (картинка)
            existing_embeds = message.embeds
            color = existing_embeds[0].color
            color_name = reverse_embed_colors.get(color, "Unknown")

            await card_generate(full_number, nickname, color_name)
            # Удалить старую картинку
            channel = inter.client.get_channel(image_saver_channel)
            async for msg in channel.history(limit=None):
                if full_number in msg.content:
                    await msg.delete()

            embed_comp_transfer_owner = emb_comp_transfer_owner(member_id, full_number)
            await inter.send(embed=embed_comp_transfer_owner, ephemeral=True)

            #вставка новой картинки в embed
            await asyncio.sleep(1,5)
            card_image = f"{full_number}.png"
            card = nxc.File(f"card_gen/cards/{card_image}", filename=card_image)
            image_upload_channel = inter.guild.get_channel(image_saver_channel)
            temp_message = await image_upload_channel.send(content=f"{full_number}",file=card)
            image_url = temp_message.attachments[0].url if temp_message.attachments else None

            card_embed_image = emb_cards_image(color, image_url)
            card_embed_user = emb_cards_users(inter.guild, color, nickname, members)
            new_owner_channel = inter.client.get_channel(new_owner_channel_id)
            new_owner_message = await new_owner_channel.fetch_message(new_owner_message_id)
            await new_owner_message.edit(embeds=[existing_embeds[0], card_embed_image, card_embed_user], attachments=[])

            # Обновляем сообщения всех пользователей
            for user_id, data in members.items():
                msg_id = data.get("id_message")
                channel_id = data.get("id_channel")
                channel = inter.client.get_channel(channel_id)
                message_users = await channel.fetch_message(msg_id)
                await message_users.edit(embeds=[existing_embeds[0], card_embed_image, card_embed_user], attachments=[])

            # Обновляем данные в базе данных
            db_cursor("cards").update({"owner": member_id,"members": members, "select_menu_id": new_owner_message_id}).eq("select_menu_id", message.id).execute()

            #Аудит действия
            member_audit = inter.guild.get_channel(bank_audit_channel)
            embed_aud_transfer_owner = emb_aud_transfer_owner(user.id, member_id, full_number)
            await member_audit.send(embed=embed_aud_transfer_owner)


    modal = TransferOwner()
    await inter.response.send_modal(modal)



#@ ---------------------------------------------------------------------------------------------------------------------------------
#@                                                         Удалить карту                                                            
#@ ---------------------------------------------------------------------------------------------------------------------------------

async def sm_delete_card(inter, user, message, channel):
    cards_table = db_rpc("find_card_in_message", {"msg_id": message.id}).execute()

    type = cards_table.data[0]['type']
    number = cards_table.data[0]['number']
    balance = cards_table.data[0]['balance']
    memb_type = cards_table.data[0].get('memb_type')
    full_number = f"{suffixes.get(type, type)}{number}"
    card_type_rus = type_translate.get(type, type)
    
    # Проверка является ли карта банковской
    if not await verify_not_banker_card(inter, type):
        return
    
    # Проверка имеется ли средства на карте
    if memb_type == 'owner':
        if not await verify_delete_card_balance(inter, balance):
            return

    class DeleteCardModal(nxc.ui.Modal):
        def __init__(self):
            super().__init__(title="Подтверждение на удаление карты")

            self.cardname_input = nxc.ui.TextInput(label=f"Введите `{full_number}` для подтверждения.", placeholder="Введите название...", required=True, min_length=9, max_length=9)
            self.add_item(self.cardname_input)


        async def callback(self, inter: nxc.Interaction):
            await inter.response.defer(ephemeral=True)

            # Получаем никнейм из поля
            cardname = self.cardname_input.value.strip()

            if cardname != full_number:
                embed=emb_no_delete_card_wrong_number()
                await inter.send(embed=embed, ephemeral=True)
                return

            embed_complete=emb_comp_delete_card(full_number)
            await inter.send(embed=embed_complete, ephemeral=True)

            #Удаление карты
            await message.delete()

            #Аудит действия
            if memb_type== 'owner':

                embed_aud_delete_card = emb_aud_delete_card_own(user.id, full_number)
            else:
                embed_aud_delete_card = emb_aud_delete_card_memb(user.id, full_number)
            member_audit = inter.guild.get_channel(bank_audit_channel)
            await member_audit.send(embed=embed_aud_delete_card)        

    modal = DeleteCardModal()
    await inter.response.send_modal(modal)





#- =================================================================================================================================
#-                                                       Неизвестный выбор                                                          
#- =================================================================================================================================

async def sm_unknown(inter, user, message, channel):
    embed = emb_sb_e_select_menu()
    await inter.response.send_message(embed= embed, ephemeral=True)
    return 