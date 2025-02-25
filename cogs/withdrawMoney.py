import nextcord as nxc
from nextcord.ext import commands
from const import *
from modules import *
from db import *

command = "/Обналичить"

class WithdrawMoney(commands.Cog):
    def __init__(self, client):
        self.client = client
        
    @nxc.slash_command(guild_ids=server_id, name="обналичить", description="Обналичить деньги с карты")
    async def withdrawMoney(
        self, 
        inter: nxc.Interaction, 
        member: nxc.Member, 
        count: int = nxc.SlashOption(name="сумма", description="Сумма обналичивания", min_value=1, max_value=1000000), 
        description: str = nxc.SlashOption(name="комментарий", description="комментарий банкира", max_length=50)
    ):
        banker = inter.user
        banker_nick = inter.user.display_name
        banker_id = inter.user.id
        member_id = member.id
        member_nick = member.display_name
        
        # Проверка прав banker
        if not await verify_this_banker(inter, command, inter.user, True):
            return

        # Проверка является ли пользователь клиентом
        if not await verify_user_is_client(inter, member):
            return

        await inter.response.defer(ephemeral=True)

        nick_table = db_cursor("clients").select("channels").eq("nickname", member_nick).execute()
        
        nick_transaction_channel_id = list(map(int, nick_table.data[0]["channels"].strip("[]").split(",")))[0]

        embed_comp_withdram_invoice = emb_comp_withdram_invoice(member_id, count, description)    
        await inter.send(embed=embed_comp_withdram_invoice, ephemeral=True)

        # Отправка сообщений в каналы транзакций
        embed_withdram_request = emb_withdram_request(banker_id, member_id, count, description)
        nick_transaction_channel = inter.client.get_channel(nick_transaction_channel_id)
        view_member=MyInvoiceView() # Кнопочки
        nick_message = await nick_transaction_channel.send(embed=embed_withdram_request, view = view_member)

        banker_invoice_channel = inter.client.get_channel(banker_invoice_channel_id)
        view_banker=BankerInvoiceView() # Кнопочки
        banker_message = await banker_invoice_channel.send(embed=embed_withdram_request, view = view_banker)

        db_cursor("invoice").insert({
            "own_dsc_id":banker_id,
            "own_number":"00000",
            "memb_dsc_id":member_id,
            "memb_message_id":nick_message.id,
            "memb_channel_id":nick_transaction_channel_id,
            "banker_message_id": banker_message.id,
            "count":count,
            "type_type":"banker"
        }).execute()

        #Аудит действия
        member_audit = inter.guild.get_channel(bank_audit_channel)
        embed_aud_withdrawMoney = emb_aud_withdrawMoney(banker_id, member_id, count, description)
        await member_audit.send(embed=embed_aud_withdrawMoney)

def setup(client):
    client.add_cog(WithdrawMoney(client))