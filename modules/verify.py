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




