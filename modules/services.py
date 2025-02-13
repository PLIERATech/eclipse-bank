from const import *
from .log_functions import *
import random
from .api import *
from card_gen import *
import asyncio
import time

suffix = ""

def create_card(banker, name, nickname, type, owner_id, color, do_random: bool, adm_number, balance):

    suffixes = {
        "personal": "EBP-",
        "team": "EBT-",
        "banker": "EBS-",
        "cio": "CIO-"
    }
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

    supabase.table("cards").insert({
        "number": number,
        "name": name,
        "type": type,
        "owner": owner_id,
        "balance": balance
    }).execute()

    cardCreateLog(banker, full_number, owner_id)
    card_generate(owner_id, number, nickname, color)
    
    return full_number

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

