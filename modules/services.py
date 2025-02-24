import nextcord as nxc
import random
import asyncio
import time
import datetime
from datetime import datetime, timedelta
from const import *
from .log_functions import *
from .api import *
from .select_menu import *
from .embeds import *
from card_gen import *


#! Создать карту и записать в бд
async def create_card(banker, name, nickname, type, owner_id, color, do_random: bool, adm_number, balance):

    # Извлекаем номера уже существующих карт и добавляем в список
    response = supabase.table("cards").select("number").execute()
    numbers_list = [item["number"] for item in response.data]
    if do_random == True:
        while True:
            number =  f"{int(''.join(random.choices(n, k=5))):05}"
            if number not in numbers_list:
                break
    else:
        number = adm_number
    
    full_number = f"{suffixes.get(type)}{number}"

    check = supabase.table("cards").insert({
        "number": number,
        "name": name,
        "type": type,
        "owner": owner_id,
        "balance": balance
    }).execute()

    if not check.data:
        return [full_number, False]

    cardCreateLog(banker, full_number, owner_id)
    await card_generate(full_number, nickname, color)
    
    return [full_number, True]



#! Продолжение создания карты - выкладывание ее в канале владельца
async def next_create_card(inter, member, full_number, card_type_rus, color, name):
    card_image = f"{full_number}.png"

    await inter.followup.send(content=f"Карта типа {card_type_rus} с номером {full_number} успешно создана!")
    await asyncio.sleep(2)

    card = nxc.File(f"card_gen/cards/{card_image}", filename=card_image)

    # Канал для загрузки изображений
    image_upload_channel = inter.guild.get_channel(image_saver_channel)

    # Отправляем картинку в канал загрузки
    temp_message = await image_upload_channel.send(content=f"{full_number}",file=card)
    
    # Получаем URL изображения
    image_url = temp_message.attachments[0].url if temp_message.attachments else None

    # Проверка загрузки изображения
    if not await verify_image_upload(inter, image_url):
        return

    # Создаём эмбеды с картинкой
    card_embed = emb_cards(color, full_number, card_type_rus, name)
    card_embed_image = emb_cards_image(color, image_url)  # Устанавливаем ссылку
    card_embed_user = emb_cards_users(inter.guild, color, member.display_name, members={})
    embeds = [card_embed, card_embed_image, card_embed_user]

    # Получаем канал для отправки карточек
    response = supabase.table("clients").select("channels").eq("dsc_id", member.id).execute()
    channels = list(map(int, response.data[0]["channels"].strip("[]").split(",")))
    cards_channel_id = channels[1]
    cards_channel = inter.guild.get_channel(cards_channel_id)

    view = CardSelectView()  # Используем уже готовый View
    
    # Отправляем финальное сообщение с картой
    message_card = await cards_channel.send(content=f"{member.mention}", embeds=embeds, view=view)

    # Сохраняем ID сообщения в БД
    card_numbers = full_number[4:]  # Оставляем только цифры из номера карты
    supabase.table("cards").update({"select_menu_id": message_card.id}).eq("number", card_numbers).execute()



#! Удаление карты
async def delete_card(channel_card_id, message_card_id, bot):
    channel = bot.get_channel(channel_card_id)
    message = await channel.fetch_message(message_card_id)
    await message.delete()
    return



#! Автоматическое удалие изображения
async def deleteCardImages(interval):
    while True:
        try:
            current_time = time.time()
            folder_path = "card_gen/cards"

            for filename in os.listdir(folder_path):
                file_path = os.path.join(folder_path, filename)

                # Проверяем, что это файл + время последнего изменения
                if os.path.isfile(file_path) and filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                    file_age = current_time - os.path.getmtime(file_path)  # Время в секундах

                    if file_age > 30:  # Файл старше 30 секунд
                        os.remove(file_path)
        except Exception as e:
            print(f"Ошибка при удалении файлов: {e}")

        await asyncio.sleep(interval)  # Асинхронная пауза



#! Получение параметров из бд для удаления карты
def get_card_info_demote(member_id):
    response = supabase.rpc("get_user_cards_demote", {"user_id": member_id}).execute()

    if response.data:
        result = response.data[0]
        return {
            "banker_balance": result["banker_balance"],                     # Баланс карты (первой из списка, должна быть одна)
            "banker_select_menu_id": result["banker_select_menu_id"],       # возвращает id сообщения банковской карты
            "banker_number": result["banker_number"],                       # возвращает номер банковской карты
            "banker_type": result["banker_type"],                           # возвращает тип банковской карты
            "non_banker_number": result["non_banker_number"],               # ищет 1 карту не банкирскую и дает ее номер
            "non_banker_type": result["non_banker_type"],                   # ищет 1 карту не банкирскую и дает ее тип
            "channels_user": result["channels_user"]                        # выдает значение channels пользователя
        }
    return None



#! Создать аккаунт
async def createAccount(guild, member):

    member_name = member.display_name
    member_id = member.id
        
    #*Работа с пользователями
    #Проверка является ли пользователь уже зарегестрированным пользователем
    response = supabase.table("clients").select("dsc_id").execute()
    clients_dsc_id_list = [item["dsc_id"] for item in response.data]

    if member_id not in clients_dsc_id_list:
        #? Создание категории-Банковского счёта
        #! Создаём категорию с доступом только для указанного пользователя
        category = await guild.create_category(member_name, overwrites={
            guild.default_role: nxc.PermissionOverwrite(view_channel=False),  # Запрещаем доступ всем
            member: nxc.PermissionOverwrite(view_channel=True, read_messages=True, read_message_history=True)  # Разрешаем только owner
        })
        #! Канал "Транзакции" - только чтение
        transactions_channel = await guild.create_text_channel("🧮ㆍТранзакции", category=category, overwrites={
            guild.default_role: nxc.PermissionOverwrite(view_channel=False),
            member: nxc.PermissionOverwrite(view_channel=True, read_message_history=True, read_messages=True, send_messages=False)  # Только чтение
        })
        #! Канал "Карты" - только чтение
        cards_channel = await guild.create_text_channel("💳ㆍКарты", category=category, overwrites={
            guild.default_role: nxc.PermissionOverwrite(view_channel=False),
            member: nxc.PermissionOverwrite(view_channel=True, read_message_history=True, read_messages=True, send_messages=False)  # Только чтение
        })

        channels = [transactions_channel.id, cards_channel.id]

        #=Создание клиента
        prdx_id = get_user_id(member_id)

        supabase.table("clients").insert({
            "nickname": member_name,
            "dsc_id": member_id,
            "prdx_id": prdx_id,
            "account": category.id,
            "channels": channels
        }).execute()

        client_role_add = guild.get_role(client_role_id)
        await member.add_roles(client_role_add)

        #Аудит действия
        member_audit = guild.get_channel(bank_audit_channel)
        embed_aud_create_client = emb_aud_create_client(member_id)
        await member_audit.send(embed=embed_aud_create_client)      

        clientCreateLog(member_name)
    return



#! Удалить аккаунт
async def deleteAccount(guild, owner):
    owner_id = owner.id
    full_count = 0
    cards_info = []
    
    response_dsc_id = supabase.table("clients").select("dsc_id, account, channels").eq("dsc_id", owner_id).execute()

    if not response_dsc_id.data:
        return[False, full_count, "-"]

    if response_dsc_id.data:
        clients_category_id = int(response_dsc_id.data[0]["account"])
        clients_channels_ids = list(map(int, response_dsc_id.data[0]["channels"].strip("[]").split(",")))

        category = guild.get_channel(clients_category_id)
        if category:
            await category.delete()

        for channel_id in clients_channels_ids:
            channel = guild.get_channel(channel_id)
            if channel:
                await channel.delete()

        delete_account_request = supabase.rpc("delete_account", {"client_id": owner_id}).execute()
        for del_account in delete_account_request.data:
            type = del_account['type']
            number = del_account['number']
            count = del_account['balance']
            members = del_account["members"]
            del_card_full_number = f"{suffixes.get(type, type)}{number}"

            full_count += count

            # Добавляем информацию о карте в список
            cards_info.append(f"{del_card_full_number} - {count} алм.")


            for user_id, data in members.items():
                msg_id = data.get("id_message")
                channel_member_id = data.get("id_channel")
                channel_member = guild.get_channel(channel_member_id)
                message_member = await channel_member.fetch_message(msg_id)
                await message_member.delete()

            await del_img_in_channel(guild, del_card_full_number)

        if guild.get_member(owner.id):
            client_role_remove = guild.get_role(client_role_id)
            await owner.remove_roles(client_role_remove)

        clientDeleteLog(owner.display_name)
        cards_output = "\n".join(cards_info) if cards_info else "-"

        if full_count > 0:
            supabase.rpc("add_balance", {"card_number": "00000", "amount": full_count}).execute()

            ceo_message_text = f"**Удаление аккаута**\n💳 Общее пополнение с удаленных карт `{full_count}`\n📤 Подробности:\n📤 {cards_output}"
            ceo_owner_transaction_channel = guild.get_channel(bank_card_transaction)
            await ceo_owner_transaction_channel.send(ceo_message_text)


        request_cards_member = supabase.rpc("find_user_in_members", {"user_id": owner_id}).execute()

        # Обновить все карты где клиент был добавлен как пользователь, удаляя его.
        for request_card_member in request_cards_member.data:
            members_users = request_card_member['members']
            client_data = request_card_member.get("clients")
            owner_name = client_data["nickname"]
            channels_list = list(map(int, client_data["channels"].strip("[]").split(",")))
            channel_owner = guild.get_channel(channels_list[1])
            messege_owner_id = request_card_member['select_menu_id']
            if not isinstance(members, dict):  # Проверяем, если это не словарь (jsonb)
                members_users = {}

            if request_card_member:
                members_users.pop(str(owner_id), None)
                message_owner = await channel_owner.fetch_message(messege_owner_id)

                # Обновляем карту
                existing_embeds = message_owner.embeds
                color = existing_embeds[1].color
                card_embed_user = emb_cards_users(channel_owner.guild, color, owner_name, members_users)
                await message_owner.edit(embeds=[existing_embeds[0], existing_embeds[1], card_embed_user], attachments=[])

                # Обновляем сообщения всех пользователей
                for user_id, data in members_users.items():
                    msg_id = data.get("id_message")
                    channel_id = data.get("id_channel")
                    channel = guild.get_channel(channel_id)
                    message_users = await channel.fetch_message(msg_id)
                    await message_users.edit(embeds=[existing_embeds[0], existing_embeds[1], card_embed_user], attachments=[])

                # Обновляем данные в базе данных
                supabase.table("cards").update({"members": members_users}).eq("select_menu_id", messege_owner_id).execute()

        #Аудит действия
        member_audit = guild.get_channel(bank_audit_channel)
        embed_aud_create_client = emb_aud_create_client(banker_id, member_id, invoice_count)
        await member_audit.send(embed=embed_aud_create_client)

        return[True, full_count, cards_output]
    


#! Удалить старую картинку
async def del_img_in_channel(client, full_number):
    channel = client.get_channel(image_saver_channel)
    async for message in channel.history(limit=None):
        if full_number in message.content:
            await message.delete()
    return



#! Проверяет сколько времени аккаунт недействительный и при превышении лимита удаляет его.
async def scheduled_task(bot):
    check_status_clients = supabase.table("clients").select("dsc_id, freeze_date").eq("status", "freeze").execute()

    for client in check_status_clients.data:
        freeze_date = client["freeze_date"]
        member_id = client["dsc_id"]

        if freeze_date is None:
            return

        freeze_date = datetime.strptime(freeze_date, "%Y-%m-%d") # Преобразуем строку в дату (если в БД хранится строка формата YYYY-MM-DD)

        # Проверяем, прошло ли 30 день
        if datetime.now() - freeze_date >= timedelta(days=days_freeze_delete):
            guild = bot.get_guild(server_id[0])
            member = await bot.fetch_user(member_id)
            check_delete_acc = await deleteAccount(guild, member)

            if check_delete_acc[0] == True:
                print(f"Клиент {member.name} удален за незаход 30 день его discord_id - {client['dsc_id']}, карта банка пополнена на {check_delete_acc[1]}")  

                #Аудит действия
                on_audit = guild.get_channel(bank_audit_channel)
                embed_aud_autoDeleteAccount = emb_aud_autoDeleteAccount(member_id)
                await on_audit.send(embed=embed_aud_autoDeleteAccount)



#! Тоже самое что сверху
async def scheduler(bot):
    """Основной цикл, проверяющий текущее время"""
    while True:
        now = datetime.now()  # Получаем локальное время
        if now.hour in TARGET_HOURS and now.minute == 0:
            await scheduled_task(bot)
            await asyncio.sleep(180)
                
        await asyncio.sleep(40)
