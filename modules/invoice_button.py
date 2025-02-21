from nextcord.ext import commands
import nextcord as nxc
from const import *
from .verify import *

class MyPersistentView(nxc.ui.View):
    def __init__(self):
        super().__init__(timeout=None)  # Ставим timeout=None, чтобы кнопки оставались активными


#@ ---------------------------------------------------------------------------------------------------------------------------------
#@                                                     Подтвердить счёт                                                             
#@ ---------------------------------------------------------------------------------------------------------------------------------
    @nxc.ui.button(label="Оплатить", style=nxc.ButtonStyle.green)
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

                # Проверка является ли номер карты цифрами
                if not await verify_card_int(inter, user_card):
                    return
























        await inter.response.send_modal(MyModal())



#@ ---------------------------------------------------------------------------------------------------------------------------------
#@                                                         Отказаться                                                               
#@ ---------------------------------------------------------------------------------------------------------------------------------

    @nxc.ui.button(label="Отказаться", style=nxc.ButtonStyle.red)
    async def disable_button(self, button: nxc.ui.Button, inter: nxc.Interaction):
        await inter.response.edit_message(view=None)  # Удаляет кнопки

























# Засунуть в ready_func
    # bot.add_view(MyPersistentView())  # Добавляем View при запуске бота

# засунуть в отправку сообщения 
    # await ctx.send("Выберите действие:", view=MyPersistentView())

