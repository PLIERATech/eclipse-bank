import nextcord as nxc
from nextcord.ext import commands
from const import *
from modules import *

command = "/Поиск-карт"

class SearchCards(commands.Cog):
    def __init__(self, client):
        self.client = client
        
    @nxc.slash_command(guild_ids=server_id, name="поиск-карт", description="Поиск всех карт клиента", default_member_permissions=nxc.Permissions(administrator=True))
    async def searchCards(
        self, 
        inter: nxc.Interaction, 
        member: nxc.Member
    ):
        admin = inter.user
        admin_nick = inter.user.display_name
        admin_id = inter.user.id
        member_nick = member.display_name
        member_id = member.id

        # Проверка прав staff
        if not await verify_staff(inter, admin, command):
            return

        # Проверка находится ли человек на сервере
        if not await verify_user_in_server(inter, member):
            return
        
        # Проверка является ли человек клиентом
        if not await verify_user_is_client(inter, member):
            return
        
        await inter.response.defer(ephemeral=True)

        search_cards_response = supabase.rpc("find_all_cards_user", {"user_id": member_id}).execute()

        if not search_cards_response.data:
            embed_no_cards_search = emb_no_cards_search(member_id, ephemeral=True)
            await inter.send(embed=embed_no_cards_search, )
        else:
            cards = []

            for search_card in search_cards_response.data:
                search_card_type = search_card["user_type"]
                card_balance = search_card["balance"]
                card_type = search_card["type"]
                card_number = search_card["number"]
                full_number = f"{suffixes.get(card_type, card_type)}{card_number}"


                if search_card_type == 'owner':
                    display_type = "Владелец"
                elif search_card_type == 'user':
                    display_type = "Пользователь"

                # Добавляем в список в виде кортежа (тип карты, баланс, строка для вывода)
                cards.append((search_card_type, card_balance, f"{len(cards)}. ({display_type}) {full_number} - {card_balance} алм"))

            # Сортируем: сначала owner, потом user, баланс по убыванию
            cards.sort(key=lambda x: (x[0] != "owner", -x[1]))
            embed_comp_search_cards = emb_comp_search_cards(member_id, cards)
            await inter.send(embed=embed_comp_search_cards, ephemeral=True)    



def setup(client):
    client.add_cog(SearchCards(client))