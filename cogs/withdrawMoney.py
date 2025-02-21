import nextcord as nxc
from nextcord.ext import commands
from const import *
from modules import *

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

        await inter.response.defer(ephemeral=True)

        nick_table = supabase.table("clients").select("channels").eq("nickname", member_nick).execute()
        if not nick_table.data:
            await inter.send(f"Ошибка: клиент {member.mention} не найден, проверьте является ли он клиентом.", ephemeral=True)
            return
        
        nick_transaction_channel_id = list(map(int, nick_table.data[0]["channels"].strip("[]").split(",")))[0]

        await inter.send(
            f"✅ **Успешно выставили счёт на снятие!**\n📤 Кому `{member.mention}`\n💰 Сумма `{count} алм.`\n📝 Комментарий: `{description or '—'}`",
            ephemeral=True
        )

        # Отправка сообщений в каналы транзакций
        nick_message_text = f"**Запрос на снятие наличных**\n💳 От банкира`{banker.mention}`\n📤 Кому `{member_nick}`\n💰 Сумма `{count} алм.`\n📝 Комментарий: `{description or '—'}`"
        nick_transaction_channel = inter.client.get_channel(nick_transaction_channel_id)
        view_member=MyInvoiceView() # Кнопочки
        nick_message = await nick_transaction_channel.send(nick_message_text, view = view_member)

        banker_invoice_channel = inter.client.get_channel(banker_invoice_channel_id)
        view_banker=BankerInvoiceView() # Кнопочки
        banker_message = await banker_invoice_channel.send(nick_message_text, view = view_banker)

        supabase.table("invoice").insert({
            "own_dsc_id":banker_id,
            "own_number":"00000",
            "memb_dsc_id":member_id,
            "memb_message_id":nick_message.id,
            "memb_channel_id":nick_transaction_channel_id,
            "banker_message_id": banker_message.id,
            "count":count,
            "type":"banker"
        }).execute()

def setup(client):
    client.add_cog(WithdrawMoney(client))