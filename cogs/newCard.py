import nextcord as nxc
from nextcord.ext import commands
from const import *
from modules import *
import asyncio

command = "/создать"

class NewCard(commands.Cog):
    def __init__(self, client):
        self.client = client
        
    @nxc.slash_command(guild_ids=server_id, name="создать", description="Создать карту Eclipse Bank")
    async def newCard(
        self, 
        inter: nxc.Interaction, 
        member: nxc.Member, 
        type: str = nxc.SlashOption(name="card_type", description="Choose 1", required=True, choices=bankerCardType), 
        color: str= nxc.SlashOption(name="card_color", description="Choose 1", required=True,choices=choice_color)
    ):
        banker_id = inter.user.id
        banker_name = inter.user.display_name
        nickname = inter.user.display_name
        card_name = member.display_name
        member_id = member.id
        guild = inter.guild

        # Проверка находится ли человек на сервере\
        if not await verify_user_in_server(inter, member):
            return

        #Проверка прав banker
        if not any(role.id in (banker_role) for role in inter.user.roles):
            status="No Permissions"
            embed = e_noPerms()
            await inter.response.send_message(embed=embed, ephemeral=True)
            PermsLog(nickname, banker_id, command, status) 
            return

#// Действие

        await inter.response.defer(ephemeral=True)

        #=Создание клиента
        await createAccount(guild, member)

        #Проверка на исчерпание лимита создания карт
        if not check_count_cards(member_id):
            status="MaxCountCard"
            await inter.send("У пользователя максимальное количество карт.", ephemeral=True)
            PermsLog(nickname, banker_id, command, status)
            return 

        status="Success"
        PermsLog(nickname, banker_id, command, status)

        #=Создание карты
        check_create_card = create_card(banker_name, card_name, card_name, type, member_id, color, True, "0", "0")
        if not check_create_card[1]:
            embed = sb_cardNotCreated()
            await inter.followup.send(embed=embed, ephemeral=True)
            return
        full_number = check_create_card[0]
        card_type_rus = type_translate.get(type, type)
        card_image = f"{full_number}.png"

        await inter.followup.send(content=f"Карта типа {card_type_rus} с номером {full_number} успешно создана!")
        await asyncio.sleep(2)

        card = nxc.File(f"card_gen/cards/{card_image}", filename=card_image)
        card_embed = e_cards(color,full_number,card_type_rus,card_name,card_image)

        response = supabase.table("clients").select("*").eq("dsc_id", member_id).execute()

        channels_response = response.data[0]["channels"]
        channels = list(map(int, channels_response.strip("[]").split(",")))
        cards_channel_id = int(channels[1])
        cards_channel = inter.guild.get_channel(cards_channel_id)

        view = CardSelectView()  # Используем уже готовый View
        
        message_card = await cards_channel.send(content=f"{member.mention}", embed=card_embed, file=card, view=view)

        #Получаем только цифры созданной карты / Удаляем все символы, кроме цифр
        card_numbers = full_number.translate(str.maketrans("", "", "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-"))
        supabase.table("cards").update({"select_menu_id": message_card.id}).eq("number", card_numbers).execute()


def setup(client):
    client.add_cog(NewCard(client))