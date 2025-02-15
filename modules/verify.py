from const import *
from .embeds import *
from .log_functions import *

# Проверка прав staffчик
async def verify_staff(inter, userUsage, command):
    if not any(role.id in (staff_role) for role in userUsage.roles):
        status="No Permissions"
        embed = e_noPerms()
        await inter.response.send_message(embed=embed, ephemeral=True) 
        PermsLog(inter.user.display_name, inter.user.id, command, status)
        return(False)
    return(True)


# Проверка находится ли человек на сервере
async def verify_user_in_server(inter, member):
    if not inter.guild.get_member(member.id):
        await inter.response.send_message("❌ Этот пользователь **не находится** на сервере!", ephemeral=True)
        return(False)
    return(True)


# Проверка имеется ли аккаунт у пользователя
async def verify_deleteAccount(inter, check):
    if not check:
        await inter.response.send_message("❌ У данного пользователя нет аккаунта!", ephemeral=True)
        return(False)
    return(True)


# Проверка написания числа
async def verify_number_lenght(inter, number):
    if number < 0 or number > 99999:
        embed = num_limit()
        await inter.response.send_message(embed=embed, ephemeral=True)
        return(False)
    return(True)


# Проверка занятости номера карты
async def verify_num_is_claimed(inter, number):
    response = supabase.table("cards").select("number").execute()
    numbers_list = [item["number"] for item in response.data]
    if number in numbers_list:
        embed = num_isClaimed()
        await inter.response.send_message(embed=embed, ephemeral=True)
        return(False)
    return(True)


# Проверка на исчерпание лимита создания карт
async def verify_count_cards(inter, member_id, command):
    response = supabase.rpc("get_card_info", {"user_id": int(member_id)}).execute()
    if not response.data:
        print("❗ Ошибка: не удалось получить данные о картах.")
        return(False)
    count_cards_allowed = response.data[0]["count_cards_allowed"]
    card_count = response.data[0]["card_count"]
    result_check = card_count < count_cards_allowed
    
    if not result_check:
        status="MaxCountCard"
        embed = user_cardLimit()
        await inter.send(embed=embed, ephemeral=True)
        PermsLog(inter.user.display_name, inter.user.id, command, status)
        return(False) 
    return(True)


# Проверка получилось ли создать карту
async def verify_create_card(inter, check):
    if not check:
        embed = sb_cardNotCreated()
        await inter.followup.send(embed=embed, ephemeral=True)
        return(False)
    return(True)


# Проверка не является ли пользователь уже банкиром
async def verify_dont_banker(inter, member, command):
    if any(role.id in (banker_role) for role in member.roles):
        status="isBanker"
        embed = user_isBanker()
        await inter.response.send_message(embed=embed, ephemeral=True)
        PermsLog(inter.user.display_name, inter.user.id, command, status)
        return(False)
    return(True)


# Проверка является ли банкиром
async def verify_this_banker(inter, command, member, owner):
    if owner:
        status="No Permissions"
        embed = e_noPerms()
    else:
        status="is_notBanker"
        embed=user_isNotBanker()

    if not any(role.id in (banker_role) for role in member.roles):
        await inter.response.send_message(embed=embed, ephemeral=True)
        PermsLog(inter.user.display_name, inter.user.id, command, status)
        return(False)
    return(True)








