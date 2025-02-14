import nextcord as nxc
from nextcord.ext import commands
from const import *
from modules import *
import asyncio

command = "/admCreate"

class AdmCreate(commands.Cog):
    def __init__(self, client):
        self.client = client
        
    @nxc.slash_command(guild_ids=server_id, name="admcreate", description="Admin Unit Creation")
    async def admcreate(
        self, inter: nxc.Interaction, 
        member: nxc.Member, 
        number: int, 
        name: str, 
        type: str = nxc.SlashOption(name="card_type", description="Choose 1", required=True, choices=admCardTypes), 
        color: str= nxc.SlashOption(name="card_color", description="Choose 1", required=True, choices=choice_color)
    ):
        # Вспомогательные параметры
        admin = inter.user
        admin_id = inter.user.id
        admin_nickname = inter.user.display_name
        member_id = member.id       
        member_nickname = member.display_name

        card_type_rus = type_translate.get(type, type)

        # Проверка прав staff
        if not await verify_staff(inter, admin, command):
            return
        
        # Проверка находится ли человек на сервере
        if not await verify_user_in_server(inter, member):
            return

        # Проверка написания числа
        if not await verify_number_lenght(inter, number):
            return
        number = f"{number:05}"

        # Проверка занятости номера карты
        if not await verify_num_is_claimed(inter, number):
            return


#// Действие

        await inter.response.defer(ephemeral=True)

        #=Создание клиента
        await createAccount(inter.guild, member)

        # Проверка на исчерпание лимита создания карт
        if not check_count_cards(member_id):
            status="MaxCountCard"
            embed = user_cardLimit()
            await inter.send(embed=embed, ephemeral=True)
            PermsLog(admin_nickname, admin_id, command, status)
            return 

        #=Создание карты
        check_create_card = create_card(admin_nickname, name, member_nickname, type, member_id, color, False, number, "0")
        # Проверка получилось ли создать карту
        if not check_create_card[1]:
            embed = sb_cardNotCreated()
            await inter.followup.send(embed=embed, ephemeral=True)
            return
        full_number = check_create_card[0]
        card_image = f"{full_number}.png"
        await inter.followup.send(content=f"Карта типа {card_type_rus} с номером {full_number} успешно создана!")
        await asyncio.sleep(2)

        card = nxc.File(f"card_gen/cards/{card_image}", filename=card_image)
        if type == "💎 CEO": color = "💎 CEO"
        card_embed = e_cards(color,full_number,card_type_rus,name,card_image)

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

        status="Success"
        PermsLog(admin_nickname, admin_id, command, status)


def setup(client):
    client.add_cog(AdmCreate(client))