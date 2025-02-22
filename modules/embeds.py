import nextcord as nxc
from const import *

#! Эмбед для карт №1 (номер, тип, название)
def emb_cards(color,full_number,type_rus,name):
    embed_color = embed_colors.get(color, color)

    embed = nxc.Embed(color=embed_color)
    embed.add_field(name="💳 Карта:⠀⠀⠀⠀⠀", value=full_number, inline=True)
    embed.add_field(name="🗂️ Тип:⠀⠀⠀⠀⠀⠀", value=type_rus, inline=True)
    embed.add_field(name="💬 Название⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀", value=name, inline=True)
    return(embed)


#! Эмбед для карт №2 (картинка)
def emb_cards_image(color, filename):
    embed_color = embed_colors.get(color, color)

    embed = nxc.Embed(color=embed_color)
    embed.set_image(url=filename) 
    return(embed)


#! Эмбед для карт №3 (владлелец и пользователи карты)
def emb_cards_users(guild, color, owner_name, members):
    embed_color = embed_colors.get(color, color)
    
    embed = nxc.Embed(color=embed_color)
    embed.add_field(name="👑 Владелец:⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀", value=owner_name, inline=False)

    if not members:
        embed.add_field(name="👥 Пользователи:", value="-", inline=False)
        return embed

    user_names = []
    for user_id in members:
        if isinstance(user_id, (str, int)):
            member = guild.get_member(int(user_id))
            if member:
                user_names.append(member.display_name)
            else:
                user_names.append(f"Не найден {user_id}")
        else:
            user_names.append(f"Неверный формат ID: {user_id}")
    embed.add_field(name="👥 Пользователи:", value="\n".join(user_names), inline=False)
    return embed


#@ Успех, select_menu                                                                           
#= Посмотреть баланс

#! Успех в просмотре
def emb_check_balance(full_number, balance):
    embed = nxc.Embed(
            title="👛 Баланс", 
            color=nxc.Color.brand_green(), 
            description=(f"На карте {full_number} хранится {balance} алм. \n\n"
                        f"{bank_sign}")
            )
    return(embed)


#= Перевод средств
#! Успех в переводе

def emb_complete_transfer(sender_full_number, receiver_full_number, amount, comment):
    embed = nxc.Embed(
            title="✅ Успех, средства отправлены", 
            color=nxc.Color.brand_green())
    embed.add_field(name="💳 Откуда", value=f"{sender_full_number}", inline=True)
    embed.add_field(name="📤 Кому", value=f"{receiver_full_number}", inline=True)
    embed.add_field(name="💰 Сумма", value=f"{amount} алм", inline=False)
    embed.add_field(name="📝 Комментарий", value=f"{comment or '—'}", inline=False)
    embed.add_field(name="\u200b", value=f"{bank_sign}", inline=False)
    return(embed)
















#@ ⚠️ Предупреждение                                                                           
#! Нельзя перевести самому себе
def emb_no_self_transfer():
    embed = nxc.Embed(
        title="⚠️ Предупреждение", 
        color=nxc.Color.red(), 
        description=(f"Перевод на ту же карту невозможен! \n\n"
                    f"{bank_sign}")
        )
    return(embed)


#! Недостаточно средств
def emb_insufficient_funds():
    embed = nxc.Embed(
        title="⚠️ Предупреждение", 
        color=nxc.Color.red(), 
        description=(f"На карте недостаточно средств! \n\n"
                    f"{bank_sign}")
        )
    return(embed)


#! Не хватает прав для пользования командой
def emb_e_noPerms():
    embed = nxc.Embed(
        title="⚠️ Предупреждение", 
        color=nxc.Color.red(), 
        description=(f"У вас недостаточно прав для использования данной команды! \n\n"
                    f"{bank_sign}")
        )
    return(embed)


#! Не хватает прав для взаимодействия с картой
def emb_e_noPerms00000():
    embed = nxc.Embed(
        title="⚠️ Предупреждение", 
        color=nxc.Color.red(), 
        description=(f"У вас недостаточно прав для взаимодействия с картой CEO-00000! \n\n"
                    f"{bank_sign}")
        )
    return(embed)


#! Номер карты уже занят
def emb_num_isClaimed():
    embed = nxc.Embed(
        title="⚠️ Предупреждение", 
        color=nxc.Color.gold(), 
        description=(f"Данный номер карты уже занят. \n\n"
                    f"{bank_sign}")
        )
    return(embed)


#! Лимит карт
def emb_user_cardLimit():
    embed = nxc.Embed(
            title="⚠️ Предупреждение", 
            color=nxc.Color.gold(), 
            description=(f"У пользователя максимальное количество карт. \n\n"
                        f"{bank_sign}")
            )
    return(embed)


#! Является банкиром
def emb_user_isBanker():
    embed = nxc.Embed(
            title="⚠️ Предупреждение", 
            color=nxc.Color.gold(), 
            description=(f"Данный пользователь уже является банкиром. \n\n"
                        f"{bank_sign}")
            )
    return(embed)


#! Не банкир
def emb_user_isNotBanker():
    embed = nxc.Embed(
            title="⚠️ Предупреждение", 
            color=nxc.Color.gold(), 
            description=(f"Данный пользователь не является банкиром. \n\n"
                        f"{bank_sign}")
            )
    return(embed)


#! Пользователя нет на сервере
def emb_user_in_server():
    embed = nxc.Embed(
        title="⚠️ Предупреждение", 
        color=nxc.Color.red(), 
        description=(f"Данного пользователя нет на сервере дискорд! \n\n"
                    f"{bank_sign}")
        )
    return(embed)


#! Пользователь не клиент
def emb_user_is_client():
    embed = nxc.Embed(
        title="⚠️ Предупреждение", 
        color=nxc.Color.red(), 
        description=(f"Данный пользователь не является клиентом! \n\n"
                    f"{bank_sign}")
        )
    return(embed)


#! Не целое положительно число (0+)
def emb_count_an_integer():
    embed = nxc.Embed(
        title="⚠️ Предупреждение", 
        color=nxc.Color.red(), 
        description=(f"Сумма должна быть целым положительным числом! \n\n"
                    f"{bank_sign}")
        )
    return(embed)


#! Ввод должен быть числом
def emb_card_int():
    embed = nxc.Embed(
        title="⚠️ Предупреждение", 
        color=nxc.Color.red(), 
        description=(f"Номер карты должен состоять из чисел! \n\n"
                    f"{bank_sign}")
        )
    return(embed)


#! Ошибка загрузки картинки
def emb_e_image_upload():
    embed = nxc.Embed(
        title="⚠️ Предупреждение", 
        color=nxc.Color.red(), 
        description=(f"Изображение не загрузилось! \n\n"
                    f"{bank_sign}")
        )
    return(embed)


#! Карта со счёта больше не действительна
def verify_dont_invoice_card():
    embed = nxc.Embed(
        title="⚠️ Предупреждение", 
        color=nxc.Color.red(), 
        description=(f"Карта с которой выставлен счёт больше не действительна! \n\n"
                    f"{bank_sign}")
        )
    return(embed)


#! Данные не найдены
def emb_e_no_found_data():
    embed = nxc.Embed(
        title="⚠️ Предупреждение", 
        color=nxc.Color.red(), 
        description=(f"Данные не найдены! \n\n"
                    f"{bank_sign}")
        )
    return(embed)


#! Банкир пытается отметить не свой счёт
def emb_e_invoice_banker_cansel():
    embed = nxc.Embed(
        title="⚠️ Предупреждение", 
        color=nxc.Color.red(), 
        description=(f"У вас нет прав на отмену данного счёта! \n\n"
                    f"{bank_sign}")
        )
    return(embed)


#! Нет карт в бд для глобального обновления карт
def emb_no_global_card_update():
    embed = nxc.Embed(
        title="⚠️ Предупреждение", 
        color=nxc.Color.red(), 
        description=(f"Нет карт для обновления! \n\n"
                    f"{bank_sign}")
        )
    return(embed)


#! Карта не найдена
def emb_no_found_card():
    embed = nxc.Embed(
        title="⚠️ Предупреждение", 
        color=nxc.Color.red(), 
        description=(f"Карта не найдена! \n\n"
                    f"{bank_sign}")
        )
    return(embed)


#! Не хватает прав для пользования командой
def emb_e_noPerms():
    embed = nxc.Embed(
        title="⚠️ Предупреждение", 
        color=nxc.Color.red(), 
        description=(f"У вас недостаточно прав для использования данной команды! \n\n"
                    f"{bank_sign}")
        )
    return(embed)


#! Не хватает прав для пользования командой
def emb_e_noPerms():
    embed = nxc.Embed(
        title="⚠️ Предупреждение", 
        color=nxc.Color.red(), 
        description=(f"У вас недостаточно прав для использования данной команды! \n\n"
                    f"{bank_sign}")
        )
    return(embed)


#! Не хватает прав для пользования командой
def emb_e_noPerms():
    embed = nxc.Embed(
        title="⚠️ Предупреждение", 
        color=nxc.Color.red(), 
        description=(f"У вас недостаточно прав для использования данной команды! \n\n"
                    f"{bank_sign}")
        )
    return(embed)


#! Не хватает прав для пользования командой
def emb_e_noPerms():
    embed = nxc.Embed(
        title="⚠️ Предупреждение", 
        color=nxc.Color.red(), 
        description=(f"У вас недостаточно прав для использования данной команды! \n\n"
                    f"{bank_sign}")
        )
    return(embed)


#! Ошибка при создании карты
def emb_sb_cardNotCreated():
    embed = nxc.Embed(
        title="🚫 Ошибка", 
        color=nxc.Color.red(), 
        description=("К сожалеию, не удалось создать карту. \n"
                    "Пожалуйста, обратитесь к администрации. \n\n"
                    f"{bank_sign}")
        )
    return(embed)


#@ ✅ Успех!                                                                                    
#! Счёт удален
def emb_account_wasDeleted():
    embed = nxc.Embed(
            title="✅ Успех!", 
            color=nxc.Color.brand_green(), 
            description=(f"Банковский счёт был успешно удалён. \n\n"
                        f"{bank_sign}")
            )
    return(embed)


#! Банкир разжалован + карта
def emb_demotedBanker(card_type_rus, full_number):
    embed = nxc.Embed(
            title="✅ Успех!", 
            color=nxc.Color.brand_green(), 
            description=("Банкир разжалован. \n"
                        "Карта банкира удалена\n"
                        f"Карта типа {card_type_rus} с номером {full_number} успешно создана! \n\n"
                        f"{bank_sign}")
            )
    return(embed)


#! Банкир разжалован
def emb_demoteBankerWithCar():
    embed = nxc.Embed(
            title="✅ Успех!", 
            color=nxc.Color.brand_green(), 
            description=("Банкир разжалован. \n"
                        "Карта банкира удалена. \n\n"
                        f"{bank_sign}")
            )
    return(embed)


#! Процесс бар глобального обновления карт
def emb_updateAllCards_processbar(progress_bar, percent):
    embed = nxc.Embed(
        color=nxc.Color.brand_green(), 
        description=(f"🔄 Обновление карт: `[{progress_bar}] {percent}%` \n\n"
                    f"{bank_sign}")
        )
    return(embed)


#! Глобальное обновление карт
def emb_updateAllCards():
    embed = nxc.Embed(
        title="✅ Успех!", 
        color=nxc.Color.brand_green(), 
        description=("Обновление карт завершено. \n\n"
                    f"{bank_sign}")
        )
    return(embed)


#! Глобальное обновление карт
def emb_updateAllCards():
    embed = nxc.Embed(
        title="✅ Успех!", 
        color=nxc.Color.brand_green(), 
        description=("Обновление карт завершено. \n\n"
                    f"{bank_sign}")
        )
    return(embed)


#! Глобальное обновление карт
def emb_updateAllCards():
    embed = nxc.Embed(
        title="✅ Успех!", 
        color=nxc.Color.brand_green(), 
        description=("Обновление карт завершено. \n\n"
                    f"{bank_sign}")
        )
    return(embed)


#! Глобальное обновление карт
def emb_updateAllCards():
    embed = nxc.Embed(
        title="✅ Успех!", 
        color=nxc.Color.brand_green(), 
        description=("Обновление карт завершено. \n\n"
                    f"{bank_sign}")
        )
    return(embed)


#! Глобальное обновление карт
def emb_updateAllCards():
    embed = nxc.Embed(
        title="✅ Успех!", 
        color=nxc.Color.brand_green(), 
        description=("Обновление карт завершено. \n\n"
                    f"{bank_sign}")
        )
    return(embed)


#! Глобальное обновление карт
def emb_updateAllCards():
    embed = nxc.Embed(
        title="✅ Успех!", 
        color=nxc.Color.brand_green(), 
        description=("Обновление карт завершено. \n\n"
                    f"{bank_sign}")
        )
    return(embed)


#! Глобальное обновление карт
def emb_updateAllCards():
    embed = nxc.Embed(
        title="✅ Успех!", 
        color=nxc.Color.brand_green(), 
        description=("Обновление карт завершено. \n\n"
                    f"{bank_sign}")
        )
    return(embed)


#! Глобальное обновление карт
def emb_updateAllCards():
    embed = nxc.Embed(
        title="✅ Успех!", 
        color=nxc.Color.brand_green(), 
        description=("Обновление карт завершено. \n\n"
                    f"{bank_sign}")
        )
    return(embed)


#! Глобальное обновление карт
def emb_updateAllCards():
    embed = nxc.Embed(
        title="✅ Успех!", 
        color=nxc.Color.brand_green(), 
        description=("Обновление карт завершено. \n\n"
                    f"{bank_sign}")
        )
    return(embed)













































