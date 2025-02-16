import nextcord as nxc
from const import *


def e_noPerms():
    embed = nxc.Embed(
        title="⚠️ Предупреждение", 
        color=nxc.Color.red(), 
        description=(f"У вас недостаточно прав для использования данной команды! \n\n"
                    f"{bank_sign}")
        )
    return(embed)


def num_limit():
    embed = nxc.Embed(
        title="⚠️ Предупреждение", 
        color=nxc.Color.gold(), 
        description=(f"Параметр `number` должен быть числом из ровно 5 цифр. \n\n"
                    f"{bank_sign}")
        )
    return(embed)


def num_isClaimed():
    embed = nxc.Embed(
        title="⚠️ Предупреждение", 
        color=nxc.Color.gold(), 
        description=(f"Данный номер карты уже занят. \n\n"
                    f"{bank_sign}")
        )
    return(embed)


def user_cardLimit():
    embed = nxc.Embed(
            title="⚠️ Предупреждение", 
            color=nxc.Color.gold(), 
            description=(f"У пользователя максимальное количество карт. \n\n"
                        f"{bank_sign}")
            )
    return(embed)


def user_isBanker():
    embed = nxc.Embed(
            title="⚠️ Предупреждение", 
            color=nxc.Color.gold(), 
            description=(f"Данный пользователь уже является банкиром. \n\n"
                        f"{bank_sign}")
            )
    return(embed)


def account_wasDeleted():
    embed = nxc.Embed(
            title="✅ Успех!", 
            color=nxc.Color.brand_green(), 
            description=(f"Банковский счёт был успешно удалён. \n\n"
                        f"{bank_sign}")
            )
    return(embed)


def user_isNotBanker():
    embed = nxc.Embed(
            title="⚠️ Предупреждение", 
            color=nxc.Color.gold(), 
            description=(f"Данный пользователь не является банкиром. \n\n"
                        f"{bank_sign}")
            )
    return(embed)


def demotedbanker(card_type_rus, full_number):
    embed = nxc.Embed(
            title="✅ Успех!", 
            color=nxc.Color.brand_green(), 
            description=("Банкир разжалован. \n"
                        "Карта банкира удалена\n"
                        f"Карта типа {card_type_rus} с номером {full_number} успешно создана! \n\n"
                        f"{bank_sign}")
            )
    return(embed)


def demoteBankerWithCar():
    embed = nxc.Embed(
            title="✅ Успех!", 
            color=nxc.Color.brand_green(), 
            description=("Банкир разжалован. \n"
                        "Карта банкира удалена. \n\n"
                        f"{bank_sign}")
            )
    return(embed)


def sb_cardNotCreated():
    embed = nxc.Embed(
        title="🚫 Ошибка", 
        color=nxc.Color.red(), 
        description=("К сожалеию, не удалось создать карту. \n"
                    "Пожалуйста, обратитесь к администрации. \n\n"
                    f"{bank_sign}")
        )
    return(embed)


def emb_updateAllCards():
    embed = nxc.Embed(
        title="✅ Успех!", 
        color=nxc.Color.brand_green(), 
        description=("Обновление карт завершено. \n\n"
                    f"{bank_sign}")
        )
    return(embed)

def emb_updateAllCards_processbar(progress_bar, percent):
    embed = nxc.Embed(
        color=nxc.Color.brand_green(), 
        description=(f"🔄 Обновление карт: `[{progress_bar}] {percent}%` \n\n"
                    f"{bank_sign}")
        )
    return(embed)




















def e_cards(color,full_number,type_rus,name,image):
    embed_color = embed_colors.get(color, color)

    embed = nxc.Embed(color=embed_color)
    embed.add_field(name="💳 Карта:", value=full_number, inline=True)
    embed.add_field(name="🗂️ Тип:", value=type_rus, inline=True)
    embed.add_field(name="💬 Название", value=name, inline=True)
    if not image == None:
        embed.set_image(url=f"attachment://{image}")
    return(embed)




# def e_cards_users(color,owner_name,members):
#     embed_color = embed_colors.get(color, color)

#     embed = nxc.Embed(color=embed_color)
#     embed.add_field(name="👑 Владелец:⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀", value=owner_name, inline=False)
#     embed.add_field(name="👥 Пользователи:", value=members, inline=False)
#     return(embed)
    


# Функция для создания Embed с никнеймами пользователей
def e_cards_users(inter, color, owner_name, members):
    embed_color = embed_colors.get(color, color)
    
    embed = nxc.Embed(color=embed_color)
    embed.add_field(name="👑 Владелец:⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀", value=owner_name, inline=False)

    # Если нет пользователей, выводим сообщение об этом
    if not members:
        embed.add_field(name="👥 Пользователи:", value="-", inline=False)
        return embed

    # Составляем список никнеймов пользователей
    user_names = []
    for user_id in members:
        # Проверяем, что user_id — это строка или число, а не кортеж
        if isinstance(user_id, (str, int)):
            # Пытаемся найти пользователя в гильдии по ID
            member = inter.guild.get_member(int(user_id))
            if member:
                user_names.append(member.nick)  # Добавляем имя пользователя в список
            else:
                user_names.append(f"Не найден {user_id}")  # Если не нашли пользователя, добавляем сообщение об ошибке
        else:
            user_names.append(f"Неверный формат ID: {user_id}")  # Если user_id — это не строка или число

    # Добавляем список пользователей в embed
    embed.add_field(name="👥 Пользователи:", value="\n".join(user_names), inline=False)
    
    return embed

