from const import *
from .log_functions import *
import random
from .api import *
from card_gen import *
import asyncio
import time

suffix = ""

def create_card(banker, name, nickname, type, owner, color, do_random: bool, adm_number):

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
        "owner": owner
    }).execute()

    cardCreateLog(banker, full_number, owner)
    card_generate(owner, number, nickname, color)
    
    return full_number

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
