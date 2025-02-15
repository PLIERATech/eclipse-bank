import nextcord as nxc
from const import *
from .log_functions import *
from nextcord.ui import View, Select

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
# Проверить баланс
async def sm_check_balance(inter, user, message, channel):
    response = supabase.table("cards").select("balance, type, number").eq("select_menu_id", message.id).execute()

    if response.data:
        balance = response.data[0]['balance']
        type = response.data[0]['type']
        number = response.data[0]['number']

        await inter.response.send_message(f"На карте {suffixes.get(type)}-{number} хранится {balance} алм.", ephemeral=True)
    else:
        await inter.response.send_message(f"Данные не найдены.", ephemeral=True)
    return 


# Перевод средств
async def sm_transfer(inter, user, message, channel):
    await inter.response.send_message(f"Вы выбрали перевод средств. Пользователь: {user.mention}, Сообщение ID: {message.id}, Канал: {channel.mention}", ephemeral=True)
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


# Добавить пользователя
async def sm_add_user(inter, user, message, channel):
    await inter.response.send_message(f"Вы выбрали добавить пользователя. Пользователь: {user.mention}, Сообщение ID: {message.id}, Канал: {channel.mention}", ephemeral=True)
    return 


# Добавить пользователя
async def sm_del_user(inter, user, message, channel):
    await inter.response.send_message(f"Вы выбрали удалить пользователя. Пользователь: {user.mention}, Сообщение ID: {message.id}, Канал: {channel.mention}", ephemeral=True)
    return 


# Передать карту
async def sm_transfer_owner(inter, user, message, channel):
    await inter.response.send_message(f"Вы выбрали передать карту. Пользователь: {user.mention}, Сообщение ID: {message.id}, Канал: {channel.mention}", ephemeral=True)
    return 




#- Неисвестный выбор
async def sm_unknown(inter, user, message, channel):
    await inter.response.send_message(f"Неизвестный выбор. Пользователь: {user.mention}, Сообщение ID: {message.id}, Канал: {channel.mention}", ephemeral=True)
    return 