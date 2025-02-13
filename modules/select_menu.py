import nextcord as nxc
from const import *
from log_functions import *
from nextcord.ui import View, Select

class CardSelectView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @nxc.ui.select(
        custom_id="card_transaction",
        placeholder="Действия с картой",
        options=[
            nxc.SelectOption(label="Перевести", value="transfer"),
            nxc.SelectOption(label="Выставить счёт", value="invoice"),
        ],
    )
    async def card_transaction_callback(self, select: Select, interaction: nxc.Interaction):
        messages = {
            "transfer": "Вы выбрали перевести средства.",
            "invoice": "Вы выбрали выставить счёт.",
        }
        await interaction.response.send_message(messages.get(select.values[0], "Неизвестный выбор."), ephemeral=True)
        await interaction.message.edit(view=CardSelectView())  # Сбрасываем выбор

    @nxc.ui.select(
        custom_id="card_settings",
        placeholder="Настройки",
        options=[
            nxc.SelectOption(label="Поменять название", value="ChangeName"),
            nxc.SelectOption(label="Добавить пользователя", value="addUser"),
            nxc.SelectOption(label="Передать карту", value="transferOwner"),
            nxc.SelectOption(label="Удалить карту", value="cardDelete"),
        ],
    )
    async def card_settings_callback(self, select: Select, interaction: nxc.Interaction):
        messages = {
            "ChangeName": "Вы выбрали поменять название.",
            "addUser": "Вы выбрали добавить пользователя.",
            "transferOwner": "Вы выбрали передать карту.",
            "cardDelete": "Вы выбрали удалить карту.",
        }
        await interaction.response.send_message(messages.get(select.values[0], "Неизвестный выбор."), ephemeral=True)
        await interaction.message.edit(view=CardSelectView())  # Сбрасываем выбор
