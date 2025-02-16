import nextcord as nxc
from const import *
from .log_functions import *
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


# Пыставить счёт
async def sm_invoice(inter, user, message, channel):
    await inter.response.send_message(f"Вы выбрали выставить счёт. Пользователь: {user.mention}, Сообщение ID: {message.id}, Канал: {channel.mention}", ephemeral=True)
    return 


#- Настройки
# Поменять название
async def sm_change_name(inter, user, message, channel):
    await inter.response.send_message(f"Вы выбрали поменять название. Пользователь: {user.mention}, Сообщение ID: {message.id}, Канал: {channel.mention}", ephemeral=True)
    return 


#@ Добавить пользователя
# Функция для добавления пользователя
async def sm_add_user(inter, user, message, channel):
    # Класс модального окна внутри функции
    result = supabase.table("cards").select("select_menu_id").eq("select_menu_id", message.id).execute()

    if not result.data:
        # Если нет совпадений, сообщаем об ошибке
        await inter.response.send_message("Ошибка: вы не владелец этой карты.", ephemeral=True)
        return




    class AddUserModal(nxc.ui.Modal):
        def __init__(self, message_id, inter):
            super().__init__(title="Добавление пользователя к карте")
            
            # Храним ID сообщения и интеракцию
            self.message_id = message_id
            self.inter = inter
            
            # Добавление поля для ввода никнейма
            self.nickname_input = nxc.ui.TextInput(label="Никнейм пользователя", placeholder="Введите никнейм...", required=True, min_length=2, max_length=32)
            self.add_item(self.nickname_input)

        async def callback(self, inter: nxc.Interaction):
            # Получаем никнейм из поля
            nickname = self.nickname_input.value.strip()
            
            # Ищем пользователя на сервере
            member = nxc.utils.get(inter.guild.members, nick=nickname)
            if not member:
                await inter.response.send_message(f"Ошибка: пользователь с никнеймом '{nickname}' не найден на сервере.", ephemeral=True)
                return

            # Получаем ID найденного пользователя
            user_id = member.id

            if user_id == user.id:
                await inter.response.send_message(f"Ошибка: Ты не можешь добавить самого себя.", ephemeral=True)
                return


            # Шаг 4: Поиск записи по message_id в Supabase
            cards_table = supabase.table("cards").select("members").eq("select_menu_id", self.message_id).execute()

            if cards_table.data:
                card = cards_table.data[0]
                members = card["members"]

                # Проверяем, не добавлен ли уже этот пользователь
                if str(user_id) in members:
                    await inter.response.send_message(f"Ошибка: пользователь с ID {user_id} уже добавлен.", ephemeral=True)
                    return

                # Преобразуем строку в словарь, если она уже существует
                if isinstance(members, str):
                    members = json.loads(members)

                # Добавляем нового пользователя в members (обновление списка)
                members[str(user_id)] = {"id_message": 111111111111111}

                # Обновляем данные в Supabase
                supabase.table("cards").update({"members": json.dumps(members)}).eq("select_menu_id", self.message_id).execute()

                await inter.response.send_message(f"Пользователь {nickname} успешно добавлен к карте!", ephemeral=True)
            else:
                await inter.response.send_message("Ошибка: не найдено соответствующего сообщения в базе данных.", ephemeral=True)

    # Создаем и показываем модальное окно
    modal = AddUserModal(message_id=message.id, inter=inter)
    await inter.response.send_modal(modal)












    # await inter.response.send_message(f"Вы выбрали добавить пользователя. Пользователь: {user.mention}, Сообщение ID: {message.id}, Канал: {channel.mention}", ephemeral=True)
    return 


#@ Удалить пользователя
async def sm_del_user(inter, user, message, channel):
    result = supabase.table("cards").select("select_menu_id").eq("select_menu_id", message.id).execute()

    if not result.data:
        await inter.response.send_message("Ошибка: вы не владелец этой карты.", ephemeral=True)
        return

    class DelUserModal(nxc.ui.Modal):
        def __init__(self, message_id, inter):
            super().__init__(title="Удаление пользователя с карты")
            
            # Храним ID сообщения и интеракцию
            self.message_id = message_id
            self.inter = inter
            
            # Добавление поля для ввода никнейма
            self.nickname_input = nxc.ui.TextInput(label="Никнейм пользователя", placeholder="Введите никнейм...", required=True, min_length=2, max_length=32)
            self.add_item(self.nickname_input)

        async def callback(self, inter: nxc.Interaction):
            # Получаем никнейм из поля
            nickname = self.nickname_input.value.strip()

            # Ищем пользователя на сервере
            member = nxc.utils.get(inter.guild.members, nick=nickname)
            if not member:
                await inter.response.send_message(f"Ошибка: пользователь с никнеймом '{nickname}' не найден на сервере.", ephemeral=True)
                return

            # Получаем ID найденного пользователя
            user_id = member.id

            if user_id == user.id:
                await inter.response.send_message(f"Ошибка: Ты не можешь удалить самого себя.", ephemeral=True)
                return

            # Шаг 4: Поиск записи по message_id в Supabase
            cards_table = supabase.table("cards").select("members").eq("select_menu_id", self.message_id).execute()

            if cards_table.data:
                card = cards_table.data[0]
                members = card["members"]

                # Проверяем, что members - строка, и если это так, преобразуем в словарь
                if isinstance(members, str):
                    members = json.loads(members)

                # Проверяем, что пользователь действительно добавлен
                if str(user_id) not in members:
                    await inter.response.send_message(f"Ошибка: пользователь с ID {user_id} не найден в списке пользователей карты.", ephemeral=True)
                    return

                # Удаляем пользователя из списка
                del members[str(user_id)]

                # Обновляем данные в Supabase
                supabase.table("cards").update({"members": json.dumps(members)}).eq("select_menu_id", self.message_id).execute()

                await inter.response.send_message(f"Пользователь {nickname} успешно удален с карты!", ephemeral=True)
            else:
                await inter.response.send_message("Ошибка: не найдено соответствующего сообщения в базе данных.", ephemeral=True)

    # Создаем и показываем модальное окно для удаления пользователя
    modal = DelUserModal(message_id=message.id, inter=inter)
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