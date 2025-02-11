import requests
from const import *


def invite(display_name):
    def get_user_id(nickname):
        url = API_PROFILE_URL.format(nickname)
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
    
    prdx_user_id = get_user_id(display_name)

    if not cookie:
        print("❌ Ошибка: не найден MY_COOKIE в .env!")
        exit(1)

    headers = {
        "cookie": f"token={cookie}",
        "next-action": "6796cf04aca5c299f40270ed2de12ac75a1a2126",
    }

    data = f'["{COMMUNITY_ID}","{prdx_user_id}"]'

    response2 = requests.post(url, headers=headers, data=data)
    response_text = response2.text.strip()

    print("📥 Ответ сервера:", response_text)

    if response2.status_code == 200:
        print("✅ Успешный запрос!")
    else:
        print(f"❌ Ошибка! Код: {response2.status_code}")

def get_user_id(display_name):
        url = API_PROFILE_URL.format(display_name)
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