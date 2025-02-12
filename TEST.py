import nextcord
from nextcord.ext import commands
from nextcord.ui import Select, View
from dotenv import load_dotenv
import json
import os

intents = nextcord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Файл для хранения данных о сообщениях
DATA_FILE = "persistent_views.json"

# Класс для Select Menu
class PersistentTestSelectView(View):
    def __init__(self):
        super().__init__(timeout=None)  # Тайм-аут отключен для персистентности

    @nextcord.ui.select(
        custom_id="persistent_select",  # Уникальный идентификатор для Select Menu
        placeholder="Выберите действие",
        options=[
            nextcord.SelectOption(label="Написать привет", value="hello", emoji="👋"),
            nextcord.SelectOption(label="Написать пока", value="bye", emoji="🚪"),
            nextcord.SelectOption(label="Написать кот", value="cat", emoji="🐱"),
        ]
    )
    async def select_callback(self, select: Select, interaction: nextcord.Interaction):
        # Обработка выбора пользователя
        if select.values[0] == "hello":
            await interaction.response.send_message("привет", ephemeral=True)
        elif select.values[0] == "bye":
            await interaction.response.send_message("пока", ephemeral=True)
        elif select.values[0] == "cat":
            await interaction.response.send_message("кот", ephemeral=True)

# Функция для сохранения данных о сообщениях
def save_message_data(channel_id, message_id):
    if not os.path.exists(DATA_FILE):
        data = []
    else:
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
    
    # Добавляем новое сообщение в данные
    data.append({"channel_id": channel_id, "message_id": message_id})
    
    # Сохраняем данные в файл
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

# Функция для загрузки данных о сообщениях
def load_message_data():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r") as f:
        return json.load(f)

@bot.event
async def on_ready():
    print(f"Бот {bot.user} готов к работе!")
    
    # Восстанавливаем View для всех сохранённых сообщений
    for entry in load_message_data():
        channel = bot.get_channel(entry["channel_id"])
        if channel:
            try:
                message = await channel.fetch_message(entry["message_id"])
                bot.add_view(PersistentTestSelectView(), message_id=message.id)
            except nextcord.NotFound:
                print(f"Сообщение {entry['message_id']} в канале {entry['channel_id']} не найдено.")
            except nextcord.Forbidden:
                print(f"Нет доступа к сообщению {entry['message_id']} в канале {entry['channel_id']}.")

@bot.slash_command(description="Тестовая команда с персистентным Select Menu")
async def test(interaction: nextcord.Interaction):
    # Отправляем сообщение с текстом "тест" и Select Menu
    view = PersistentTestSelectView()
    await interaction.response.send_message("тест", view=view)
    
    # Получаем отправленное сообщение
    message = await interaction.original_message()
    
    # Сохраняем информацию о сообщении
    save_message_data(interaction.channel_id, message.id)

token: str = os.environ.get("BOT_TOKEN")
BOT_TOKEN = str(token)

# Запуск бота
bot.run(BOT_TOKEN)