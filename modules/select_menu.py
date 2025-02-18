import nextcord as nxc
from const import *
from .log_functions import *
from .embeds import *
from nextcord.ui import View, Select
import json

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





#- Действия с картой
#@ Проверить баланс
async def sm_check_balance(inter, user, message, channel):
    response = supabase.table("cards").select("balance, type, number").eq("select_menu_id", message.id).execute()

    if response.data:
        balance = response.data[0]['balance']
        type = response.data[0]['type']
        number = response.data[0]['number']

        await inter.response.send_message(f"На карте {suffixes.get(type)}{number} хранится {balance} алм.", ephemeral=True)
    else:
        await inter.response.send_message(f"Данные не найдены.", ephemeral=True)
    return 


#@ Перевод средств
async def sm_transfer(inter, user, message, channel):
    """Вызывает модальное окно для перевода средств"""

    # 1. Ищем dsc_id владельца по ID канала
    query = supabase.table("clients").select("dsc_id").like("channels", f"%,{channel.id}]%").execute()

    # 3. Получаем dsc_id владельца
    owner_dsc_id = query.data[0]["dsc_id"]

    # 4. Сравниваем с пользователем
    if owner_dsc_id != user.id:
        return await inter.response.send_message("❌ Ошибка: Вы не владелец аккаунта!", ephemeral=True)








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
            """Обрабатывает данные после отправки формы"""
            receiver_card = self.card_number.value.strip()

            # 🔹 Проверка: сумма должна быть целым числом
            try:
                amount = int(self.amount.value)
                if amount <= 0:
                    raise ValueError
            except ValueError:
                return await inter.response.send_message("❌ Ошибка: сумма должна быть **целым положительным числом**!", ephemeral=True)
            
            # 🔹 Определяем карту отправителя через message.id
            sender_data = supabase.table("cards").select("number, balance").eq("select_menu_id", message.id).execute()
            sender_card = sender_data.data[0]["number"]
            sender_balance = sender_data.data[0]["balance"]

            receiver_data = supabase.table("cards").select("number, balance, owner").eq("number", receiver_card).execute()

            # 🔹 Проверяем, существует ли карта получателя
            if not receiver_data.data:
                return await inter.response.send_message("❌ Ошибка: карта **не найдена**!", ephemeral=True)

            receiver_balance = receiver_data.data[0]["balance"]
            receiver_owner = receiver_data.data[0]["owner"]

            # 🔹 Проверяем, хватает ли денег
            if sender_balance < amount:
                return await inter.response.send_message("❌ Ошибка: **недостаточно средств**!", ephemeral=True)

            # 🔹 Обновляем баланс в базе данных
            supabase.table("cards").update({"balance": sender_balance - amount}).eq("number", sender_card).execute()
            supabase.table("cards").update({"balance": receiver_balance + amount}).eq("number", receiver_card).execute()

            # 🔹 Отправляем сообщение об успешном переводе
            await inter.response.send_message(
                f"✅ **Перевод выполнен!**\n💳 От `{sender_card}`\n📤 Кому `{receiver_card}`\n💰 Сумма `{amount}₽`\n📝 Комментарий: `{self.comment.value or '—'}`",
                ephemeral=True
            )

            # 🔹 Уведомляем получателя, если он есть в Discord
            recipient = inter.client.get_user(receiver_owner)
            if recipient:
                await recipient.send(
                    f"📩 Вы получили **{amount}₽** от `{sender_card}`.\n📝 Комментарий: `{self.comment.value or '—'}`"
                )

    # 🔹 Показываем форму пользователю
    await inter.response.send_modal(TransferModal())

    # await inter.response.send_message(f"Вы выбрали перевод средств. Пользователь: {user.mention}, Сообщение ID: {message.id}, Канал: {channel.mention}", ephemeral=True)
    return 


#@ Пыставить счёт
async def sm_invoice(inter, user, message, channel):
    await inter.response.send_message(f"Вы выбрали выставить счёт. Пользователь: {user.mention}, Сообщение ID: {message.id}, Канал: {channel.mention}", ephemeral=True)
    return 


#- Настройки
#@ Поменять название
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

    class ChangeNameCardModal(nxc.ui.Modal):
        def __init__(self):
            super().__init__(title="Добавление пользователя к карте")

            self.cardname_input = nxc.ui.TextInput(label="Новое название карты", placeholder="Введите название...", required=True, min_length=1, max_length=20)
            self.add_item(self.cardname_input)


        async def callback(self, inter: nxc.Interaction):

            # Получаем никнейм из поля
            cardname = self.cardname_input.value.strip()

            if cardname == bdcardname:
                await inter.response.send_message(f"Ошибка: Вы не можете поставить такое же название", ephemeral=True)
                return
            
            supabase.table("cards").update({"name": cardname}).eq("select_menu_id", message.id).execute()

            await inter.response.send_message(f"Название карты {full_number} успешно измененно на '{cardname}'!", ephemeral=True)

            existing_embeds = message.embeds
            color = existing_embeds[1].color
            new_card_embed = e_cards(color, full_number, card_type_rus, cardname) 
            await message.edit(embeds=[new_card_embed, existing_embeds[1], existing_embeds[2]], attachments=[])

            # Преобразуем строку в словарь, если она уже есть
            if isinstance(members, str):
                members = json.loads(members)

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
    return 


#@ Добавить пользователя
async def sm_add_user(inter, user, message, channel):
    cards_table = supabase.table("cards").select("type, number, members, clients(nickname)").eq("select_menu_id", message.id).execute()

    if not cards_table.data:
        await inter.response.send_message("Ошибка: вы не владелец этой карты.", ephemeral=True)
        return

    type = cards_table.data[0]['type']
    number = cards_table.data[0]['number']
    members = cards_table.data[0]['members']
    full_number = f"{suffixes.get(type, type)}{number}"
    client_data = cards_table.data[0].get("clients")
    owner_name = client_data["nickname"]

    if isinstance(members, str):
        try:
            members = json.loads(members)
        except json.JSONDecodeError:
            members = {}

    class AddUserModal(nxc.ui.Modal):
        def __init__(self):
            super().__init__(title="Добавление пользователя к карте")
            self.nickname_input = nxc.ui.TextInput(label="Никнейм пользователя", placeholder="Введите никнейм...", required=True, min_length=2, max_length=32)
            self.add_item(self.nickname_input)

        async def callback(self, inter: nxc.Interaction):
            nickname = self.nickname_input.value.strip()
            
            member = nxc.utils.get(inter.guild.members, display_name=nickname)
            if not member:
                await inter.response.send_message(f"Ошибка: пользователь с никнеймом '{nickname}' не найден на сервере.", ephemeral=True)
                return

            # Проверка, является ли пользователь клиентом
            if not any(role.id == client_role_id for role in member.roles):
                await inter.response.send_message(f"Пользователь {nickname} не является клиентом", ephemeral=True)
                return

            member_id = member.id
            if member_id == user.id:
                await inter.response.send_message(f"Ошибка: Ты не можешь добавить самого себя.", ephemeral=True)
                return

            # Проверка, добавлен ли пользователь уже
            if str(member_id) in members:
                await inter.response.send_message(f"Ошибка: пользователь с ID {member_id} уже добавлен.", ephemeral=True)
                return

            # Получаем канал пользователя и его ID
            member_table = supabase.table("clients").select("channels").eq("dsc_id", member_id).execute()
            member_channel_id = list(map(int, member_table.data[0]["channels"].strip("[]").split(",")))[1]
            member_channel = inter.guild.get_channel(member_channel_id)

            existing_embeds = message.embeds
            color = existing_embeds[1].color
            card_embed_user = e_cards_users(inter, color, owner_name, {})

            view = CardSelectView()  # Используем уже готовый View
            message_member_card = await member_channel.send(content=f"{member.mention}", embeds=[existing_embeds[0], existing_embeds[1], card_embed_user], view=view)

            # Добавляем нового пользователя в список
            members[str(member_id)] = {"id_channel": member_channel_id, "id_message": message_member_card.id}

            card_embed_user = e_cards_users(inter, color, owner_name, members)
            await message.edit(embeds=[existing_embeds[0], existing_embeds[1], card_embed_user], attachments=[])

            # Обновляем сообщения всех пользователей
            for user_id, data in members.items():
                msg_id = data.get("id_message")
                channel_id = data.get("id_channel")
                channel = inter.client.get_channel(channel_id) 
                message_users = await channel.fetch_message(msg_id)
                await message_users.edit(embeds=[existing_embeds[0], existing_embeds[1], card_embed_user], attachments=[])

            supabase.table("cards").update({"members": json.dumps(members)}).eq("select_menu_id", message.id).execute()

            await inter.response.send_message(f"Пользователь {nickname} успешно добавлен к карте {full_number}!", ephemeral=True)

    modal = AddUserModal()
    await inter.response.send_modal(modal)












    # await inter.response.send_message(f"Вы выбрали добавить пользователя. Пользователь: {user.mention}, Сообщение ID: {message.id}, Канал: {channel.mention}", ephemeral=True)
    return 


#@ Удалить пользователя
async def sm_del_user(inter, user, message, channel):
    cards_table = supabase.table("cards").select("type, number, members, clients(nickname)").eq("select_menu_id", message.id).execute()

    if not cards_table.data:
        await inter.response.send_message("Ошибка: вы не владелец этой карты.", ephemeral=True)
        return

    type = cards_table.data[0]['type']
    number = cards_table.data[0]['number']
    members = cards_table.data[0]['members']
    full_number = f"{suffixes.get(type, type)}{number}"
    client_data = cards_table.data[0].get("clients")
    owner_name = client_data["nickname"]

    if isinstance(members, str):
        try:
            members = json.loads(members)
        except json.JSONDecodeError:
            members = {}

    class RemoveUserModal(nxc.ui.Modal):
        def __init__(self):
            super().__init__(title="Удаление пользователя с карты")
            self.nickname_input = nxc.ui.TextInput(label="Никнейм пользователя", placeholder="Введите никнейм...", required=True, min_length=2, max_length=32)
            self.add_item(self.nickname_input)

        async def callback(self, inter: nxc.Interaction):
            nickname = self.nickname_input.value.strip()
            
            member = nxc.utils.get(inter.guild.members, display_name=nickname)
            if not member:
                await inter.response.send_message(f"Ошибка: пользователь с никнеймом '{nickname}' не найден на сервере.", ephemeral=True)
                return

            member_id = member.id
            if member_id == user.id:
                await inter.response.send_message(f"Ошибка: Ты не можешь удалить самого себя.", ephemeral=True)
                return

            # Проверка, есть ли пользователь в списке
            if str(member_id) not in members:
                await inter.response.send_message(f"Ошибка: пользователь с ID {member_id} не добавлен к карте.", ephemeral=True)
                return

            member_data = members.get(str(member_id))
            channel_member_id = member_data.get("id_channel")
            message_member_id = member_data.get("id_message")
            channel_member = inter.guild.get_channel(channel_member_id)
            message_member = await channel_member.fetch_message(message_member_id)
            await message_member.delete()

            # Удаляем пользователя из списка
            del members[str(member_id)]

            # Обновляем карту
            existing_embeds = message.embeds
            color = existing_embeds[1].color
            card_embed_user = e_cards_users(inter, color, owner_name, members)
            await message.edit(embeds=[existing_embeds[0], existing_embeds[1], card_embed_user], attachments=[])

            # Обновляем сообщения всех пользователей
            for user_id, data in members.items():
                msg_id = data.get("id_message")
                channel_id = data.get("id_channel")
                channel = inter.client.get_channel(channel_id)
                message_users = await channel.fetch_message(msg_id)
                await message_users.edit(embeds=[existing_embeds[0], existing_embeds[1], card_embed_user], attachments=[])

            # Обновляем данные в базе данных
            supabase.table("cards").update({"members": json.dumps(members)}).eq("select_menu_id", message.id).execute()

            await inter.response.send_message(f"Пользователь {nickname} успешно удален с карты {full_number}!", ephemeral=True)

    modal = RemoveUserModal()
    await inter.response.send_modal(modal)





    #await inter.response.send_message(f"Вы выбрали удалить пользователя. Пользователь: {user.mention}, Сообщение ID: {message.id}, Канал: {channel.mention}", ephemeral=True)
    return 


# Передать карту
async def sm_transfer_owner(inter, user, message, channel):
    await inter.response.send_message(f"Вы выбрали передать карту. Пользователь: {user.mention}, Сообщение ID: {message.id}, Канал: {channel.mention}", ephemeral=True)
    return 




#- Неисвестный выбор
async def sm_unknown(inter, user, message, channel):
    await inter.response.send_message(f"Неизвестный выбор. Пользователь: {user.mention}, Сообщение ID: {message.id}, Канал: {channel.mention}", ephemeral=True)
    return 