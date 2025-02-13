import os
from supabase import Client
from dotenv import load_dotenv
from supabase.lib.client_options import ClientOptions
import logging

n = "0123456789"

#-загрузка файла .env
load_dotenv()

#-Webhooks
wh_bank_audit = "https://ptb.discord.com/api/webhooks/1338930883356393575/z82Vf9NYlMruWYBJnwHq63wMA12qOEFmoRmK-WCobs0fr61wksfGCF4eePoeNvjUjShI"
wh_alary_audit = "https://ptb.discord.com/api/webhooks/1338931100315029615/-bGfub6agVX0gSk6TdELx-VnN5FCFcizYRdpi9A9hlXqOSUOp1LJsAE-qdqS59CgOzS-"
wh_stats = "https://ptb.discord.com/api/webhooks/1338931477873954876/rDgZPJxvRPu4gNlfd70JX654vkJv-JLJuNhduHolRel6qMPd8HaWlcwDlgaXvH-wcMur"

#?Поключение к базе данных Supabase
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = Client(url, key, options = ClientOptions(postgrest_client_timeout = 5, storage_client_timeout = 30))

#? Работа c API prdx.so
cookie = os.getenv("MY_COOKIE")
API_PROFILE_URL = "https://prdx.so/api/v1/user/profile?discord_id={}"
INVITE_URL = "https://prdx.so/t/eclipse/invite"
COMMUNITY_ID = "110"

#@Работа с когами
COGS_FOLDER = "cogs"
CONFIG_FILE = "cogs_config.json"


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


#*Каналы Дискорда
bank_audit_channel = 1338888321400700928
salary_channel = 1338884884441206825
stats_channel = 1338886067025084426