from const import *
from log_functions import *
import random
from api import *

suffix = ""

def create_card(banker, name, type, owner):

    if type == "private":
        suffix = "EBP-"
    elif type == "team":
        suffix = "EBT-"
    elif type == "banker":
        suffix == "EBS-"

    #Извлекаем номера уже существующих карт и добавляем в список
    response = supabase.table("cards").select("number").execute()
    numbers_list = [item["number"] for item in response.data]
    
    while True:
        number = int(''.join(random.choices(n, k=5)))
        if number not in numbers_list:
            break
    
    full_number = f"{suffix}{number}"

    supabase.table("cards").insert({
        "number": number,
        "name": name,
        "type": type,
        "owner": owner
    }).execute()

    cardCreateLog(banker, full_number, owner)
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