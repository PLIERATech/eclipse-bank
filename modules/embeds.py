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




























def e_cards(color,full_number,type_rus,name,image):
    embed_color = None

    embed_color = embed_colors.get(color, color)

    embed = nxc.Embed(color=embed_color)
    embed.add_field(name="💳 Карта:", value=full_number, inline=True)
    embed.add_field(name="🗂️ Тип:", value=type_rus, inline=True)
    embed.add_field(name="💬 Название", value=name, inline=True)
    embed.set_image(url=f"attachment://{image}")
    embed.set_footer(text="Eclipse Bank")
    return(embed)
    