import nextcord as nxc
import random
import asyncio
import time
from const import *
from .log_functions import *
from .api import *
from card_gen import *

suffix = ""

def create_card(banker, name, nickname, type, owner_id, color, do_random: bool, adm_number, balance):
    
    suffix = suffixes.get(type)

    #Извлекаем номера уже существующих карт и добавляем в список
    response = supabase.table("cards").select("number").execute()
    numbers_list = [item["number"] for item in response.data]
    if do_random == True:
        while True:
            number =  f"{int(''.join(random.choices(n, k=5))):05}"
            if number not in numbers_list:
                break
    else:
        number = adm_number
    
    full_number = f"{suffix}{number}"

    check = supabase.table("cards").insert({
        "number": number,
        "name": name,
        "type": type,
        "owner": owner_id,
        "balance": balance
    }).execute()

    if not check.data:
        return [full_number, False]

    cardCreateLog(banker, full_number, owner_id)
    card_generate(full_number,type, nickname, color)
    
    return [full_number, True]

async def delete_card(channel_card_id, message_card_id, bot):
    channel = bot.get_channel(channel_card_id)
    message = await channel.fetch_message(message_card_id)
    await message.delete()
    return

def create_client(nickname, id, account, channels):

    prdx_id = get_user_id(id)

    supabase.table("clients").insert({
        "nickname": nickname,
        "dsc_id": id,
        "prdx_id": prdx_id,
        "account": account,
        "channels": channels
    }).execute()

    clientCreateLog(nickname)

async def deleteCardImages(interval):
    while True:
        try:
            current_time = time.time()
            folder_path = "card_gen/cards"

            for filename in os.listdir(folder_path):
                file_path = os.path.join(folder_path, filename)

                # Проверяем, что это файл + время последнего изменения
                if os.path.isfile(file_path) and filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                    file_age = current_time - os.path.getmtime(file_path)  # Время в секундах

                    if file_age > 60:  # Файл старше 60 секунд
                        os.remove(file_path)
        except Exception as e:
            print(f"Ошибка при удалении файлов: {e}")

        await asyncio.sleep(interval)  # Асинхронная пауза

def check_count_cards(member_id):
    response = supabase.rpc("get_card_info", {"user_id": int(member_id)}).execute()

    if not response.data:
        print("❗ Ошибка: не удалось получить данные о картах.")
        return None  # Ошибка получения данных

    count_cards_allowed = response.data[0]["count_cards_allowed"]
    card_count = response.data[0]["card_count"]

    return card_count < count_cards_allowed  # True - можно создать карту, False - нельзя

def get_card_info_demote(member_id):
    response = supabase.rpc("get_user_cards_demote", {"user_id": member_id}).execute()

    if response.data:
        result = response.data[0]
        return {
            "banker_balance": result["banker_balance"],
            "banker_select_menu_id": result["banker_select_menu_id"],
            "banker_number": result["banker_number"],
            "non_banker_number": result["non_banker_number"],
            "non_banker_type": result["non_banker_type"],
            "channels_user": result["channels_user"]
        }
    return None


async def createAccount(guild, owner):

    card_name = owner.display_name
    owner_id = owner.id
        
    #*Работа с пользователями
    #Проверка является ли пользователь уже зарегестрированным пользователем
    response = supabase.table("clients").select("dsc_id").execute()
    clients_dsc_id_list = [item["dsc_id"] for item in response.data]
    if owner_id not in clients_dsc_id_list:
        #? Создание категории-Банковского счёта
        #! Создаём категорию с доступом только для указанного пользователя
        category = await guild.create_category(card_name, overwrites={
            guild.default_role: nxc.PermissionOverwrite(view_channel=False),  # Запрещаем доступ всем
            owner: nxc.PermissionOverwrite(view_channel=True, read_messages=True, read_message_history=True)  # Разрешаем только owner
        })
        #! Канал "Транзакции" - только чтение
        transactions_channel = await guild.create_text_channel("🧮ㆍТранзакции", category=category, overwrites={
            guild.default_role: nxc.PermissionOverwrite(view_channel=False),
            owner: nxc.PermissionOverwrite(view_channel=True, read_message_history=True, read_messages=True, send_messages=False)  # Только чтение
        })
        #! Канал "Карты" - только чтение
        cards_channel = await guild.create_text_channel("💳ㆍКарты", category=category, overwrites={
            guild.default_role: nxc.PermissionOverwrite(view_channel=False),
            owner: nxc.PermissionOverwrite(view_channel=True, read_message_history=True, read_messages=True, send_messages=False)  # Только чтение
        })

        channels = [transactions_channel.id, cards_channel.id]

        #=Создание клиента
        create_client(card_name, owner_id, category.id, channels)
    return

async def deleteAccount(guild, owner):
    owner_id = owner.id
    
    response_dsc_id = supabase.table("clients").select("dsc_id, account, channels").eq("dsc_id", owner_id).execute()

    if not response_dsc_id.data:
        return(False)

    if response_dsc_id.data:
        clients_category_id = int(response_dsc_id.data[0]["account"])
        clients_channels_ids = list(map(int, response_dsc_id.data[0]["channels"].strip("[]").split(",")))

        category = guild.get_channel(clients_category_id)
        if category:
            await category.delete()

        for channel_id in clients_channels_ids:
            channel = guild.get_channel(channel_id)
            if channel:
                await channel.delete()

        supabase.rpc("delete_account", {"client_id": owner_id}).execute()

        clientDeleteLog(owner.display_name)
        return(True)
