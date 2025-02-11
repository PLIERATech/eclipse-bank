import os
from supabase import Client
from dotenv import load_dotenv
from supabase.lib.client_options import ClientOptions
import nextcord as nxc

#-загрузка файла .env
load_dotenv()


#-Webhooks


#?Поключение к базе данных Supabase
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = Client(url, key, options = ClientOptions(postgrest_client_timeout = 5, storage_client_timeout = 30))


#@Работа с когами
COGS_FOLDER = "cogs"
CONFIG_FILE = "cogs_config.json"


#//айди дискорд сервера
server_id = []

#//токен бота
token: str = os.environ.get("BOT_TOKEN")
BOT_TOKEN = str(token)


#@Роли  Дискорда


#*Каналы Дискорда
