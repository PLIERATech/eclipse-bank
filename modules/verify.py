from const import *
from .embeds import *
from .log_functions import *


#! Проверка на staff роль
async def verify_staff(inter, userUsage, command):
    if not any(role.id in (staff_role) for role in userUsage.roles):
        status="No Permissions"
        embed = emb_e_noPerms()
        await inter.response.send_message(embed=embed, ephemeral=True) 
        PermsLog(inter.user.display_name, inter.user.id, command, status)
        return(False)
    return(True)



#! Проверка прав на обработку с карты CEO-00000
async def verify_ceo_card(inter, banker, number):
    if number == 0:
        if not any(role.id in (staff_role) for role in banker.roles):
            embed = emb_e_noPerms00000()
            await inter.response.send_message(embed=embed, ephemeral=True) 
            return(False)
    return(True)



#! Проверка находится ли пользователь на сервере
async def verify_user_in_server(inter, member):
    if not inter.guild.get_member(member.id):
        embed = emb_user_in_server()
        await inter.response.send_message(embed=embed, ephemeral=True) 
        return(False)
    return(True)



#! Проверка является ли пользователь клиентом
async def verify_user_is_client(inter, member):
    if not any(role.id == client_role_id for role in member.roles):
        embed = emb_user_is_client()
        await inter.response.send_message(embed=embed, ephemeral=True) 
        return(False)
    return(True)



#! Проверка является ли пользователь клиентом при удалении
async def verify_deleteAccount(inter, check):
    if not check:
        embed = emb_user_is_client()
        await inter.response.send_message(embed=embed, ephemeral=True) 
        return(False)
    return(True)



#! Проверка занятости номера карты
async def verify_num_is_claimed(inter, number):
    response = supabase.table("cards").select("number").execute()
    numbers_list = [item["number"] for item in response.data]
    if number in numbers_list:
        embed = emb_num_isClaimed()
        await inter.response.send_message(embed=embed, ephemeral=True)
        return(False)
    return(True)



#! Проверка на исчерпание лимита создания карт
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
        embed = emb_user_cardLimit()
        await inter.send(embed=embed, ephemeral=True)
        PermsLog(inter.user.display_name, inter.user.id, command, status)
        return(False) 
    return(True)



#! Проверка получилось ли создать карту
async def verify_create_card(inter, check):
    if not check:
        embed = emb_sb_cardNotCreated()
        await inter.followup.send(embed=embed, ephemeral=True)
        return(False)
    return(True)



#! Проверка не является ли пользователь уже банкиром
async def verify_dont_banker(inter, member, command):
    if any(role.id in (banker_role) for role in member.roles):
        status="isBanker"
        embed = emb_user_isBanker()
        await inter.response.send_message(embed=embed, ephemeral=True)
        PermsLog(inter.user.display_name, inter.user.id, command, status)
        return(False)
    return(True)



#! Проверка является ли банкиром
async def verify_this_banker(inter, command, member, owner):
    if owner:
        status="No Permissions"
        embed = emb_e_noPerms()
    else:
        status="is_notBanker"
        embed = emb_user_isNotBanker()

    if not any(role.id in (banker_role) for role in member.roles):
        await inter.response.send_message(embed=embed, ephemeral=True)
        PermsLog(inter.user.display_name, inter.user.id, command, status)
        return(False)
    return(True)



#! Проверка на целое число
async def verify_an_integer(inter, value):
    try:
        amount = int(value)
        if amount <= 0:
            raise ValueError
        return(True)
    except ValueError:
        embed = emb_count_an_integer()
        await inter.send(embed=embed, ephemeral=True) 
        return(False)



#! Проверка является ли номер карты цифрами
async def verify_card_int(inter, number):
    try:
        int(number)
        return(True)
    except ValueError:
        embed = emb_card_int()
        await inter.send(embed=embed, ephemeral=True) 
        return(False)



#! Проверка загрузки картинки
async def verify_image_upload(inter, url):
    if not url:
        embed = emb_e_image_upload()
        await inter.send(embed=embed, ephemeral=True) 
        return(False)
    return(True)



#! Проверка является ли карта с выставленного счёта действительной
async def verify_invoice_card(inter, check_data, message):
    if not check_data.data[0].get("cards"):
        embed = verify_dont_invoice_card()
        await inter.send(embed=embed, ephemeral=True) 
        supabase.table("invoice").delete().eq("memb_message_id", message.id).execute()
        await message.delete()
        return(False)
    return(True)



#! Не найдены данные
async def verify_found_data(inter, check_data):
    if not check_data.data[0]:
        embed = emb_e_no_found_data()
        await inter.send(embed=embed, ephemeral=True) 
        return(False)
    return(True)



#! Проверка прав на отмену счёта определенного банкира
async def verify_invoice_banker_cancel(inter, member_id, banker_id, member):
    if member_id != banker_id and not any(role.id in (staff_role) for role in member.roles):
        embed = emb_e_invoice_banker_cansel()
        await inter.send(embed=embed, ephemeral=True)
        return(False)
    return(True)



#! Проверка есть ли карты в бд
async def verify_total_card_update(inter, total):
    if total == 0:
        embed = emb_no_global_card_update()
        await inter.send(embed=embed, ephemeral=True)
        return(False)
    return(True)



#! Проверка найдена ли карта
async def verify_found_card(inter, check_data):
    if not check_data.data:
        embed = emb_no_found_card()
        await inter.send(embed=embed, ephemeral=True)
        return(False)
    return(True)



#! Проверка существует ли клиент по нику
async def verify_select_menu_client(inter, check_data, nickname):
    if not check_data.data:
        embed = emb_no_client_select_menu(nickname)
        await inter.send(embed=embed, ephemeral=True)
        return(False)
    return(True)




#! Проверка является ли карта не зарплатной
async def verify_not_banker_card(inter, type):
    if type == admCardTypes[2]:
        embed = emb_is_banker_card()
        await inter.response.send_message(embed=embed, ephemeral=True)
        return(False)
    return(True)



#! Проверка владелец ли карты в select menu
async def verify_select_menu_owner(inter, check_data):
    if not check_data.data:
        embed = emb_no_owner_select_menu()
        await inter.response.send_message(embed=embed, ephemeral=True)
        return(False)
    return(True)


#! Проверка правильности номера или владельца в invoice button
async def verify_select_pay_button(inter, check_data):
    if not check_data.data:
        embed = emb_no_card_pay_button()
        await inter.response.send_message(embed=embed, ephemeral=True)
        return(False)
    return(True)