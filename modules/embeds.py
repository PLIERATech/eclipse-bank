import nextcord as nxc
from const import *
from db import *

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


#@ Команды                                                                                

#= Обналичить (Withdraw Money) 
#! Успех в выставлении счёта на обналичивании
def emb_comp_withdram_invoice(member_id, amount, comment):
    embed = nxc.Embed(
            title="✅ Счёт на снятие выставлен", 
            color=nxc.Color.brand_green())
    embed.add_field(name="👨‍💼 Кому", value=f"<@{member_id}>", inline=False)
    embed.add_field(name="💰 Сумма", value=f"{amount} алм", inline=False)
    embed.add_field(name="📝 Комментарий", value=f"{comment or '—'}", inline=False)
    embed.add_field(name="\u200b", value=f"{bank_sign}", inline=False)
    return(embed)


#! Выставленный счёт от банкира для получателя и банкира
def emb_withdram_request(banker_id, member_id, amount, comment):
    embed = nxc.Embed(
            title="❗💵 Запрос на вывод наличных", 
            color=nxc.Color.brand_green())
    embed.add_field(name="👤 От банкира", value=f"<@{banker_id}>", inline=True)
    embed.add_field(name="👨‍💼 Кому", value=f"<@{member_id}>", inline=True)
    embed.add_field(name="💰 Сумма", value=f"{amount} алм", inline=False)
    embed.add_field(name="📝 Комментарий", value=f"{comment or '—'}", inline=False)
    embed.add_field(name="\u200b", value=f"{bank_sign}", inline=False)
    return(embed)


#= Обновить все карты (Update All Cards) 
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


#= Деньги хранящиеся в банке (Total Balance) 
#! Узнать сколько деняг хранится в банке
def emb_total_balance(total):
    embed = nxc.Embed(
            title="✅ Общий баланс!", 
            color=nxc.Color.brand_green(), 
            description=(f"В банке хранится {total} алм.! ({total // 9} аб + {total - (total // 9 * 9)} алм.) \n\n"
                        f"{bank_sign}")
            )
    return(embed)


#= Изъять деньги (Take Off Money) 
#! Успех в изъятии денег
def emb_comp_take_off_money(full_number, amount, comment):
    embed = nxc.Embed(
            title="✅ Изъятие средств", 
            color=nxc.Color.brand_green())
    embed.add_field(name="💳 Из карты", value=f"{full_number}", inline=False)
    embed.add_field(name="💰 Сумма", value=f"{amount} алм", inline=False)
    embed.add_field(name="📝 Комментарий", value=f"{comment or '—'}", inline=False)
    embed.add_field(name="\u200b", value=f"{bank_sign}", inline=False)
    return(embed)


#! Сообщение об изъятии денег
def emb_take_off_money(admin_id, full_number, amount, comment):
    embed = nxc.Embed(
            title="❗💵 Изъятие средств", 
            color=nxc.Color.brand_green())
    embed.add_field(name="👤 Администратор", value=f"<@{admin_id}>", inline=False)
    embed.add_field(name="💳 Из карты", value=f"{full_number}", inline=False)
    embed.add_field(name="💰 Сумма", value=f"{amount} алм", inline=False)
    embed.add_field(name="📝 Комментарий", value=f"{comment or '—'}", inline=False)
    embed.add_field(name="\u200b", value=f"{bank_sign}", inline=False)
    return(embed)


#= Посмотреть информацию об картах владельца (Search Cards) 
#! Успех в поиске клиента и его карт
def emb_comp_search_cards(member_id, cards):
    embed = nxc.Embed(
            title=f"✅ Карты клиента <@{member_id}>", 
        color=nxc.Color.brand_green(), 
        description=("\n".join(card[2] for card in cards)+"\n\n"
                    f"{bank_sign}")
        )
    return(embed)


#! У клиента нет карт
def emb_no_cards_search(member_id):
    embed = nxc.Embed(
        title="⚠️ Предупреждение", 
        color=nxc.Color.red(), 
        description=(f"У клиента <@{member_id}> нет карт. \n\n"
                    f"{bank_sign}")
        )
    return(embed)


#= Пополнить (Replenish Money) 
#! Успех в пополнении
def emb_comp_replenish(full_number, count, commission, salary, total_amount, description, banker_id):
    embed = nxc.Embed(
            title="✅ Карта пополнена", 
            color=nxc.Color.brand_green())
    embed.add_field(name="💳 Карта", value=f"{full_number}", inline=False)
    embed.add_field(name="💰 Сумма", value=f"{count}", inline=True)
    embed.add_field(name="📤 Комиссия", value=f"{commission+salary}", inline=True)
    embed.add_field(name="💰 Итого", value=f"{total_amount}", inline=True)
    embed.add_field(name="📝 Комментарий", value=f"{description or '—'}", inline=False)
    embed.add_field(name="👤 Банкир", value=f"<@{banker_id}>", inline=False)
    embed.add_field(name="\u200b", value=f"{bank_sign}", inline=False)
    return(embed)


#! Выполнено пополнение, комиссия CEO 
def emb_replenish_ceo(full_number, count, commission, salary, total_amount, description, banker_id):
    embed = nxc.Embed(
            title="💵 Пополнение карты пользователя", 
            color=nxc.Color.brand_green())
    embed.add_field(name="💳 Карта", value=f"{full_number}", inline=False)
    embed.add_field(name="💰 Сумма", value=f"{count}", inline=True)
    embed.add_field(name="📤 Комиссия", value=f"{commission+salary}", inline=True)
    embed.add_field(name="💰 Итого к пополнению CEO-00000", value=f"{commission}", inline=False)
    embed.add_field(name="👤 Банкир", value=f"<@{banker_id}>", inline=False)
    embed.add_field(name="\u200b", value=f"{bank_sign}", inline=False)
    return(embed)


#! Выполнено пополнение для пользователей карты получателя 
def emb_replenish_user(full_number, count, commission, salary, total_amount, description, banker_id):
    embed = nxc.Embed(
            title="💵 Пополнение карты", 
            color=nxc.Color.brand_green())
    embed.add_field(name="💳 Карта", value=f"{full_number}", inline=False)
    embed.add_field(name="💰 Сумма", value=f"{count}", inline=True)
    embed.add_field(name="📤 Комиссия", value=f"{commission+salary}", inline=True)
    embed.add_field(name="💰 Итого", value=f"{total_amount}", inline=True)
    embed.add_field(name="📝 Комментарий", value=f"{description or '—'}", inline=False)
    embed.add_field(name="👤 Банкир", value=f"<@{banker_id}>", inline=False)
    embed.add_field(name="\u200b", value=f"{bank_sign}", inline=False)
    return(embed)


#! Выполнено пополнение, комиссия банкира 
def emb_replenish_banker(full_number, salary):
    embed = nxc.Embed(
            title="💵 Пополнение карты", 
            color=nxc.Color.brand_green())
    embed.add_field(name="💳 Карта", value=f"{full_number}", inline=False)
    embed.add_field(name="💰 Сумма", value=f"{salary}", inline=False)
    embed.add_field(name="📝 Комментарий", value=f"Комиссия с пополнение чужой карты", inline=False)
    embed.add_field(name="\u200b", value=f"{bank_sign}", inline=False)
    return(embed)


#! Карта банкира не найдена 
def emb_no_found_banker_card():
    embed = nxc.Embed(
        title="⚠️ Предупреждение", 
        color=nxc.Color.red(), 
        description=(f"Для данного действия у вас должна быть карта банкира! \n\n"
                    f"{bank_sign}")
        )
    return(embed)


#= Уволить банкира (Demote) 
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


#= Удалить клиента (Delete Account) 
#! Счёт удален
def emb_account_wasDeleted():
    embed = nxc.Embed(
            title="✅ Успех!", 
            color=nxc.Color.brand_green(), 
            description=(f"Банковский счёт был успешно удалён. \n\n"
                        f"{bank_sign}")
            )
    return(embed)


#@ select_menu                                                                            

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
def emb_comp_transfer(sender_full_number, receiver_full_number, amount, comment):
    embed = nxc.Embed(
            title="✅ Средства отправлены", 
            color=nxc.Color.brand_green())
    embed.add_field(name="💳 Откуда", value=f"{sender_full_number}", inline=True)
    embed.add_field(name="📤 Кому", value=f"{receiver_full_number}", inline=True)
    embed.add_field(name="💰 Сумма", value=f"{amount} алм", inline=False)
    embed.add_field(name="📝 Комментарий", value=f"{comment or '—'}", inline=False)
    embed.add_field(name="\u200b", value=f"{bank_sign}", inline=False)
    return(embed)


#! Выполненый перевод для пользователей карты отправителя
def emb_transfer_sender(sender_full_number, receiver_full_number, amount, comment):
    embed = nxc.Embed(
            title="🚀 Средства переведены", 
            color=nxc.Color.brand_green())
    embed.add_field(name="💳 Откуда", value=f"{sender_full_number}", inline=True)
    embed.add_field(name="📤 Кому", value=f"{receiver_full_number}", inline=True)
    embed.add_field(name="💰 Сумма", value=f"{amount} алм", inline=False)
    embed.add_field(name="📝 Комментарий", value=f"{comment or '—'}", inline=False)
    embed.add_field(name="\u200b", value=f"{bank_sign}", inline=False)
    return(embed)


#! Выполненый перевод для пользователей карты получателя
def emb_transfer_receimer(sender_full_number, receiver_full_number, amount, comment):
    embed = nxc.Embed(
            title="💵 Поступили средства", 
            color=nxc.Color.brand_green())
    embed.add_field(name="💳 От", value=f"{sender_full_number}", inline=True)
    embed.add_field(name="📤 Куда", value=f"{receiver_full_number}", inline=True)
    embed.add_field(name="💰 Сумма", value=f"{amount} алм", inline=False)
    embed.add_field(name="📝 Комментарий", value=f"{comment or '—'}", inline=False)
    embed.add_field(name="\u200b", value=f"{bank_sign}", inline=False)
    return(embed)


#= Выставить счёт 
#! Успех в выставлении счёта
def emb_comp_invoice(nick_id, amount, comment):
    embed = nxc.Embed(
            title="✅ Выставлен счёт", 
            color=nxc.Color.brand_green())
    embed.add_field(name="👨‍💼 Кому", value=f"<@{nick_id}>", inline=False)
    embed.add_field(name="💰 Сумма", value=f"{amount} алм", inline=False)
    embed.add_field(name="📝 Комментарий", value=f"{comment or '—'}", inline=False)
    embed.add_field(name="\u200b", value=f"{bank_sign}", inline=False)
    return(embed)


#! Сообщение о выставленном счёте для пользователей карты отправителя
def emb_invoice_sender(sender_nick, nick_id, amount, comment):
    embed = nxc.Embed(
            title="🚀 Выставлен счёт", 
            color=nxc.Color.brand_green())
    embed.add_field(name="🤑 Кем", value=f"{sender_nick}", inline=True)
    embed.add_field(name="👨‍💼 Кому", value=f"<@{nick_id}>", inline=True)
    embed.add_field(name="💰 Сумма", value=f"{amount} алм", inline=False)
    embed.add_field(name="📝 Комментарий", value=f"{comment or '—'}", inline=False)
    embed.add_field(name="\u200b", value=f"{bank_sign}", inline=False)
    return(embed)


#! Сообщение о выставленном счёте для получившего
def emb_invoice_nick(sender_id, sender_full_number, amount, comment):
    embed = nxc.Embed(
            title="❗💵 Запрос средств", 
            color=nxc.Color.brand_green())
    embed.add_field(name="🤑 От", value=f"<@{sender_id}>", inline=True)
    embed.add_field(name="💳 На карту", value=f"{sender_full_number}", inline=True)
    embed.add_field(name="💰 Сумма", value=f"{amount} алм", inline=False)
    embed.add_field(name="📝 Комментарий", value=f"{comment or '—'}", inline=False)
    embed.add_field(name="\u200b", value=f"{bank_sign}", inline=False)
    return(embed)


#= Поменять название 
#! Успех в смене названия
def emb_comp_change_name(full_number, cardname):
    embed = nxc.Embed(
            title="✅ Изменено название", 
        color=nxc.Color.brand_green(), 
        description=(f"Название карты {full_number} изменено на {cardname}. \n\n"
                    f"{bank_sign}")
        )
    return(embed)


#! Нельзя ставить одинаковые названия карты
def emb_same_name():
    embed = nxc.Embed(
        title="⚠️ Предупреждение", 
        color=nxc.Color.red(), 
        description=(f"Название уже используется этой картой. Введите другое название! \n\n"
                    f"{bank_sign}")
        )
    return(embed)


#= Добавить пользователя к карте 
#! Успех в добавлении пользователя
def emb_comp_add_user(nick_id, full_number):
    embed = nxc.Embed(
            title="✅ Пользователь добавлен", 
        color=nxc.Color.brand_green(), 
        description=(f"Пользователь <@{nick_id}> успешно добавлен к карте {full_number}! \n\n"
                    f"{bank_sign}")
        )
    return(embed)


#! Нельзя добавить самого себя
def emb_self_add_card():
    embed = nxc.Embed(
        title="⚠️ Предупреждение", 
        color=nxc.Color.red(), 
        description=(f"Ты не можешь добавить к карте самого себя! \n\n"
                    f"{bank_sign}")
        )
    return(embed)


#! Нельзя добавлять тех кто уже добавлен к карте
def emb_no_replay_add(nick):
    embed = nxc.Embed(
        title="⚠️ Предупреждение", 
        color=nxc.Color.red(), 
        description=(f"Клиент {nick} уже добавлен к карте! \n\n"
                    f"{bank_sign}")
        )
    return(embed)


#= Удалить пользователя из карты 
#! Успех в удалении пользователя из карты
def emb_comp_del_user_in_card(nick_id, full_number):
    embed = nxc.Embed(
            title="✅ Пользователь удалён", 
        color=nxc.Color.brand_green(), 
        description=(f"Пользователь <@{nick_id}> успешно удалён из карты {full_number}! \n\n"
                    f"{bank_sign}")
        )
    return(embed)


#! Нельзя удалять себя из карты
def emb_self_del_card():
    embed = nxc.Embed(
        title="⚠️ Предупреждение", 
        color=nxc.Color.red(), 
        description=(f"Ты не можешь удалить из карты самого себя! \n\n"
                    f"{bank_sign}")
        )
    return(embed)


#! Нельзя удалять тех кто не добавлен к карте
def emb_no_added_in_card(member_id):
    embed = nxc.Embed(
        title="⚠️ Предупреждение", 
        color=nxc.Color.red(), 
        description=(f"Клиент <@{member_id}> не добавлен к карте. \n\n"
                    f"{bank_sign}")
        )
    return(embed)


#= Передать владение картой
#! Успех в передачи прав на карту 
def emb_comp_transfer_owner(member_id, full_number):
    embed = nxc.Embed(
            title="✅ Владение картой передано", 
        color=nxc.Color.brand_green(), 
        description=(f"Пользователь <@{member_id}> успешно стал владельцем карты {full_number}! \n\n"
                    f"{bank_sign}")
        )
    return(embed)


#! Нельзя передать карту самому себе
def emb_self_transfer_owner():
    embed = nxc.Embed(
        title="⚠️ Предупреждение", 
        color=nxc.Color.red(), 
        description=(f"Ты не можешь передать карту самому себе! \n\n"
                    f"{bank_sign}")
        )
    return(embed)


#! Нельзя передать владение если клиент не добавлен в пользователи
def emb_no_added_in_card_transfer(member_id):
    embed = nxc.Embed(
        title="⚠️ Предупреждение", 
        color=nxc.Color.red(), 
        description=(f"Клиент <@{member_id}> должен быть пользователем карты.\n"
                     f"Перед передачей карты, добавьте его в пользователи \n\n"
                    f"{bank_sign}")
        )
    return(embed)


#= Удалить карту 
#! Успех в удалении карты 
def emb_comp_delete_card(full_number):
    embed = nxc.Embed(
            title="✅ Карта удалена", 
        color=nxc.Color.brand_green(), 
        description=(f"Карта {full_number} успешно удалена! \n\n"
                    f"{bank_sign}")
        )
    return(embed)


#! Карта банкира не найдена 
def emb_no_delete_card_balance():
    embed = nxc.Embed(
        title="⚠️ Предупреждение", 
        color=nxc.Color.red(), 
        description=(f"Для удаления карты, на ней не должно быть средств! \n\n"
                    f"{bank_sign}")
        )
    return(embed)


#! Карта неправильно введена 
def emb_no_delete_card_wrong_number():
    embed = nxc.Embed(
        title="⚠️ Предупреждение", 
        color=nxc.Color.red(), 
        description=(f"Для данной операции вы должны правильно написать название карты! \n\n"
                    f"{bank_sign}")
        )
    return(embed)




#@ invoice_button                                                                             

#= Подтвердить счёт 
#! Успех в потдверждении
def emb_comp_pay_button():
    embed = nxc.Embed(
            title="✅ Счёт подтверждён", 
            color=nxc.Color.brand_green(), 
            description=(f"\n"
                        f"{bank_sign}")
            )
    return(embed)


#! Недостаточно средств
def emb_no_card_pay_button():
    embed = nxc.Embed(
        title="⚠️ Предупреждение", 
        color=nxc.Color.red(), 
        description=(f"Указанный номер карты не существует или вы не являетесь её владельцем/пользователем! \n\n"
                    f"{bank_sign}")
        )
    return(embed)

#! Выполненый перевод для пользователей карты отправителя
def emb_member_pay_button(member_id, member_full_number, invoice_full_number, amount, comment, invoice_own_id):
    embed = nxc.Embed(
            title=f"✅ Счёт оплачен", 
            color=nxc.Color.brand_green())
    embed.add_field(name="👨‍💼 Оплачен", value=f"<@{member_id}>", inline=False)
    embed.add_field(name="💳 Откуда", value=f"{member_full_number}", inline=True)
    embed.add_field(name="📤 Кому", value=f"{invoice_full_number}", inline=True)
    embed.add_field(name="💰 Сумма", value=f"{amount} алм", inline=False)
    embed.add_field(name="📝 Комментарий", value=f"{comment or '—'}", inline=False)
    embed.add_field(name="🤑 Запросивший", value=f"<@{invoice_own_id}>", inline=False)
    embed.add_field(name="\u200b", value=f"{bank_sign}", inline=False)
    return(embed)


#! Выполненый перевод для пользователей карты получателя
def emb_invoice_pay_button(member_id, member_full_number, invoice_full_number, amount, comment, invoice_own_id):
    embed = nxc.Embed(
            title=f"✅ Счёт оплачен", 
            color=nxc.Color.brand_green())
    embed.add_field(name="👨‍💼 Оплачен", value=f"<@{member_id}>", inline=False)
    embed.add_field(name="💳 От", value=f"{member_full_number}", inline=True)
    embed.add_field(name="📤 Куда", value=f"{invoice_full_number}", inline=True)
    embed.add_field(name="💰 Сумма", value=f"{amount} алм", inline=False)
    embed.add_field(name="📝 Комментарий", value=f"{comment or '—'}", inline=False)
    embed.add_field(name="🤑 Запросивший", value=f"<@{invoice_own_id}>", inline=False)
    embed.add_field(name="\u200b", value=f"{bank_sign}", inline=False)
    return(embed)


#! Выполненый перевод для пользователей карты отправителя от банкира
def emb_member_pay_button_banker(member_id, member_full_number, amount, comment, invoice_own_id):
    embed = nxc.Embed(
            title=f"✅ Счёт оплачен", 
            color=nxc.Color.brand_green())
    embed.add_field(name="👨‍💼 Оплачен", value=f"<@{member_id}>", inline=False)
    embed.add_field(name="💳 Откуда", value=f"{member_full_number}", inline=False)
    embed.add_field(name="📤 Действие:", value=f"снятие наличных", inline=False)
    embed.add_field(name="💰 Сумма", value=f"{amount} алм", inline=False)
    embed.add_field(name="📝 Комментарий", value=f"{comment or '—'}", inline=False)
    embed.add_field(name="👤 Банкир", value=f"<@{invoice_own_id}>", inline=False)
    embed.add_field(name="\u200b", value=f"{bank_sign}", inline=False)
    return(embed)


#! Отредактированное сообщение банкира для проверки счёта
def emb_banker_invoice_message(member_id, amount, invoice_own_id):
    embed = nxc.Embed(
            title=f"✅ Счёт оплачен", 
            color=nxc.Color.brand_green())
    embed.add_field(name="👨‍💼 Оплачен", value=f"<@{member_id}>", inline=False)
    embed.add_field(name="📤 Действие:", value=f"снятие наличных", inline=False)
    embed.add_field(name="💰 Сумма", value=f"{amount} алм", inline=False)
    embed.add_field(name="👤 Банкир", value=f"<@{invoice_own_id}>", inline=False)
    embed.add_field(name="\u200b", value=f"{bank_sign}", inline=False)
    return(embed)


#= Отмена 
#! Успех счёт отменён
def emb_comp_decline_button():
    embed = nxc.Embed(
            title="❌ Счёт отменён", 
            color=nxc.Color.brand_green(), 
            description=(f"\n"
                        f"{bank_sign}")
            )
    return(embed)


#! Сообщение для банкира или пользователей 
def emb_msg_decline_button(member_id, amount):
    embed = nxc.Embed(
            title="❌ Счёт отменён", 
            color=nxc.Color.brand_green(), 
            description=(f"<@{member_id}> отменил выставленный счён на сумму {amount} алм. \n\n"
                        f"{bank_sign}")
            )
    return(embed)


#= Отмена банкиром 
#! Успех счёт отменён банкиром 
def emb_comp_cancel_button():
    embed = nxc.Embed(
            title="❌ Счёт отменён", 
            color=nxc.Color.brand_green(), 
            description=(f"\n"
                        f"{bank_sign}")
            )
    return(embed)


#! Сообщение для пользователя 
def emb_edit_member_cancel_button(member_id, amount):
    embed = nxc.Embed(
            title="❌ Счёт отменён", 
            color=nxc.Color.brand_green(), 
            description=(f"Счёт выставленный банкиром <@{member_id}> на сумму `{amount} алм.` отменён \n\n"
                        f"{bank_sign}")
            )
    return(embed)


#! Сообщение для банкира или пользователей 
def emb_edit_bancer_cancel_button(member_id):
    embed = nxc.Embed(
            title="❌ Счёт отменён", 
            color=nxc.Color.brand_green(), 
            description=(f"Счёт отменён банкиром <@{member_id}> \n\n"
                        f"{bank_sign}")
            )
    return(embed)


#= Выставить счёт 
#! Успех в выставлении счёта
def emb_comp_invoice(nick_id, amount, comment):
    embed = nxc.Embed(
            title="✅ Выставлен счёт", 
            color=nxc.Color.brand_green())
    embed.add_field(name="👨‍💼 Кому", value=f"<@{nick_id}>", inline=False)
    embed.add_field(name="💰 Сумма", value=f"{amount} алм", inline=False)
    embed.add_field(name="📝 Комментарий", value=f"{comment or '—'}", inline=False)
    embed.add_field(name="\u200b", value=f"{bank_sign}", inline=False)
    return(embed)


#! Сообщение о выставленном счёте для пользователей карты отправителя
def emb_invoice_sender(sender_nick, nick_id, amount, comment):
    embed = nxc.Embed(
            title="🚀 Выставлен счёт", 
            color=nxc.Color.brand_green())
    embed.add_field(name="🤑 Кем", value=f"{sender_nick}", inline=True)
    embed.add_field(name="👨‍💼 Кому", value=f"<@{nick_id}>", inline=True)
    embed.add_field(name="💰 Сумма", value=f"{amount} алм", inline=False)
    embed.add_field(name="📝 Комментарий", value=f"{comment or '—'}", inline=False)
    embed.add_field(name="\u200b", value=f"{bank_sign}", inline=False)
    return(embed)


#! Сообщение о выставленном счёте для получившего
def emb_invoice_nick(sender_id, sender_full_number, amount, comment):
    embed = nxc.Embed(
            title="❗💵 Запрос средств", 
            color=nxc.Color.brand_green())
    embed.add_field(name="🤑 От", value=f"<@{sender_id}>", inline=True)
    embed.add_field(name="💳 На карту", value=f"{sender_full_number}", inline=True)
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


#! С зарплатной картой взаимодействоватьнельзя
def emb_is_banker_card():
    embed = nxc.Embed(
        title="⚠️ Предупреждение", 
        color=nxc.Color.red(), 
        description=(f"Данные действия с зарплатной картой запрещены! \n\n"
                    f"{bank_sign}")
        )
    return(embed)


#! Не является владельцем для операции с картой
def emb_no_owner_select_menu():
    embed = nxc.Embed(
        title="⚠️ Предупреждение", 
        color=nxc.Color.red(), 
        description=(f"Не хватает прав для этого действия! \n\n"
                    f"{bank_sign}")
        )
    return(embed)


#! Клиента не существует в select menu
def emb_no_client_select_menu(nickname):
    embed = nxc.Embed(
        title="⚠️ Предупреждение", 
        color=nxc.Color.red(), 
        description=(f"Клиент с никнеймом {nickname} не найден, проверьте правильно ли написан никнейм и является ли он клиентом.! \n\n"
                    f"{bank_sign}")
        )
    return(embed)


#! Ошибка неизвестный выбор select menu
def emb_sb_e_select_menu():
    embed = nxc.Embed(
        title="🚫 Ошибка", 
        color=nxc.Color.red(), 
        description=("Неизвестный выбор действия. \n"
                    "Пожалуйста, обратитесь к администрации. \n\n"
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








#@ ----------------------------------------------------------------------------------------------
#@ АУДИТ                                                                                         
#@ ----------------------------------------------------------------------------------------------

#! Создание кастомной карты админом 
def emb_aud_createCustomCard(full_number, member_id, admin_id):
    embed = nxc.Embed(
        title="Создание кастомной карты админом", 
        color=nxc.Color.brand_green(), 
        description=(f"Создана карта {full_number} для клиента <@{member_id}>. \n"
                    f"Администратор: <@{admin_id}>. \n\n"
                    f"{bank_sign}")
        )
    return(embed)


#! Создание карты банкиром 
def emb_aud_createCard(full_number, member_id, banker_id):
    embed = nxc.Embed(
        title="Создание карты банкиром", 
        color=nxc.Color.brand_green(), 
        description=(f"Создана карта {full_number} для клиента <@{member_id}>. \n"
                    f"Банкир: <@{banker_id}>. \n\n"
                    f"{bank_sign}")
        )
    return(embed)


#! Нанимание банкира 
def emb_aud_admitBanker(member_id, full_number, admin_id):
    embed = nxc.Embed(
        title="Банкир нанят", 
        color=nxc.Color.brand_green(), 
        description=(f"Банкир <@{member_id}> принят на службу и получил зарплатную карту {full_number}. \n"
                    f"Назначил администратор: <@{admin_id}>.\n\n"
                    f"{bank_sign}")
        )
    return(embed)


#! Разжалование банкира + создание карты с балансом 
def emb_aud_demoteBanker_create_card(full_number, member_id, balance, admin_id):
    embed = nxc.Embed(
        title="Банкир разжалован", 
        color=nxc.Color.brand_green(), 
        description=(f"Банкир <@{member_id}> разжалован и получил карту {full_number} с балансом {balance} алм. \n"
                    f"Разжаловал администратор: <@{admin_id}>.\n\n"
                    f"{bank_sign}")
        )
    return(embed)


#! Разжалование банкира + перевод средств на первую карту 
def emb_aud_demoteBanker_send_balance(full_number, member_id, balance, admin_id):
    embed = nxc.Embed(
        title="Банкир разжалован", 
        color=nxc.Color.brand_green(), 
        description=(f"Банкир <@{member_id}> разжалован и {balance} алм. переведено на карту {full_number}. \n"
                    f"Разжаловал администратор: <@{admin_id}>.\n\n"
                    f"{bank_sign}")
        )
    return(embed)


#! Разжалование банкира 
def emb_aud_demoteBanker(member_id, admin_id):
    embed = nxc.Embed(
        title="Банкир разжалован", 
        color=nxc.Color.brand_green(), 
        description=(f"Банкир <@{member_id}> разжалован. \n"
                    f"Разжаловал администратор: <@{admin_id}>.\n\n"
                    f"{bank_sign}")
        )
    return(embed)


#! Удаление карты 
def emb_aud_deleteAccount(member_id, admin_id):
    embed = nxc.Embed(
        title="Клиент удалён", 
        color=nxc.Color.brand_green(), 
        description=(f"Клиент <@{member_id}> был удалён администратором <@{admin_id}>. \n\n"
                    f"{bank_sign}")
        )
    return(embed)


#! Автоматическое удаление карты 
def emb_aud_autoDeleteAccount(member_id):
    embed = nxc.Embed(
        title="Клиент удалён автомотически", 
        color=nxc.Color.brand_green(), 
        description=(f"Клиент <@{member_id}> был заморожен и был удален за незаход на сервер {days_freeze_delete} дней. \n\n"
                    f"{bank_sign}")
        )
    return(embed)


#! Клиент вернулся на сервер 
def emb_aud_member_join(member_id):
    embed = nxc.Embed(
        title="Клиент вернулся на сервер", 
        color=nxc.Color.brand_green(), 
        description=(f"Клиент <@{member_id}> вернулся на сервер и его аккаунт был разморожен. \n\n"
                    f"{bank_sign}")
        )
    return(embed)


#! Клиент вышел с сервера 
def emb_aud_member_remove(member_id):
    embed = nxc.Embed(
        title="Клиент вышел с сервера", 
        color=nxc.Color.brand_green(), 
        description=(f"Клиент <@{member_id}> вышел с сервера и его аккаунт был заморожен. \n\n"
                    f"{bank_sign}")
        )
    return(embed)


#! Пополнение баланса 
def emb_aud_replenishMoney(banker_id, member_full_number, banker_full_number, commission, salary, total_amount, comment):
    embed = nxc.Embed(
        title="Пополнение баланса", 
        color=nxc.Color.brand_green(), 
        description=(f"Банкир <@{banker_id}> пополнил баланс карты {member_full_number}."))
    embed.add_field(name="Получатель", value=f"{member_full_number} ({total_amount} алм.)", inline=True)
    embed.add_field(name="Комисия", value=f"CEO-00000 ({commission} алм.)", inline=True)
    embed.add_field(name="ЗП с комиссии", value=f"{banker_full_number} ({salary} алм.)", inline=True)
    embed.add_field(name="📝 Комментарий", value=f"{comment or '—'}", inline=False)
    embed.add_field(name="\u200b", value=f"{bank_sign}", inline=False)
    return(embed)


#! Обновил все карты 
def emb_aud_updateAllCards(member_id):
    embed = nxc.Embed(
        title="Обновлены все карты", 
        color=nxc.Color.brand_green(), 
        description=(f"Администратор <@{member_id}> обновил все карты банка. \n\n"
                    f"{bank_sign}")
        )
    return(embed)


#! Изъятие средств 
def emb_aud_takeOffMoney(admin_id, full_number, amount, comment):
    embed = nxc.Embed(
        title="Изъятие средств", 
        color=nxc.Color.brand_green(), 
        description=(f"Администратор <@{admin_id}> изъял с карты {full_number} - {amount} алм. \n"
                     f"Комментарий: {comment}\n\n"
                    f"{bank_sign}"))
    return(embed)


#! Обналичивание средств 
def emb_aud_withdrawMoney(banker_id, member_id, count, comment):
    embed = nxc.Embed(
        title="Выставлен счёт на снятие средств", 
        color=nxc.Color.brand_green(), 
        description=(f"Банкир <@{banker_id}> выставил счёт клиенту <@{member_id}> на снятие {count} алм. \n"
                     f"Комментарий: {comment}\n\n"
                    f"{bank_sign}"))
    return(embed)


#! Подтверждён выставленный счёт игрока 
def emb_aud_invoice_pay_member(member_id, invoice_card_own_id, member_full_number, invoice_full_number, amount, comment):
    embed = nxc.Embed(
        title="Подтверждён счёт игрока", 
        color=nxc.Color.brand_green(), 
        description=(f"Клиент <@{member_id}> подтвердил счёт выставленный <@{invoice_card_own_id}>."))
    embed.add_field(name="Снятие из", value=f"{member_full_number}", inline=True)
    embed.add_field(name="Начисление в", value=f"{invoice_full_number}", inline=True)
    embed.add_field(name="Сумма", value=f"{amount} алм.", inline=True)
    embed.add_field(name="📝 Комментарий", value=f"{comment or '—'}", inline=False)
    embed.add_field(name="\u200b", value=f"{bank_sign}", inline=False)
    return(embed)


#! Подтверждён выставленный счёт банкира 
def emb_aud_invoice_pay_banker(member_id, invoice_card_own_id, member_full_number, amount, comment):
    embed = nxc.Embed(
        title="Подтверждён счёт банкира", 
        color=nxc.Color.brand_green(), 
        description=(f"Клиент <@{member_id}> подтвердил счёт выставленный банкиром <@{invoice_card_own_id}>."))
    embed.add_field(name="Снятие из", value=f"{member_full_number}", inline=True)
    embed.add_field(name="Сумма", value=f"{amount} алм.", inline=True)
    embed.add_field(name="📝 Комментарий", value=f"{comment or '—'}", inline=False)
    embed.add_field(name="\u200b", value=f"{bank_sign}", inline=False)
    return(embed)


#! Отказ на выставленный счёт игрока 
def emb_aud_invoice_decline_member(member_id, invoice_member_id, count):
    embed = nxc.Embed(
        title="Отказ счёта игрока", 
        color=nxc.Color.brand_green(), 
        description=(f"Клиент <@{member_id}> отказался от счёта выставленный <@{invoice_member_id}> на снятие {count} алм. \n\n"
                    f"{bank_sign}"))
    return(embed)


#! Отказ на выставленный счёт банкира 
def emb_aud_invoice_decline_banker(member_id, banker_id, count):
    embed = nxc.Embed(
        title="Отказ счёта банкира", 
        color=nxc.Color.brand_green(), 
        description=(f"Клиент <@{member_id}> отказался от счёта выставленный банкиром <@{banker_id}> на снятие {count} алм. \n\n"
                    f"{bank_sign}"))
    return(embed)


#! Банкир отменил высталвенный счёт 
def emb_aud_invoice_cancel_banker(banker_id, member_id, count):
    embed = nxc.Embed(
        title="Банкир отменил высталвенный счёт", 
        color=nxc.Color.brand_green(), 
        description=(f"Банкир <@{banker_id}> отменил счёта выставленный клиенту <@{member_id}> на снятие {count} алм. \n\n"
                    f"{bank_sign}"))
    return(embed)


#! Создан клиент 
def emb_aud_create_client(member_id):
    embed = nxc.Embed(
        title="Новый клиент", 
        color=nxc.Color.brand_green(), 
        description=(f"<@{member_id}> стал клиентом Eclipse Bank. \n\n"
                    f"{bank_sign}"))
    return(embed)










