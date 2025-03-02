import nextcord as nxc
from const import *
from db import *

#! Функция на вызов сообщений из бд 
def get_message_with_title(message_id, title_args=(), description_args=()):
    """Получает title и template из Supabase и форматирует их разными аргументами"""
    response = db_cursor("embeds_text").select("title_emb, description_emb").eq("id", message_id).execute()
    
    if not response.data:
        return None, None, None

    title = response.data[0]["title_emb"]
    color = embed_colors.get(title, embed_colors["Other"])
    title = message_title.get(title,title)
    description = response.data[0]["description_emb"]

    try:
        formatted_title = title % title_args if "%s" in title else title
        formatted_template = description % description_args if "%s" in description else description
    except TypeError:
        return None, None, None

    return formatted_title, formatted_template, color

# title_emb, message_emb, color_emb = get_message_with_title(
#             31, ("Иван2",), ("Иван", "алмазный меч"))


#! Автоэмбед
def emb_auto(title_emb, description_emb, color_emb):
    embed = nxc.Embed(
        title=title_emb, 
        color=color_emb, 
        description=(f"{description_emb} \n\n"
                    f"{bank_sign}")
        )
    return embed


#! Эмбед для карт №1 (номер, тип, название)
def emb_cards(color,full_number,type_rus,name):
    embed_color = embed_colors.get(color, color)

    embed = nxc.Embed(color=embed_color)
    embed.add_field(name="💳 Карта:⠀⠀⠀⠀⠀", value=full_number, inline=True)
    embed.add_field(name="🗂️ Тип:⠀⠀⠀⠀⠀⠀", value=type_rus, inline=True)
    embed.add_field(name="💬 Название⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀", value=name, inline=True)
    return embed


#! Эмбед для карт №2 (картинка)
def emb_cards_image(color, filename):
    embed_color = embed_colors.get(color, color)

    embed = nxc.Embed(color=embed_color)
    embed.set_image(url=filename) 
    return embed


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



# Цвета:
emb_color_set = embed_colors["Other"]

#@                                                                                        
#@ Команды                                                                                
#@                                                                                        

#= Обналичить (Withdraw Money) 
#! Успех в выставлении счёта на обналичивании
def emb_comp_withdraw_invoice(member_id, amount, comment):
    embed = nxc.Embed(
        title="✅ Счёт на снятие выставлен",
        color=emb_color_set
    )
    embed.add_field(name="👨‍💼 Кому", value=f"<@{member_id}>", inline=True)
    embed.add_field(name="💰 Сумма", value=f"**{amount:,} алм**", inline=True)
    embed.add_field(name="📝 Комментарий", value=comment or "—", inline=False)
    embed.add_field(name="────────────", value=f"**{bank_sign}**", inline=False)

    return embed


#! Выставленный счёт от банкира для получателя и банкира
def emb_withdraw_request(banker_id, member_id, amount, comment):
    embed = nxc.Embed(
        title="❗💵 Запрос на вывод наличных",
        color=emb_color_set
    )
    embed.add_field(name="👤 Банкир", value=f"<@{banker_id}>", inline=True)
    embed.add_field(name="👨‍💼 Получатель", value=f"<@{member_id}>", inline=True)
    embed.add_field(name="💰 Сумма", value=f"**{amount:,} алм**", inline=False)
    embed.add_field(name="📝 Комментарий", value=comment or "—", inline=False)
    embed.add_field(name="────────────", value=f"**{bank_sign}**", inline=False)

    return embed


#= Обновить все карты (Update All Cards) 
#! Процесс бар глобального обновления карт
def emb_updateAllCards_processbar(progress_bar, percent):
    embed = nxc.Embed(
        color=emb_color_set, 
        description=(f"🔄 Обновление карт: `[{progress_bar}] {percent}%` \n\n"
                    f"{bank_sign}")
        )
    return embed


#= Изъять деньги (Take Off Money) 
#! Успех в изъятии денег
def emb_comp_take_off_money(full_number, amount, comment):
    embed = nxc.Embed(
        title="✅ Изъятие средств",
        color=emb_color_set
    )
    embed.add_field(name="💳 Карта", value=f"**{full_number}**", inline=True)
    embed.add_field(name="💰 Сумма", value=f"**{amount:,} алм**", inline=True)
    embed.add_field(name="📝 Комментарий", value=comment or "—", inline=False)
    embed.add_field(name="────────────", value=f"**{bank_sign}**", inline=False)

    return embed


#! Сообщение об изъятии денег
def emb_take_off_money(admin_id, full_number, amount, comment):
    embed = nxc.Embed(
        title="❗💵 Изъятие средств",
        color=emb_color_set
    )
    embed.add_field(name="👤 Администратор", value=f"<@{admin_id}>", inline=True)
    embed.add_field(name="💳 Карта", value=f"**{full_number}**", inline=True)
    embed.add_field(name="💰 Сумма", value=f"**{amount:,} алм**", inline=False)
    embed.add_field(name="📝 Комментарий", value=comment or "—", inline=False)
    embed.add_field(name="────────────", value=f"**{bank_sign}**", inline=False)

    return embed


#= Посмотреть информацию об картах владельца (Search Cards) 
#! Успех в поиске клиента и его карт
def emb_comp_search_cards(member_id, cards):
    embed = nxc.Embed(
            title="✅ Результаты поиска", 
        color=emb_color_set, 
        description=(f"Карты клиента <@{member_id}>: \n"
                    "\n".join(card[1] for card in cards)+"\n\n"
                    f"{bank_sign}")
        )
    return embed


#= Пополнить (Replenish Money) 
#! Успех в пополнении
def emb_comp_replenish(full_number, count, commission, salary, total_amount, description, banker_id):
    embed = nxc.Embed(
        title="✅ Карта пополнена",
        color=emb_color_set
    )
    embed.add_field(name="💳 Карта", value=f"**{full_number}**", inline=False)
    embed.add_field(name="💰 Сумма", value=f"**{count} алм**", inline=True)
    embed.add_field(name="📤 Комиссия", value=f"**{commission + salary} алм**", inline=True)
    embed.add_field(name="💰 Итого", value=f"**{total_amount} алм**", inline=True)
    embed.add_field(name="📝 Комментарий", value=description or "—", inline=False)
    embed.add_field(name="👤 Банкир", value=f"<@{banker_id}>", inline=False)
    embed.add_field(name="────────────", value=f"**{bank_sign}**", inline=False)

    return embed


#! Выполнено пополнение, комиссия CEO 
def emb_replenish_ceo(full_number, count, commission, salary, banker_id):
    embed = nxc.Embed(
        title="💵 Пополнение карты пользователя",
        color=emb_color_set
    )
    embed.add_field(name="💳 Карта", value=f"**{full_number}**", inline=False)
    embed.add_field(name="💰 Сумма", value=f"**{count} алм**", inline=True)
    embed.add_field(name="📤 Комиссия", value=f"**{commission + salary} алм**", inline=True)
    embed.add_field(name="💰 Итого к пополнению CEO-00000", value=f"**{commission} алм**", inline=False)
    embed.add_field(name="👤 Банкир", value=f"<@{banker_id}>", inline=False)
    embed.add_field(name="────────────", value=f"**{bank_sign}**", inline=False)

    return embed


#! Выполнено пополнение для пользователей карты получателя 
def emb_replenish_user(full_number, count, commission, salary, total_amount, description, banker_id):
    embed = nxc.Embed(
        title="💵 Пополнение карты",
        color=emb_color_set
    )
    embed.add_field(name="💳 Карта", value=f"**{full_number}**", inline=False)
    embed.add_field(name="💰 Сумма", value=f"**{count} алм**", inline=True)
    embed.add_field(name="📤 Комиссия", value=f"**{commission + salary} алм**", inline=True)
    embed.add_field(name="💰 Итого", value=f"**{total_amount} алм**", inline=True)
    embed.add_field(name="📝 Комментарий", value=description or "—", inline=False)
    embed.add_field(name="👤 Банкир", value=f"<@{banker_id}>", inline=False)
    embed.add_field(name="────────────", value=f"**{bank_sign}**", inline=False)

    return embed


#! Выполнено пополнение, комиссия банкира 
def emb_replenish_banker(full_number, salary):
    embed = nxc.Embed(
        title="💵 Пополнение карты",
        color=emb_color_set
    )
    embed.add_field(name="💳 Карта", value=f"**{full_number}**", inline=False)
    embed.add_field(name="💰 Сумма", value=f"**{salary} алм**", inline=False)
    embed.add_field(name="📝 Комментарий", value="Комиссия с пополнения чужой карты", inline=False)
    embed.add_field(name="────────────", value=f"**{bank_sign}**", inline=False)

    return embed


#! Пополнение баланса 
def emb_banker_chat_replenish(banker_id, member_full_number, banker_full_number, commission, salary, total_amount, comment):
    embed = nxc.Embed(
        title="Пополнение баланса", 
        color=emb_color_set, 
        description=(f"👤 Банкир <@{banker_id}> пополнил баланс карты {member_full_number}."))
    embed.add_field(name="👨‍💼 Получатель", value=f"{member_full_number} ({total_amount} алм.)", inline=True)
    embed.add_field(name="📤 Комисия", value=f"({commission + salary} алм.)", inline=True)
    embed.add_field(name="💰 ЗП с комиссии", value=f"{banker_full_number} ({salary} алм.)", inline=True)
    embed.add_field(name="📝 Комментарий", value=f"{comment or '—'}", inline=False)
    embed.add_field(name="────────────", value=f"**{bank_sign}**", inline=False)
    return embed




#! Создание карты 
def emb_banker_chat_new_card(banker_id, member_id, full_number, banker_full_number, commission, salary):
    embed = nxc.Embed(
        title="Создание карты", 
        color=emb_color_set, 
        description=(f"👤 Банкир <@{banker_id}> создал карту {full_number} для <@{member_id}>."))
    embed.add_field(name="📤 Стоимость", value=f"({commission + salary} алм.)", inline=True)
    embed.add_field(name="💰 ЗП со стоимости", value=f"{banker_full_number} ({salary} алм.)", inline=True)
    embed.add_field(name="────────────", value=f"**{bank_sign}**", inline=False)
    return embed


#! Выполнено пополнение, комиссия CEO 
def emb_new_card_ceo(full_number, count, commission, banker_id):
    embed = nxc.Embed(
        title=f"💳 Создание карты {full_number} для клиента",
        color=emb_color_set
    )
    embed.add_field(name="💰 Стоимость", value=f"**{count} алм**", inline=True)
    embed.add_field(name="💰 К пополнению CEO-00000", value=f"**{commission} алм**", inline=True)
    embed.add_field(name="👤 Банкир", value=f"<@{banker_id}>", inline=False)
    embed.add_field(name="────────────", value=f"**{bank_sign}**", inline=False)

    return embed


#! Выполнено пополнение, комиссия банкира 
def emb_new_card_banker(full_number, salary):
    embed = nxc.Embed(
        title="💵 Пополнение карты",
        color=emb_color_set
    )
    embed.add_field(name="💳 Карта", value=f"**{full_number}**", inline=False)
    embed.add_field(name="💰 Сумма", value=f"**{salary} алм**", inline=False)
    embed.add_field(name="📝 Комментарий", value="Зарплата за создание карты для клиента", inline=False)
    embed.add_field(name="────────────", value=f"**{bank_sign}**", inline=False)

    return embed



#! Создание клиента 
def emb_banker_chat_give_client(banker_id, member_id, banker_full_number, salary):
    embed = nxc.Embed(
        title="Выдача статуса клиента", 
        color=emb_color_set, 
        description=(f"👤 Банкир <@{banker_id}> сделал клиентом <@{member_id}>."))
    embed.add_field(name="📤 Стоимость", value=f"({salary} алм.)", inline=True)
    embed.add_field(name="💰 ЗП со стоимости", value=f"{banker_full_number} ({salary} алм.)", inline=True)
    embed.add_field(name="────────────", value=f"**{bank_sign}**", inline=False)
    return embed


#! Выполнено пополнение, комиссия банкира 
def emb_give_client_banker(full_number, salary):
    embed = nxc.Embed(
        title="💵 Пополнение карты",
        color=emb_color_set
    )
    embed.add_field(name="💳 Карта", value=f"**{full_number}**", inline=False)
    embed.add_field(name="💰 Сумма", value=f"**{salary} алм**", inline=False)
    embed.add_field(name="📝 Комментарий", value="Зарплата с создания клиента", inline=False)
    embed.add_field(name="────────────", value=f"**{bank_sign}**", inline=False)

    return embed


#@ select_menu                                                                            

#= Перевод средств 
#! Успех в переводе
def emb_comp_transfer(sender_full_number, receiver_full_number, amount, comment):
    embed = nxc.Embed(
        title="✅ Средства отправлены", 
        color=emb_color_set
    )
    embed.add_field(name="💳 Откуда", value=f"**{sender_full_number}**", inline=True)
    embed.add_field(name="📤 Кому", value=f"**{receiver_full_number}**", inline=True)
    embed.add_field(name="💰 Сумма", value=f"**{amount} алм**", inline=False)
    embed.add_field(name="📝 Комментарий", value=f"{comment or '—'}", inline=False)
    embed.add_field(name="────────────", value=f"**{bank_sign}**", inline=False)

    return embed


#! Выполненый перевод для пользователей карты отправителя
def emb_transfer_sender(member_id, sender_full_number, receiver_full_number, amount, comment):
    embed = nxc.Embed(
        title="🚀 Средства переведены", 
        color=emb_color_set
    )
    embed.add_field(name="💼 Кем", value=f"<@{member_id}>", inline=True)
    embed.add_field(name="💳 Откуда", value=f"**{sender_full_number}**", inline=True)
    embed.add_field(name="📤 Кому", value=f"**{receiver_full_number}**", inline=True)
    embed.add_field(name="💰 Сумма", value=f"**{amount} алм**", inline=False)
    embed.add_field(name="📝 Комментарий", value=f"{comment or '—'}", inline=False)
    embed.add_field(name="────────────", value=f"**{bank_sign}**", inline=False)

    return embed



#! Выполненый перевод для пользователей карты получателя
def emb_transfer_receimer(member_id, sender_full_number, receimer_full_number, amount, comment):
    embed = nxc.Embed(
        title="💵 Поступили средства", 
        color=emb_color_set
    )
    embed.add_field(name="💼 Кем", value=f"<@{member_id}>", inline=True)
    embed.add_field(name="💳 Откуда", value=f"**{sender_full_number}**", inline=True)
    embed.add_field(name="📤 Куда", value=f"**{receimer_full_number}**", inline=True)
    embed.add_field(name="💰 Сумма", value=f"**{amount} алм**", inline=False)
    embed.add_field(name="📝 Комментарий", value=f"{comment or '—'}", inline=False)
    embed.add_field(name="────────────", value=f"**{bank_sign}**", inline=False)

    return embed



#= Выставить счёт 
#! Успех в выставлении счёта
def emb_comp_invoice(nick_id, amount, comment):
    embed = nxc.Embed(
        title="✅ Выставлен счёт", 
        color=emb_color_set
    )
    embed.add_field(name="👨‍💼 Кому", value=f"<@{nick_id}>", inline=True)
    embed.add_field(name="💰 Сумма", value=f"**{amount} алм**", inline=True)
    embed.add_field(name="📝 Комментарий", value=f"{comment or '—'}", inline=False)
    embed.add_field(name="────────────", value=f"**{bank_sign}**", inline=False)

    return embed



#! Сообщение о выставленном счёте для пользователей карты отправителя
def emb_invoice_sender(sender_id, nick_id, amount, comment):
    embed = nxc.Embed(
            title="🚀 Выставлен счёт", 
            color=emb_color_set
    )
    embed.add_field(name="💼 От кого", value=f"**<@{sender_id}>**", inline=True)
    embed.add_field(name="👨‍💼 Кому", value=f"<@{nick_id}>", inline=True)
    embed.add_field(name="💰 Сумма", value=f"**{amount} алм**", inline=False)
    embed.add_field(name="📝 Комментарий", value=f"{comment or '—'}", inline=False)
    embed.add_field(name="────────────", value=f"**{bank_sign}**", inline=False)

    return embed



#! Сообщение о выставленном счёте для получившего
def emb_invoice_nick(sender_id, sender_full_number, amount, comment):
    embed = nxc.Embed(
        title="❗💵 Запрос средств", 
        color=emb_color_set
    )
    embed.add_field(name="💼 От кого", value=f"<@{sender_id}>", inline=True)
    embed.add_field(name="💳 На карту", value=f"{sender_full_number}", inline=True)
    embed.add_field(name="💰 Сумма", value=f"**{amount} алм**", inline=False)
    embed.add_field(name="📝 Комментарий", value=f"{comment or '—'}", inline=False)
    embed.add_field(name="────────────", value=f"**{bank_sign}**", inline=False)

    return embed



#@ invoice_button                                                                             

#= Подтвердить счёт 

#! Выполненый перевод для пользователей карты отправителя
def emb_member_pay_button(member_id, member_full_number, invoice_full_number, amount, comment, invoice_own_id):
    embed = nxc.Embed(
        title="✅ Счёт оплачен", 
        color=emb_color_set
    )
    embed.add_field(name="👨‍💼 Оплачено", value=f"<@{member_id}>", inline=True)
    embed.add_field(name="💳 Откуда", value=f"{member_full_number}", inline=True)
    embed.add_field(name="📤 Кому", value=f"{invoice_full_number}", inline=True)
    embed.add_field(name="💰 Сумма", value=f"**{amount} алм**", inline=False)
    embed.add_field(name="📝 Комментарий", value=f"{comment or '—'}", inline=False)
    embed.add_field(name="💼 Запросивший", value=f"<@{invoice_own_id}>", inline=False)
    embed.add_field(name="────────────", value=f"**{bank_sign}**", inline=False)

    return embed

#! Выполненый перевод для пользователей карты получателя
def emb_invoice_pay_button(member_id, member_full_number, invoice_full_number, amount, comment, invoice_own_id):
    embed = nxc.Embed(
            title=f"✅ Счёт оплачен", 
            color=emb_color_set
    )
    embed.add_field(name="👨‍💼 Оплачен", value=f"<@{member_id}>", inline=True)
    embed.add_field(name="💳 От", value=f"{member_full_number}", inline=True)
    embed.add_field(name="📤 Куда", value=f"{invoice_full_number}", inline=True)
    embed.add_field(name="💰 Сумма", value=f"{amount} алм", inline=False)
    embed.add_field(name="📝 Комментарий", value=f"{comment or '—'}", inline=False)
    embed.add_field(name="💼 Запросивший", value=f"<@{invoice_own_id}>", inline=False)
    embed.add_field(name="────────────", value=f"**{bank_sign}**", inline=False)
    return embed


#! Выполненый перевод для пользователей карты отправителя от банкира
def emb_member_pay_button_banker(member_id, member_full_number, amount, comment, invoice_own_id):
    embed = nxc.Embed(
            title=f"✅ Счёт оплачен", 
            color=emb_color_set)
    embed.add_field(name="👨‍💼 Оплачен", value=f"<@{member_id}>", inline=True)
    embed.add_field(name="💳 Откуда", value=f"{member_full_number}", inline=True)
    embed.add_field(name="📤 Действие:", value=f"снятие наличных", inline=True)
    embed.add_field(name="💰 Сумма", value=f"{amount} алм", inline=False)
    embed.add_field(name="📝 Комментарий", value=f"{comment or '—'}", inline=False)
    embed.add_field(name="👤 Банкир", value=f"<@{invoice_own_id}>", inline=False)
    embed.add_field(name="────────────", value=f"**{bank_sign}**", inline=False)
    return embed


#! Отредактированное сообщение банкира для проверки счёта
def emb_banker_invoice_message(member_id, amount, invoice_own_id):
    embed = nxc.Embed(
            title=f"✅ Счёт оплачен", 
            color=emb_color_set)
    embed.add_field(name="👨‍💼 Оплачен", value=f"<@{member_id}>", inline=True)
    embed.add_field(name="📤 Действие:", value=f"снятие наличных", inline=True)
    embed.add_field(name="💰 Сумма", value=f"{amount} алм", inline=False)
    embed.add_field(name="👤 Банкир", value=f"<@{invoice_own_id}>", inline=False)
    embed.add_field(name="────────────", value=f"**{bank_sign}**", inline=False)
    return embed




#@ ----------------------------------------------------------------------------------------------
#@ АУДИТ                                                                                         
#@ ----------------------------------------------------------------------------------------------


#! Пополнение баланса 
def emb_aud_replenishMoney(banker_id, member_full_number, banker_full_number, commission, salary, total_amount, comment):
    embed = nxc.Embed(
        title="Пополнение баланса", 
        color=emb_color_set, 
        description=(f"Банкир <@{banker_id}> пополнил баланс карты {member_full_number}."))
    embed.add_field(name="Получатель", value=f"{member_full_number} ({total_amount} алм.)", inline=True)
    embed.add_field(name="Комисия", value=f"({commission + salary} алм.)", inline=True)
    embed.add_field(name="ЗП с комиссии", value=f"{banker_full_number} ({salary} алм.)", inline=True)
    embed.add_field(name="📝 Комментарий", value=f"{comment or '—'}", inline=False)
    embed.add_field(name="────────────", value=f"**{bank_sign}**", inline=False)
    return embed


#! Подтверждён выставленный счёт игрока 
def emb_aud_invoice_pay_member(member_id, invoice_card_own_id, member_full_number, invoice_full_number, amount, comment):
    embed = nxc.Embed(
        title="Подтверждён счёт игрока", 
        color=emb_color_set, 
        description=(f"Клиент <@{member_id}> подтвердил счёт выставленный <@{invoice_card_own_id}>."))
    embed.add_field(name="Снятие из", value=f"{member_full_number}", inline=True)
    embed.add_field(name="Начисление в", value=f"{invoice_full_number}", inline=True)
    embed.add_field(name="Сумма", value=f"{amount} алм.", inline=True)
    embed.add_field(name="📝 Комментарий", value=f"{comment or '—'}", inline=False)
    embed.add_field(name="────────────", value=f"**{bank_sign}**", inline=False)
    return embed


#! Подтверждён выставленный счёт банкира 
def emb_aud_invoice_pay_banker(member_id, invoice_card_own_id, member_full_number, amount, comment):
    embed = nxc.Embed(
        title="Подтверждён счёт банкира", 
        color=emb_color_set, 
        description=(f"Клиент <@{member_id}> подтвердил счёт выставленный банкиром <@{invoice_card_own_id}>."))
    embed.add_field(name="Снятие из", value=f"{member_full_number}", inline=True)
    embed.add_field(name="Сумма", value=f"{amount} алм.", inline=True)
    embed.add_field(name="📝 Комментарий", value=f"{comment or '—'}", inline=False)
    embed.add_field(name="────────────", value=f"**{bank_sign}**", inline=False)
    return embed


#! Перевод средств 
def emb_aud_transfer(member_id, sender_full_number, receiver_full_number, amount, comment):
    embed = nxc.Embed(
        title="Выполнил перевод средств", 
        color=emb_color_set, 
        description=(f"Клиент <@{member_id}> перевёл средства."))
    embed.add_field(name="Снятие из", value=f"{sender_full_number}", inline=True)
    embed.add_field(name="Начисление в", value=f"{receiver_full_number}", inline=True)
    embed.add_field(name="Сумма", value=f"{amount} алм.", inline=True)
    embed.add_field(name="📝 Комментарий", value=f"{comment or '—'}", inline=False)
    embed.add_field(name="────────────", value=f"**{bank_sign}**", inline=False)
    return embed