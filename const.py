import os
from dotenv import load_dotenv
import logging
import nextcord as nxc

n = "0123456789"

#-загрузка файла .env
load_dotenv()

#-Webhooks
wh_bank_audit = "https://ptb.discord.com/api/webhooks/1338930883356393575/z82Vf9NYlMruWYBJnwHq63wMA12qOEFmoRmK-WCobs0fr61wksfGCF4eePoeNvjUjShI"
wh_alary_audit = "https://ptb.discord.com/api/webhooks/1338931100315029615/-bGfub6agVX0gSk6TdELx-VnN5FCFcizYRdpi9A9hlXqOSUOp1LJsAE-qdqS59CgOzS-"
wh_stats = "https://ptb.discord.com/api/webhooks/1338931477873954876/rDgZPJxvRPu4gNlfd70JX654vkJv-JLJuNhduHolRel6qMPd8HaWlcwDlgaXvH-wcMur"

#? Работа c API prdx.so
cookie = os.getenv("MY_COOKIE")
API_PROFILE_URL = "https://prdx.so/api/v1/user/profile?discord_id={}"
INVITE_URL = "https://prdx.so/t/eclipse/invite"
KICK_URL = "https://prdx.so/t/eclipse"
COMMUNITY_ID = "110"

#! Работа с бд
BACKUP_FOLDER = "backup-db"
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")


#@Работа с когами
COGS_FOLDER = "cogs"
CONFIG_FILE = "cogs_config.json"

#*Работа с Embeds
bank_sign = "-# Eclipse Bank"

#//айди дискорд сервера
server_id = [1338868051222859779]

#//токен бота
token: str = os.environ.get("BOT_TOKEN")
BOT_TOKEN = str(token)


#@Роли  Дискорда
staff_role = [1338898054325080145]
banker_role = [1338875585472106537, 1338898054325080145]
player_role = [1338875732063162418]

banker_role_id = 1338875585472106537
client_role_id = 1338875692292505683


#*Каналы Дискорда
bank_audit_channel = 1338888321400700928
salary_channel = 1338884884441206825
stats_channel = 1338886067025084426
image_saver_channel = 1341363839542755399

ceo_card_channel = 1345111427329036481
ceo_transaction_channel = 1345111428411031755
banker_invoice_channel_id = 1342500616584433776

cleints_category = 1345044652759187517

#! Категории для карт

cards_category = [
    1345044652759187517,   #Категория №1
    1346182776008867840,   #Категория №2
    1346182815775064236,   #Категория №3
    1346183103323836457,   #Категория №4
    1346183137620918322,   #Категория №5
    1346183164233519155,   #Категория №6
    1346183189256999004,   #Категория №7
    1346183244894179400,   #Категория №8
    1346184229381341204,   #Категория №9
    1346184285228499008    #Категория №10
]

cards_category_reserv = 1346197001330622548


#- Дополнительные значения
suffixes = {
    "👤 Personal": "EBP-",
    "🏰 Team": "EBT-",
    "💸 Banker": "EBS-",
    "💎 CEO": "CEO-"
}

type_translate = {
    "👤 Personal": "👤 Личная",
    "🏰 Team": "🏰 Общины",
    "💸 Banker": "💸 Банкира",
    "💎 CEO": "💎 CEO"
}

message_title = {
    "Success": "✅ Успех!",
    "Warning": "⚠️ Предупреждение",
    "Error": "🚫 Ошибка"
}


#. Словари для команд
admCardTypes = ["👤 Personal", "🏰 Team", "💸 Banker", "💎 CEO"]
bankerCardType = ["👤 Personal", "🏰 Team"]
choice_color = ["⚫ Black", "⚪ White", "🔴 Red", "🟠 Orange", "🟡 Yellow", "🟢 Green", "🔵 Blue", "🟣 Purple"]

ignore_members = [436507782263603200, 187208294161448960]

embed_colors = {
        "🔴 Red": nxc.Colour.from_rgb(182, 79, 81),
        "🟠 Orange": nxc.Colour.from_rgb(220, 130, 82),
        "🟡 Yellow": nxc.Colour.from_rgb(223, 186, 66),
        "🟢 Green": nxc.Colour.from_rgb(146, 182, 79),
        "🔵 Blue": nxc.Colour.from_rgb(79, 139, 182),
        "🟣 Purple": nxc.Colour.from_rgb(137, 79, 182),
        "⚫ Black": nxc.Colour.from_rgb(41, 41, 41),
        "⚪ White": nxc.Colour.from_rgb(245, 245, 245),
        "💎 CEO": nxc.Colour.from_rgb(5, 170, 156),
        "💸 Banker": nxc.Colour.from_rgb(23, 181, 181),
        "Success": nxc.Colour.from_rgb(20, 196, 4),
        "Warning": nxc.Colour.from_rgb(255, 123, 0),
        "Error": nxc.Colour.from_rgb(186, 13, 13),
        "Other": nxc.Colour.from_rgb(20, 41, 227)
    }
reverse_embed_colors = {v: k for k, v in embed_colors.items()}


commission_replenish = {
    "1": 8,     # до скольки комиссия 1 алмаза
    "2": 24,    # до скольки комиссия 2 алмаза
    "3": 64     # до скольки комиссия 3 алмаза
                # дальше до бесконечности комиссия 4 алмаза
}


TARGET_HOURS = {12, 0} # Времена, когда нужно запускать скрипт (по системному времени)

days_freeze_delete = 30 # Сколько дней для удаления аккаунта