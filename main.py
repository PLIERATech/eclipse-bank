
#* ==============================
#*         ИМПОРТЫ               
#* ==============================
from const import *  
import nextcord
from nextcord.ext import commands
import os
import json
import logging
import asyncio
from modules import *

#* ==============================
#*       НАСТРОЙКА ЛОГГЕРА       
#* ==============================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | 📋 %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

#* ==============================
#*     СОЗДАНИЕ ОБЪЕКТА БОТА     
#* ==============================
intents = nextcord.Intents.default()
intents.message_content = True
intents.messages = True
intents.guilds = True
intents.members = True
bot = commands.Bot(command_prefix=".", intents=intents)

#@ ==================================
#@ ФУНКЦИЯ: bot_ready()              
#@ Выводит информацию о запуске бота 
#@ ==================================
def bot_ready(bot):
    header = "🚀 БОТ ГОТОВ К РАБОТЕ 🚀"
    separator = "═" * 30

    logging.info(f"{header}\n{separator}\n"
                f"🤖 Бот: {bot.user}\n"
                f"🆔 ID: {bot.user.id}\n"
                f"📅 Подключён к {len(bot.guilds)} серверам\n"
                f"👥 Всего пользователей: {sum(g.member_count for g in bot.guilds)}\n {separator}\n")

#? =================================
#? ФУНКЦИЯ: cogs_list()             
#? Логирует список загруженных COGs 
#? =================================
def cogs_list(cogs):
    header = "📂 ЗАГРУЖЕННЫЕ COGS 📂"
    separator = "─" * len(header)

    formatted_list = "\n".join(
        [f"✅ {cog_name.ljust(20)} | {'🟢 Включен' if enabled else '🔴 Выключен'}"
        for cog_name, enabled in cogs.items()]
    )

    logging.info(f"\n{header}\n{separator}\n{formatted_list}\n")

#= =================================
#= ФУНКЦИЯ: generate_cogs_config()  
#= Генерирует/обновляет конфиг COGs 
#= =================================
def generate_cogs_config():
    cogs = [file[:-3] for file in os.listdir(COGS_FOLDER) if file.endswith(".py")]

    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as file:
            config = json.load(file)
    else:
        config = {}

    for cog in cogs:
        if cog not in config:
            config[cog] = True

    with open(CONFIG_FILE, "w") as file:
        json.dump(config, file, indent=4)

    logging.info("🔄 Конфигурация COGS обновлена.")
    return config

#- ==================================
#- ФУНКЦИЯ: load_cogs()              
#- Загружает COGs, выводит их статус 
#- ==================================
def load_cogs(bot):
    config = generate_cogs_config()
    
    all_cogs = {}

    for cog_name, enabled in config.items():
        try:
            if enabled:
                bot.load_extension(f"cogs.{cog_name}")
            all_cogs[cog_name] = enabled  # Запоминаем все коги
        except Exception as e:
            logging.error(f"❌ Ошибка загрузки {cog_name}: {e}")
            all_cogs[cog_name] = False

    cogs_list(all_cogs)

#@ ==============================
#@ ОБРАБОТЧИК СОБЫТИЯ on_ready   
#@ ==============================
@bot.event
async def on_ready():
    try:
        await bot.sync_application_commands()
        logging.info("✅ Слэш-команды успешно синхронизированы!")
    except Exception as e:
        logging.error(f"❌ Ошибка синхронизации слэш-команд: {e}")

    bot_ready(bot)
    await start_persistent_view(bot)
    await check_and_refresh_threads(bot)
    await asyncio.gather(deleteCardImages(60), scheduler(bot))

#// ==============================
#// СКРЫТИЕ ЛОГОВ NEXTCORD        
#// ==============================
nextcord_logger = logging.getLogger("nextcord")
nextcord_logger.setLevel(logging.ERROR)

#* Запускаем загрузку COGs 
load_cogs(bot)

#* Запуск бота 
bot.run(BOT_TOKEN)