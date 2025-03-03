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
from db import *


#! Создать карту и записать в бд
async def create_card(banker, name, nickname, type, owner_id, color, do_random: bool, adm_number, balance):

    # Извлекаем номера уже существующих карт и добавляем в список
    response = db_cursor("cards").select("number").execute()
    numbers_list = [item["number"] for item in response.data]
    if do_random == True:
        while True:
            short_number = int(''.join(random.choices(n, k=5)))
            if short_number <=20:
                break
            number =  f"{short_number:05}"
            if number not in numbers_list:
                break
    else:
        number = adm_number
    
    full_number = f"{suffixes.get(type)}{number}"

    check = db_cursor("cards").insert({
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
    response = db_cursor("clients").select("account").eq("dsc_id", member.id).execute()
    cards_channel_id = response.data[0]["account"]
    cards_channel = inter.guild.get_channel(cards_channel_id)

    view = CardSelectView()  # Используем уже готовый View
    
    # Отправляем финальное сообщение с картой
    message_card = await cards_channel.send(content=f"{member.mention}", embeds=embeds, view=view)

    # Сохраняем ID сообщения в БД
    card_numbers = full_number[4:]  # Оставляем только цифры из номера карты
    db_cursor("cards").update({"select_menu_id": message_card.id}).eq("number", card_numbers).execute()



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
            oneLog(f"Ошибка при удалении файлов: {e}")

        await asyncio.sleep(interval)  # Асинхронная пауза



#! Получение параметров из бд для удаления карты
def get_card_info_demote(member_id):
    response = db_rpc("get_user_cards_demote", {"user_id": member_id}).execute()

    if response.data:
        result = response.data[0]
        return {
            "banker_balance": result["banker_balance"],                     # Баланс карты (первой из списка, должна быть одна)
            "banker_select_menu_id": result["banker_select_menu_id"],       # возвращает id сообщения банковской карты
            "banker_number": result["banker_number"],                       # возвращает номер банковской карты
            "banker_type": result["banker_type"],                           # возвращает тип банковской карты
            "non_banker_number": result["non_banker_number"],               # ищет 1 карту не банкирскую и дает ее номер
            "non_banker_type": result["non_banker_type"],                   # ищет 1 карту не банкирскую и дает ее тип
            "account_id": result["account_user"],                           # выдает значение account пользователя
            "transactions_id": result["transactions_user"],                 # выдает значение transactions пользователя     
            "count_cards": result["count_cards_user"]                       # выдает значения карт пользователя         
        }
    return None



#! Создать аккаунт
async def createAccount(guild, member, banker_id):

    member_name = member.display_name
    member_id = member.id
        
    #*Работа с пользователями
    #Проверка является ли пользователь уже зарегестрированным пользователем
    response = db_cursor("clients").select("dsc_id").execute()
    clients_dsc_id_list = [item["dsc_id"] for item in response.data]


    if member_id not in clients_dsc_id_list:
        #? Создание банковского счёта
        #! Получаем категорию и роль клиента 
        category = nxc.utils.get(guild.categories, id=cleints_category)
        client_role = guild.get_role(client_role_id)

        #! Канал "Карты" - только чтение
        cards_channel = await guild.create_text_channel(f"💳ㆍ{member_name}", category=category, overwrites={
            guild.default_role: nxc.PermissionOverwrite(view_channel=False),
            client_role: nxc.PermissionOverwrite(view_channel=False),  # Запрещаем доступ для client_role
            member: nxc.PermissionOverwrite(view_channel=True, read_message_history=True, read_messages=True, send_messages=False, send_messages_in_threads=False)
        })
        #! Ветка "Транзакции" - только чтение
        transaction_msg = await cards_channel.send("🧮 Все транзакции клиента")
        thread = await cards_channel.create_thread(name="🧮ㆍТранзакции", type=nxc.ChannelType.public_thread,
            message=transaction_msg,
            auto_archive_duration=10080  # Автоархивация на 7 дней (10080 минут)
        )

        #=Создание клиента
        prdx_id = get_user_id(member_id)

        db_cursor("clients").insert({
            "nickname": member_name,
            "dsc_id": member_id,
            "prdx_id": prdx_id,
            "account": cards_channel.id,
            "transactions": thread.id
        }).execute()

        client_role_add = guild.get_role(client_role_id)
        await member.add_roles(client_role_add)

        #Аудит действия
        member_audit = guild.get_channel(bank_audit_channel)

        title_emb, message_emb, color_emb = get_message_with_title(
            67, (), (member_id, banker_id))
        embed_aud_create_client = emb_auto(title_emb, message_emb, color_emb)        
        await member_audit.send(embed=embed_aud_create_client)      

        clientCreateLog(member_name)
        return True
    return False



#! Удалить аккаунт
async def deleteAccount(guild, owner):
    owner_id = owner.id
    full_count = 0
    cards_info = []
    
    response_dsc_id = db_cursor("clients").select("dsc_id, account").eq("dsc_id", owner_id).execute()

    if not response_dsc_id.data:
        return[False, full_count, "-"]

    if response_dsc_id.data:
        clients_channel_id = response_dsc_id.data[0]["account"]

        # Удаление канала клиента
        channel = guild.get_channel(clients_channel_id)
        if channel:
            await channel.delete()

        delete_account_request = db_rpc("delete_account", {"client_id": owner_id}).execute()
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
            db_rpc("add_balance", {"card_number": "00000", "amount": full_count}).execute()

            title_emb, message_emb, color_emb = get_message_with_title(
                81, (), ())
            embed_del = emb_auto(title_emb, message_emb, color_emb)

            ceo_owner_card_channel = guild.get_channel(ceo_card_channel)
            ceo_owner_transaction_channel = ceo_owner_card_channel.thread(ceo_transaction_channel)
            await ceo_owner_transaction_channel.send(embed=embed_del)


        request_cards_member = db_rpc("find_user_in_members", {"user_id": owner_id}).execute()

        # Обновить все карты где клиент был добавлен как пользователь, удаляя его.
        for request_card_member in request_cards_member.data:
            members_users = request_card_member['members']
            owner_name = request_card_member["nickname"]
            channel_owner = request_card_member["account"]
            messege_owner_id = request_card_member['select_menu_id']
            if not isinstance(members_users, dict):  # Проверяем, если это не словарь (jsonb)
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
                db_cursor("cards").update({"members": members_users}).eq("select_menu_id", messege_owner_id).execute()

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
    check_status_clients = db_cursor("clients").select("dsc_id, freeze_date").eq("status", "freeze").execute()

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
                oneLog(f"Клиент {member.name} удален за незаход 30 день его discord_id - {client['dsc_id']}, карта банка пополнена на {check_delete_acc[1]}")  

                #Аудит действия
                on_audit = guild.get_channel(bank_audit_channel)

                title_emb, message_emb, color_emb = get_message_with_title(
                    59, (), (member_id, days_freeze_delete))
                embed_aud_autoDeleteAccount = emb_auto(title_emb, message_emb, color_emb)     
                await on_audit.send(embed=embed_aud_autoDeleteAccount)


#! Закрытие и открытие веток автоматическое по истечению активности 3 дней.
async def check_and_refresh_threads(bot):
    """Проверяет активность веток и обновляет их, если прошло более 3 дней."""
    guild = bot.get_guild(server_id[0])

    for channel in guild.text_channels:
        # Получаем все активные ветки в канале
        threads = channel.threads
        for thread in threads:
            try:
                # Получаем время последнего сообщения в ветке
                last_message = None
                async for message in thread.history(limit=1):  # Используем async for
                    last_message = message
                    break

                if last_message:
                    last_activity = last_message.created_at
                else:
                    last_activity = thread.created_at

                # Проверяем, прошло ли 3 дня с последней активности
                if datetime.now(last_activity.tzinfo) - last_activity >= timedelta(days=3):

                    # Закрываем и открываем ветку
                    await thread.edit(archived=True)
                    await thread.edit(archived=False)
                    oneLog(f"Таймер ветки {thread.id} обновлен.")
                    await asyncio.sleep(2)

            except nxc.HTTPException as e:
                oneLog(f"Ошибка при обработке ветки {thread.id}: {e}")


#! Сохранение бд!
async def backup_database():
    """Создает резервную копию базы данных с указанием даты и времени."""
    if not os.path.exists(BACKUP_FOLDER):
        os.makedirs(BACKUP_FOLDER)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    backup_filename = f"{BACKUP_FOLDER}/backup_{timestamp}.sql"

    env = os.environ.copy()
    env["PGPASSWORD"] = DB_PASSWORD

    try:
        command = f"pg_dump -h {DB_HOST} -p {DB_PORT} -U {DB_USER} -d {DB_NAME} -F c -f {backup_filename}"
        os.system(command)
        oneLog(f"Резервная копия базы данных сохранена: {backup_filename}")
    except Exception as e:
        oneLog(f"Ошибка при создании резервной копии БД: {e}")


#! Тоже самое что сверху
async def scheduler(bot):
    """Основной цикл, проверяющий текущее время"""
    while True:
        now = datetime.now()  # Получаем локальное время
        if now.hour in TARGET_HOURS and now.minute == 0:
            await backup_database()
            await scheduled_task(bot)
            await check_and_refresh_threads(bot)
            await asyncio.sleep(180)
                
        await asyncio.sleep(40)