import requests
from const import *
from db import *

#@ API для взаимодействия с prdx.so

#! Пригласить в общину
def invite_team(dsc_id):
    prdx_user_id = get_user_id(dsc_id)

    if not cookie:
        print("❌ Ошибка: не найден MY_COOKIE в .env!")
        exit(1)

    headers = {
        "cookie": f"token={cookie}",
        "next-action": "6796cf04aca5c299f40270ed2de12ac75a1a2126",
    }

    data = f'["{COMMUNITY_ID}","{prdx_user_id}"]'

    response2 = requests.post(INVITE_URL, headers=headers, data=data)
    response_text = response2.text.strip()

    print("📥 Ответ сервера:", response_text)

    if response2.status_code == 200:
        print("✅ Успешный запрос!")
    else:
        print(f"❌ Ошибка! Код: {response2.status_code}")



#! Выкинуть из общины
def kick_team(dsc_id):
    prdx_user_id = get_user_id(dsc_id)

    if not cookie:
        print("❌ Ошибка: не найден MY_COOKIE в .env!")
        exit(1)

    headers = {
        "cookie": f"token={cookie}",
        "next-action": "ef984850ad23324ae6e74229f870cc87d1959fcc",
    }

    data = f'["{COMMUNITY_ID}","{prdx_user_id}"]'

    response2 = requests.post(KICK_URL, headers=headers, data=data)
    response_text = response2.text.strip()

    print("📥 Ответ сервера:", response_text)

    if response2.status_code == 200:
        print("✅ Успешный запрос!")
    else:
        print(f"❌ Ошибка! Код: {response2.status_code}")



#! Получить prdx id пользователя по discord id
def get_user_id(dsc_id):
        url = API_PROFILE_URL.format(dsc_id)
        response = requests.get(url)

        if response.status_code != 200:
            return None

        data = response.json()
        if not data.get("status"):
            return None

        user = data["data"]
        
        if user["is_banned"] or not user["has_access"]:
            return None

        return user["id"]



#! Получить minecraft nick пользователя по discord id
def get_prdx_nickname(dsc_id):
        url = API_PROFILE_URL.format(dsc_id)
        response = requests.get(url)

        if response.status_code != 200:
            return None

        data = response.json()
        if not data.get("status"):
            return None

        user = data["data"]
        
        if user["is_banned"] or not user["has_access"]:
            return None

        return user["nick"]