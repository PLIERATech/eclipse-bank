import nextcord as nxc
from nextcord.ext import commands
from const import *
from modules import *

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
            supabase.table("clients").update({"count_cards": 2}).eq("dsc_id", member_id).execute()

        # Использование:
        get_card_info = get_card_info_demote(member_id)
        channels_response = get_card_info["channels_user"]
        channels = list(map(int, channels_response.strip("[]").split(",")))
        channel_card_id = channels[1]
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
                embed = emb_demotedBanker(card_type_rus, full_number)
                await inter.followup.send(embed=embed, ephemeral=True)
            else:
                await delete_card(channel_card_id, int(get_card_info["banker_select_menu_id"]), inter.client)

                supabase.table("cards").update({"balance": int(get_card_info['banker_balance'])}).eq("number", get_card_info["non_banker_number"]).execute()
                embed = emb_demoteBankerWithCar()
                await inter.followup.send(embed=embed, ephemeral=True)
        else:
            await delete_card(channel_card_id, int(get_card_info["banker_select_menu_id"]), inter.client)
            embed = emb_demoteBankerWithCar()
            await inter.followup.send(embed=embed, ephemeral=True)
        
        # Снятие роли
        banker_role_remove = inter.guild.get_role(banker_role_id)
        await member.remove_roles(banker_role_remove)

        kick_team(member_id)


def setup(client):
    client.add_cog(Demote(client))