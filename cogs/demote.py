import nextcord as nxc
from nextcord.ext import commands
from const import *
from modules import *
from db import *

command = "/разжаловать"

ignore_members = [436507782263603200]
# ignore_members = [436507782263603200, 187208294161448960]

class Demote(commands.Cog):
    def __init__(self, client):
        self.client = client
        
    @nxc.slash_command(guild_ids=server_id, name="разжаловать", description="разжаловать банкира")
    async def demote(
        self, 
        inter: nxc.Interaction, 
        member: nxc.Member
    ):

        oneLog(f"{inter.user.display_name} написал команду {command}")

        admin = inter.user
        admin_id = inter.user.id
        admin_nick = inter.user.display_name
        member_nick = member.display_name
        member_id = member.id
        
        # Проверка прав staff
        if not await verify_staff(inter, admin, command):
            return
        
        # Проверка находится ли человек на сервере
        if not await verify_user_in_server(inter, member):
            return

        # Проверка является ли пользователь банкиром
        if not await verify_this_banker(inter, command, member, False):
            return

        await inter.response.defer(ephemeral=True)

        if not member_id in ignore_members:
            db_cursor("clients").update({"count_cards": 3}).eq("dsc_id", member_id).execute()

        # Использование:
        get_card_info = get_card_info_demote(member_id)
        channel_card_id =  get_card_info["account_id"]
        banker_card_number = get_card_info['banker_number']
        banker_card_type = get_card_info['banker_type']
        banker_card_full_number = f"{suffixes.get(banker_card_type, banker_card_type)}{banker_card_number}"

        if get_card_info['banker_balance'] != 0: # если есть баланс
            if get_card_info['non_banker_number'] is None: # если нет обычной карты
                #=Создание карты если нет и есть деньги
                card_type="👤 Personal"
                card_type_rus = type_translate.get(card_type, card_type)
                color = choice_color[5]
                check_create_card = await create_card(admin_nick, member_nick, member_nick, card_type, member_id, color, True, "0", int(get_card_info['banker_balance']))
                # Проверка получилось ли создать карту
                if not await verify_create_card(inter, check_create_card[1]):
                    return
                
                full_number = check_create_card[0]
                await next_create_card(inter, member, full_number, card_type_rus, color, member_nick)
                await delete_card(channel_card_id, int(get_card_info["banker_select_menu_id"]), inter.client)
                title_emb, message_emb, color_emb = get_message_with_title(
                    5, (), (card_type_rus, full_number))
                embed = emb_auto(title_emb, message_emb, color_emb)

                title_emb, message_emb, color_emb = get_message_with_title(
                    55, (), (member_id, full_number, int(get_card_info['banker_balance']), admin_id))
                embed_aud_admitBanker = emb_auto(title_emb, message_emb, color_emb)
            else:
                await delete_card(channel_card_id, int(get_card_info["banker_select_menu_id"]), inter.client)
                member_type = get_card_info["non_banker_type"]
                member_number = get_card_info["non_banker_number"]
                member_full_number = f"{suffixes.get(member_type, member_type)}{member_number}"
                db_rpc("add_balance", {"card_number": member_number, "amount": int(get_card_info['banker_balance'])}).execute()
                title_emb, message_emb, color_emb = get_message_with_title(
                    6, (), ())
                embed = emb_auto(title_emb, message_emb, color_emb)

                title_emb, message_emb, color_emb = get_message_with_title(
                    56, (), (member_id, int(get_card_info['banker_balance']), member_full_number, admin_id))
                embed_aud_admitBanker = emb_auto(title_emb, message_emb, color_emb)
        else:
            await delete_card(channel_card_id, int(get_card_info["banker_select_menu_id"]), inter.client)
            title_emb, message_emb, color_emb = get_message_with_title(
                6, (), ())
            embed = emb_auto(title_emb, message_emb, color_emb)
            
            title_emb, message_emb, color_emb = get_message_with_title(
                57, (), (member_id, admin_id))
            embed_aud_admitBanker = emb_auto(title_emb, message_emb, color_emb)
        
        # Снятие роли
        banker_role_remove = inter.guild.get_role(banker_role_id)
        await member.remove_roles(banker_role_remove)

        kick_team(member_id)

        await inter.followup.send(embed=embed, ephemeral=True)
        #Аудит действия
        member_audit = inter.guild.get_channel(bank_audit_channel)
        await member_audit.send(embed=embed_aud_admitBanker)       

        oneLog(f"{command} написанная {inter.user.display_name} успешно выполнена")


def setup(client):
    client.add_cog(Demote(client))