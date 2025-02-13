from const import *
from log_functions import *
import random
from .api import *
from card_gen import *

suffix = ""

def create_card(banker, name, type, owner, color, do_random: bool, adm_number):

    suffixes = {
        "private": "EBP-",
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
    card_generate(owner, number, name, color)
    
    return full_number

def create_client(nickname, id, account, channels):

    prdx_id = get_user_id(nickname)

    supabase.table("clients").insert({
        "nickname": nickname,
        "dsc_id": id,
        "prdx_id": prdx_id,
        "account": account,
        "channels": channels
    }).execute()

    clientCreateLog(nickname)