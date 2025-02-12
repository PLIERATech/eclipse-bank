import nextcord as nxc
from nextcord.ext import commands
from const import *
from log_functions import *
from .services import *
from .api import *
import json


async def createAccount(guild, owner):

    card_name = owner.display_name
    owner_id = owner.id
        
    #*Работа с пользователями
    #Проверка является ли пользователь уже зарегестрированным пользователем
    response = supabase.table("clients").select("dsc_id").execute()
    clients_dsc_id_list = [item["dsc_id"] for item in response.data]
    if owner_id not in clients_dsc_id_list:
        #? Создание категории-Банковского счёта
        #! Создаём категорию с доступом только для указанного пользователя
        category = await guild.create_category(card_name, overwrites={
            guild.default_role: nxc.PermissionOverwrite(view_channel=False),  # Запрещаем доступ всем
            owner: nxc.PermissionOverwrite(view_channel=True, read_messages=True, read_message_history=True)  # Разрешаем только owner
        })
        #! Канал "Команды" - можно отправлять сообщения и использовать слэш-команды
        commands_channel = await guild.create_text_channel("📇ㆍКоманды", category=category, overwrites={
            guild.default_role: nxc.PermissionOverwrite(view_channel=False),  # Запрещён доступ всем
            owner: nxc.PermissionOverwrite(
                view_channel=True, send_messages=True, read_message_history=True, use_slash_commands=True)  # Разрешены сообщения и слэш-команды
        })
        #! Канал "Транзакции" - только чтение
        transactions_channel = await guild.create_text_channel("💊ㆍТранзакции", category=category, overwrites={
            guild.default_role: nxc.PermissionOverwrite(view_channel=False),
            owner: nxc.PermissionOverwrite(view_channel=True, read_message_history=True, read_messages=True, send_messages=False)  # Только чтение
        })
        #! Канал "Карты" - только чтение
        cards_channel = await guild.create_text_channel("💳ㆍКарты", category=category, overwrites={
            guild.default_role: nxc.PermissionOverwrite(view_channel=False),
            owner: nxc.PermissionOverwrite(view_channel=True, read_message_history=True, read_messages=True, send_messages=False)  # Только чтение
        })

        channels = [commands_channel.id, transactions_channel.id, cards_channel.id]

        #=Создание клиента
        create_client(card_name, owner_id, category.id, channels)
    return

async def deleteAccount(guild, owner):
    owner_id = owner.id

    response_dsc_id = supabase.table("clients").select("dsc_id").execute()
    clients_dsc_id_list = [item["dsc_id"] for item in response_dsc_id.data]

    if owner_id in clients_dsc_id_list:
        response_account = supabase.table("clients").select("account").eq("dsc_id", owner_id).execute()
        response_channels = supabase.table("clients").select("channels").eq("dsc_id", owner_id).execute()
        clients_category_id = int(response_account.data[0]["account"])
        clients_channels_ids = list(map(int, response_channels.data[0]["channels"].strip("[]").split(",")))

        category = guild.get_channel(clients_category_id)
        if category:
            await category.delete()

        for channel_id in clients_channels_ids:
            channel = guild.get_channel(channel_id)
            if channel:
                await channel.delete()

        supabase.table('clients').delete().eq('dsc_id', owner_id).execute()
        supabase.table('cards').delete().eq('owner', owner_id).execute()

        clientDeleteLog(owner.display_name)
