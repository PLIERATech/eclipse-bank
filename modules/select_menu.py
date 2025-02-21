from nextcord.ui import View, Select
import nextcord as nxc
from const import *
from .log_functions import *
from .embeds import *
from .verify import *
from card_gen import *
import asyncio

class CardSelectView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @nxc.ui.select(
        custom_id="card_transaction",
        placeholder="Действия с картой",
        options=[
            nxc.SelectOption(label="Баланс", value="sm_checkBalance"),
            nxc.SelectOption(label="Перевод", value="sm_transfer"),
            # nxc.SelectOption(label="Выставить счёт", value="sm_invoice"),
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
            # "sm_invoice": sm_invoice,
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
    response_card = supabase.rpc("find_balance", {"msg_id": message.id}).execute()

    if response_card.data:
        balance = response_card.data[0]['balance']
        type = response_card.data[0]['type']
        number = response_card.data[0]['number']
        full_number = f"{suffixes.get(type, type)}{number}"

        await inter.send(f"На карте {full_number} хранится {balance} алм.", ephemeral=True)
    else:
        await inter.send(f"Данные не найдены.", ephemeral=True)



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
            

            receiver_data = supabase.table("cards").select("type, balance, members, clients(channels)").eq("number", receiver_card).execute()

            # 🔹 Проверяем, существует ли карта получателя
            if not receiver_data.data:
                await inter.send("❌ Ошибка: карта **не найдена**!", ephemeral=True)
                return

            receiver_type = receiver_data.data[0]["type"]
            receiver_balance = receiver_data.data[0]["balance"]
            receiver_members = receiver_data.data[0]["members"]
            receiver_client_data = receiver_data.data[0].get("clients")
            receiver_owner_transaction_channel_id = list(map(int, receiver_client_data["channels"].strip("[]").split(",")))[0]
            receiver_full_number = f"{suffixes.get(receiver_type, receiver_type)}{receiver_card}"

            if not isinstance(receiver_members, dict):  # Проверяем, если это не словарь (jsonb)
                receiver_members = {}

            # 🔹 Определяем карту отправителя через message.id

            sender_data = supabase.rpc("find_card_in_message", {"msg_id": message.id}).execute()
            sender_type = sender_data.data[0]["type"]
            sender_card = sender_data.data[0]["number"]
            sender_balance = sender_data.data[0]["balance"]
            sender_members = sender_data.data[0]["members"]
            sender_owner_transaction_channel_id = sender_data.data[0]["owner_transactions"]
            sender_full_number = f"{suffixes.get(sender_type, sender_type)}{sender_card}"

            if not isinstance(sender_members, dict):  # Проверяем, если это не словарь (jsonb)
                sender_members = {}

            # 🔹 Проверяем, хватает ли денег
            if sender_balance < amount:
                await inter.sende("❌ Ошибка: **недостаточно средств**!", ephemeral=True)
                return

            await inter.send(
                f"✅ **Перевод выполнен!**\n💳 Откуда `{sender_full_number}`\n📤 Кому `{receiver_full_number}`\n💰 Сумма `{amount} алм.`\n📝 Комментарий: `{self.comment.value or '—'}`",
                ephemeral=True
            )

            # 🔹 Обновляем баланс в базе данных
            supabase.table("cards").update({"balance": sender_balance - amount}).eq("number", sender_card).execute()
            supabase.table("cards").update({"balance": receiver_balance + amount}).eq("number", receiver_card).execute()

            # Отправка сообщений в каналы транзакций
            sender_message_text = f"**Перевод**\n💳 Откуда `{sender_full_number}`\n📤 Кому `{receiver_full_number}`\n💰 Сумма `{amount} алм.`\n📝 Комментарий: `{self.comment.value or '—'}`"
            receimer_message_text = f"**Поступили средства**\n💳 От `{sender_full_number}`\n📤 Куда `{receiver_full_number}`\n💰 Сумма `{amount} алм.`\n📝 Комментарий: `{self.comment.value or '—'}`"
            sender_owner_transaction_channel = inter.client.get_channel(sender_owner_transaction_channel_id)
            receiver_owner_transaction_channel = inter.client.get_channel(receiver_owner_transaction_channel_id)
            await sender_owner_transaction_channel.send(sender_message_text)
            await receiver_owner_transaction_channel.send(receimer_message_text)

            # Отправка сообщений в каналы транзакций пользователей
            for user_id, data in sender_members.items():
                channel_id_transactions_sender = data.get("id_transactions_channel")
                channel_transactions_sender = inter.client.get_channel(channel_id_transactions_sender)
                await channel_transactions_sender.send(sender_message_text)

            for user_id, data in receiver_members.items():
                channel_id_transactions_receiver = data.get("id_transactions_channel")
                channel_transactions_receiver = inter.client.get_channel(channel_id_transactions_receiver)
                await channel_transactions_receiver.send(receimer_message_text)

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
            

            receiver_data = supabase.table("clients").select("type, balance, members, clients(channels)").eq("number", receiver_card).execute()

            # 🔹 Проверяем, существует ли карта получателя
            if not receiver_data.data:
                await inter.send("❌ Ошибка: карта **не найдена**!", ephemeral=True)
                return

            receiver_type = receiver_data.data[0]["type"]
            receiver_balance = receiver_data.data[0]["balance"]
            receiver_members = receiver_data.data[0]["members"]
            receiver_client_data = receiver_data.data[0].get("clients")
            receiver_owner_transaction_channel_id = list(map(int, receiver_client_data["channels"].strip("[]").split(",")))[0]
            receiver_full_number = f"{suffixes.get(receiver_type, receiver_type)}{receiver_card}"

            if not isinstance(receiver_members, dict):  # Проверяем, если это не словарь (jsonb)
                receiver_members = {}

            # 🔹 Определяем карту отправителя через message.id

            sender_data = supabase.rpc("find_card_in_message", {"msg_id": message.id}).execute()
            sender_type = sender_data.data[0]["type"]
            sender_card = sender_data.data[0]["number"]
            sender_balance = sender_data.data[0]["balance"]
            sender_members = sender_data.data[0]["members"]
            sender_owner_transaction_channel_id = sender_data.data[0]["owner_transactions"]
            sender_full_number = f"{suffixes.get(sender_type, sender_type)}{sender_card}"

            if not isinstance(sender_members, dict):  # Проверяем, если это не словарь (jsonb)
                sender_members = {}

            # 🔹 Проверяем, хватает ли денег
            if sender_balance < amount:
                await inter.sende("❌ Ошибка: **недостаточно средств**!", ephemeral=True)
                return

            await inter.send(
                f"✅ **Перевод выполнен!**\n💳 Откуда `{sender_full_number}`\n📤 Кому `{receiver_full_number}`\n💰 Сумма `{amount} алм.`\n📝 Комментарий: `{self.comment.value or '—'}`",
                ephemeral=True
            )

            # 🔹 Обновляем баланс в базе данных
            supabase.table("cards").update({"balance": sender_balance - amount}).eq("number", sender_card).execute()
            supabase.table("cards").update({"balance": receiver_balance + amount}).eq("number", receiver_card).execute()

            # Отправка сообщений в каналы транзакций
            sender_message_text = f"**Перевод**\n💳 Откуда `{sender_full_number}`\n📤 Кому `{receiver_full_number}`\n💰 Сумма `{amount} алм.`\n📝 Комментарий: `{self.comment.value or '—'}`"
            receimer_message_text = f"**Поступили средства**\n💳 От `{sender_full_number}`\n📤 Куда `{receiver_full_number}`\n💰 Сумма `{amount} алм.`\n📝 Комментарий: `{self.comment.value or '—'}`"
            sender_owner_transaction_channel = inter.client.get_channel(sender_owner_transaction_channel_id)
            receiver_owner_transaction_channel = inter.client.get_channel(receiver_owner_transaction_channel_id)
            await sender_owner_transaction_channel.send(sender_message_text)
            await receiver_owner_transaction_channel.send(receimer_message_text)

            # Отправка сообщений в каналы транзакций пользователей
            for user_id, data in sender_members.items():
                channel_id_transactions_sender = data.get("id_transactions_channel")
                channel_transactions_sender = inter.client.get_channel(channel_id_transactions_sender)
                await channel_transactions_sender.send(sender_message_text)

            for user_id, data in receiver_members.items():
                channel_id_transactions_receiver = data.get("id_transactions_channel")
                channel_transactions_receiver = inter.client.get_channel(channel_id_transactions_receiver)
                await channel_transactions_receiver.send(receimer_message_text)

    # 🔹 Показываем форму пользователю
    model = InvoiceModal()
    await inter.response.send_modal(model)



















#     await inter.response.send_message(f"Вы выбрали выставить счёт. Пользователь: {user.mention}, Сообщение ID: {message.id}, Канал: {channel.mention}", ephemeral=True)
#     return 






#- =================================================================================================================================
#-                                                                                                                                  
#-                                                      Настройки карты                                                             
#-                                                                                                                                  
#- =================================================================================================================================

#@ ---------------------------------------------------------------------------------------------------------------------------------
#@                                                     Поменять название                                                            
#@ ---------------------------------------------------------------------------------------------------------------------------------

async def sm_change_name(inter, user, message, channel):
    cards_table = supabase.table("cards").select("type, name, number, members").eq("select_menu_id", message.id).execute()

    # Проверка является ли владелец карты (при условии добавления пользователей)
    if not cards_table.data:
        await inter.response.send_message("Ошибка: вы не владелец этой карты.", ephemeral=True)
        return

    type = cards_table.data[0]['type']
    number = cards_table.data[0]['number']
    bdcardname = cards_table.data[0]['name']
    members = cards_table.data[0]['members']
    full_number = f"{suffixes.get(type, type)}{number}"
    card_type_rus = type_translate.get(type, type)
    
    # Проверка является ли карта банковской (нельзя менять название)
    if type == admCardTypes[2]:
        await inter.response.send_message("Ошибка: нельзя поменять название зарплатной карты", ephemeral=True)
        return
    
    # Преобразуем строку в словарь, если она уже есть
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
                await inter.send(f"Ошибка: Вы не можете поставить такое же название", ephemeral=True)
                return

            await inter.send(f"Название карты {full_number} успешно измененно на '{cardname}'!", ephemeral=True)

            supabase.table("cards").update({"name": cardname}).eq("select_menu_id", message.id).execute()

            existing_embeds = message.embeds
            color = existing_embeds[1].color
            new_card_embed = e_cards(color, full_number, card_type_rus, cardname) 
            await message.edit(embeds=[new_card_embed, existing_embeds[1], existing_embeds[2]], attachments=[])

            # Обновляем все сообщения пользователей
            if members:
                for user_id, data in members.items():
                    msg_id = data.get("id_message")
                    channel_id = data.get("id_channel")
                    channel = inter.client.get_channel(channel_id) 
                    message_users = await channel.fetch_message(msg_id)
                    await message_users.edit(embeds=[new_card_embed, existing_embeds[1], existing_embeds[2]], attachments=[])

    modal = ChangeNameCardModal()
    await inter.response.send_modal(modal)



#@ ---------------------------------------------------------------------------------------------------------------------------------
#@                                                   Добавить пользователя                                                          
#@ ---------------------------------------------------------------------------------------------------------------------------------

async def sm_add_user(inter, user, message, channel):
    cards_table = supabase.table("cards").select("type, number, members, owner, clients(nickname)").eq("select_menu_id", message.id).execute()

    if not cards_table.data:
        await inter.response.send_message("Ошибка: вы не владелец этой карты.", ephemeral=True)
        return

    type = cards_table.data[0]['type']
    number = cards_table.data[0]['number']
    members = cards_table.data[0]['members']
    full_number = f"{suffixes.get(type, type)}{number}"
    client_data = cards_table.data[0].get("clients")
    owner_name = client_data["nickname"]
    owner_id = cards_table.data[0]['owner'] 

    # Проверка является ли карта банковской (нельзя менять название)
    if type == admCardTypes[2]:
        await inter.response.send_message("Ошибка: нельзя добавить пользователя для зарплатной карты", ephemeral=True)
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
            
            nick_table = supabase.table("clients").select("dsc_id, channels").eq("nickname", nickname).execute()
            if not nick_table.data:
                await inter.send(f"Ошибка: клиент с никнеймом '{nickname}' не найден, проверьте правильно ли написан его никнейм и является ли он клиентом.", ephemeral=True)
                return

            member_id = nick_table.data[0]['dsc_id']
            if not any(role.id in (staff_role) for role in user.roles):
                if member_id == owner_id:
                    await inter.send(f"Ошибка: Ты не можешь передать карту самому себе.", ephemeral=True)
                    return

            # Проверка, добавлен ли пользователь уже
            if str(member_id) in members:
                await inter.send(f"Ошибка: клиент {nickname} уже добавлен к карте.", ephemeral=True)
                return

            # Получаем канал пользователя и его ID
            member_table = supabase.table("clients").select("channels").eq("dsc_id", member_id).execute()
            member_channel_id = list(map(int, member_table.data[0]["channels"].strip("[]").split(",")))[1]
            member_transactions_channel_id = list(map(int, member_table.data[0]["channels"].strip("[]").split(",")))[0]
            member_channel = inter.guild.get_channel(member_channel_id)

            existing_embeds = message.embeds
            color = existing_embeds[1].color
            card_embed_user = e_cards_users(inter.guild, color, owner_name, {})

            view = CardSelectView()  # Используем уже готовый View
            message_member_card = await member_channel.send(content=f"<@{member_id}>", embeds=[existing_embeds[0], existing_embeds[1], card_embed_user], view=view)

            # Добавляем нового пользователя в список
            members[str(member_id)] = {"id_transactions_channel": member_transactions_channel_id, "id_channel": member_channel_id, "id_message": message_member_card.id}

            card_embed_user = e_cards_users(inter.guild, color, owner_name, members)

            await inter.send(f"Пользователь {nickname} успешно добавлен к карте {full_number}!", ephemeral=True)

            await message.edit(embeds=[existing_embeds[0], existing_embeds[1], card_embed_user], attachments=[])

            # Обновляем сообщения всех пользователей 
            for user_id, data in members.items():
                msg_id = data.get("id_message")
                channel_id = data.get("id_channel")
                channel = inter.client.get_channel(channel_id) 
                message_users = await channel.fetch_message(msg_id)
                await message_users.edit(embeds=[existing_embeds[0], existing_embeds[1], card_embed_user], attachments=[])

            supabase.table("cards").update({"members": members}).eq("select_menu_id", message.id).execute()

    modal = AddUserModal()
    await inter.response.send_modal(modal)



#@ ---------------------------------------------------------------------------------------------------------------------------------
#@                                                    Удалить пользователя                                                          
#@ ---------------------------------------------------------------------------------------------------------------------------------

async def sm_del_user(inter, user, message, channel):
    cards_table = supabase.table("cards").select("type, number, members, owner, clients(nickname)").eq("select_menu_id", message.id).execute()

    if not cards_table.data:
        await inter.response.send_message("Ошибка: вы не владелец этой карты.", ephemeral=True)
        return

    type = cards_table.data[0]['type']
    number = cards_table.data[0]['number']
    members = cards_table.data[0]['members']  # Это уже jsonb
    full_number = f"{suffixes.get(type, type)}{number}"
    client_data = cards_table.data[0].get("clients")
    owner_name = client_data["nickname"]
    owner_id = cards_table.data[0]['owner'] 

    # Проверка является ли карта банковской (нельзя менять название)
    if type == admCardTypes[2]:
        await inter.response.send_message("Ошибка: нельзя удалить пользователя из зарплатной карты", ephemeral=True)
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
        
            nick_table = supabase.table("clients").select("dsc_id, channels").eq("nickname", nickname).execute()
            if not nick_table.data:
                await inter.send(f"Ошибка: клиент с никнеймом '{nickname}' не найден, проверьте правильно ли написан его никнейм и является ли он клиентом.", ephemeral=True)
                return

            member_id = nick_table.data[0]['dsc_id']
            if not any(role.id in (staff_role) for role in user.roles):
                if member_id == owner_id:
                    await inter.send(f"Ошибка: Ты не можешь передать карту самому себе.", ephemeral=True)
                    return

            # Проверка, есть ли пользователь в списке
            if str(member_id) not in members:
                await inter.send(f"Ошибка: клиент с ID {member_id} не добавлен к карте.", ephemeral=True)
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
            card_embed_user = e_cards_users(inter.guild, color, owner_name, members)

            await inter.send(f"Пользователь {nickname} успешно удален с карты {full_number}!", ephemeral=True)

            await message.edit(embeds=[existing_embeds[0], existing_embeds[1], card_embed_user], attachments=[])

            # Обновляем сообщения всех пользователей
            for user_id, data in members.items():
                msg_id = data.get("id_message")
                channel_id = data.get("id_channel")
                channel = inter.client.get_channel(channel_id)
                message_users = await channel.fetch_message(msg_id)
                await message_users.edit(embeds=[existing_embeds[0], existing_embeds[1], card_embed_user], attachments=[])


            # Обновляем данные в базе данных
            supabase.table("cards").update({"members": members}).eq("select_menu_id", message.id).execute()  # Используем members как jsonb

    modal = RemoveUserModal()
    await inter.response.send_modal(modal)



#@ ---------------------------------------------------------------------------------------------------------------------------------
#@                                                        Передать карту                                                            
#@ ---------------------------------------------------------------------------------------------------------------------------------

async def sm_transfer_owner(inter, user, message, channel):
    cards_table = supabase.table("cards").select("type, number, members, owner, clients(nickname, channels)").eq("select_menu_id", message.id).execute()

    if not cards_table.data:
        await inter.response.send_message("Ошибка: вы не владелец этой карты.", ephemeral=True)
        return

    type = cards_table.data[0]['type']
    number = cards_table.data[0]['number']
    members = cards_table.data[0]['members']
    full_number = f"{suffixes.get(type, type)}{number}"
    client_data = cards_table.data[0].get("clients")
    old_owner_name = client_data["nickname"]
    old_owner_id = cards_table.data[0]['owner'] 
    old_owner_transaction_channel_id = list(map(int, client_data["channels"].strip("[]").split(",")))[0]
    old_owner_card_channel_id = list(map(int, client_data["channels"].strip("[]").split(",")))[1]

    # Проверка является ли карта банковской (нельзя менять название)
    if type == admCardTypes[2]:
        await inter.response.send_message("Ошибка: нельзя поменять владельца зарплатной карты", ephemeral=True)
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
            
            nick_table = supabase.table("clients").select("dsc_id, channels").eq("nickname", nickname).execute()
            if not nick_table.data:
                await inter.send(f"Ошибка: клиент с никнеймом '{nickname}' не найден, проверьте правильно ли написан его никнейм и является ли он клиентом.", ephemeral=True)
                return

            member_id = nick_table.data[0]['dsc_id']
            if member_id == old_owner_id:
                await inter.send(f"Ошибка: Ты не можешь передать карту самому себе.", ephemeral=True)
                return

            if str(member_id) not in members:
                await inter.send(f"Ошибка: клиент `{nickname}` должен быть пользователем карты. Перед передачей карты, добавьте его в пользователи.", ephemeral=True)
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

            #вставка новой картинки в embed
            await inter.send(f"{nickname} успешно стал владельцем карты `{full_number}`!", ephemeral=True)
            await asyncio.sleep(1,5)
            card_image = f"{full_number}.png"
            card = nxc.File(f"card_gen/cards/{card_image}", filename=card_image)
            image_upload_channel = inter.guild.get_channel(image_saver_channel)
            temp_message = await image_upload_channel.send(content=f"{full_number}",file=card)
            image_url = temp_message.attachments[0].url if temp_message.attachments else None

            card_embed_image = e_cards_image(color, image_url)
            card_embed_user = e_cards_users(inter.guild, color, nickname, members)
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
            supabase.table("cards").update({"owner": member_id,"members": members, "select_menu_id": new_owner_message_id}).eq("select_menu_id", message.id).execute()  # Используем members как jsonb

    modal = TransferOwner()
    await inter.response.send_modal(modal)






#- =================================================================================================================================
#-                                                       Неизвестный выбор                                                          
#- =================================================================================================================================

async def sm_unknown(inter, user, message, channel):
    await inter.response.send_message(f"Неизвестный выбор. Пользователь: {user.mention}, Сообщение ID: {message.id}, Канал: {channel.mention}", ephemeral=True)
    return 