import nextcord as nxc
from nextcord.ext import commands
from const import *
from modules import *

command = "/разжаловать"
type = "banker"

ignore_members = [436507782263603200]
# ignore_members = [436507782263603200, 187208294161448960]

class Demote(commands.Cog):
    def __init__(self, client):
        self.client = client
        
    @nxc.slash_command(guild_ids=server_id, name="разжаловать", description="разжаловать банкира")
    async def demote(self, inter: nxc.Interaction, member: nxc.Member):

        admin_id = inter.user.id
        admin_nick = inter.user.display_name
        member_nick = member.display_name
        member_id = member.id
        guild = inter.guild
        
        #Проверка прав staff
        if not any(role.id in (staff_role) for role in inter.user.roles):
            status="No Permissions"
            await inter.response.send_message("❗ У вас недостаточно прав для использования данной команды.", ephemeral=True)
            PermsLog(admin_nick, admin_id, command, status)
            return
        
        #Проверка является ли пользователь банкиром
        if not any(role.id in (banker_role) for role in member.roles):
            status="isntBanker"
            await inter.response.send_message("❗ Данный пользователь не является банкиром.", ephemeral=True)
            PermsLog(admin_nick, admin_id, command, status)
            return

        await inter.response.defer(ephemeral=True)

        if not member_id in ignore_members:
            supabase.table("clients").update({"count_cards": 2}).eq("dsc_id", member_id).execute()

        # Использование:
        get_card_info = get_card_info_demote(member_id)
        channels_response = get_card_info["channels_user"]
        channels = list(map(int, channels_response.strip("[]").split(",")))
        channel_card_id = channels[1]
        if int(get_card_info['banker_balance']) > 0:
            if get_card_info['non_banker_number'] == None:
                #=Создание карты если нет и есть деньги
                card_type="personal"
                full_number = create_card(admin_nick, member_nick, member_nick, card_type, member_id, color="green", do_random=True, adm_number="0", balance=get_card_info['banker_balance'])
                card_type_rus = "Личная"
                card_image = f"{full_number}.png"

                #Удаление банковской карты
                await delete_card(channel_card_id, int(get_card_info["banker_select_menu_id"]), inter.client)
                
                #Продолжение создания банковской карты
                await asyncio.sleep(2)
                card = nxc.File(f"card_gen/cards/{card_image}", filename=card_image)

                card_embed = nxc.Embed(color=nxc.Colour.from_rgb(146, 182, 79))
                card_embed.add_field(name="💳 Карта:", value=full_number, inline=True)
                card_embed.add_field(name="🗂️ Тип:", value=card_type_rus, inline=True)
                card_embed.add_field(name="💬 Название", value=member_nick, inline=True)
                card_embed.set_image(url=f"attachment://{card_image}")
                card_embed.set_footer(text="Eclipse Bank 2025")

                cards_channel = inter.guild.get_channel(channel_card_id)

                view = CardSelectView()  # Используем уже готовый View
                
                message_card = await cards_channel.send(content=f"{member.mention}", embed=card_embed, file=card, view=view)

                #Получаем только цифры созданной карты / Удаляем все символы, кроме цифр
                card_numbers = full_number.translate(str.maketrans("", "", "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-"))
                supabase.table("cards").update({"select_menu_id": message_card.id}).eq("number", card_numbers).execute()
                await inter.followup.send(content=f"Карта типа {card_type_rus} с номером {full_number} успешно создана!\n Карта банкира удалена\n Банкир разжалован")
            else:
                await delete_card(channel_card_id, int(get_card_info["banker_select_menu_id"]), inter.client)

                supabase.table("cards").update({"balance": int(get_card_info['banker_balance'])}).eq("number", get_card_info["non_banker_number"]).execute()
                await inter.followup.send(content=f"Карта банкира удалена\n Банкир разжалован")
        else:
            await delete_card(channel_card_id, int(get_card_info["banker_select_menu_id"]), inter.client)
            await inter.followup.send(content=f"Карта банкира удалена\n Банкир разжалован")
        
        #Снятие роли
        banker_role_remove = inter.guild.get_role(banker_role_id)
        await member.remove_roles(banker_role_remove)

        kick_team(member_id)


def setup(client):
    client.add_cog(Demote(client))