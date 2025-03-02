import nextcord as nxc
from nextcord.ext import commands
from const import *
from modules import *
from db import *

command = "/Пополнить-казну"

class ReplenishBank(commands.Cog):
    def __init__(self, client):
        self.client = client
        
    @nxc.slash_command(guild_ids=server_id, name="пополнить-казну", description="пополнить баланс карты", default_member_permissions=nxc.Permissions(administrator=True))
    async def replenishBank(
        self, 
        inter: nxc.Interaction, 
        count: int = nxc.SlashOption(name="сумма", description="Сумма взноса", min_value=2, max_value=1000000), 
        description: str = nxc.SlashOption(name="комментарий", description="комментарий банкира", max_length=50)
    ):
        
        oneLog(f"{inter.user.display_name} написал команду {command}")        

        admin = inter.user
        admin_id = inter.user.id

        # Проверка прав staff
        if not await verify_staff(inter, admin, command):
            return

        db_rpc("add_balance", {"card_number": "00000", "amount": count}).execute()
        full_number = "CEO-00000"

        embed_comp_replenishbank = emb_comp_replenish_bank(full_number, count, description, admin_id)
        await inter.send(embed=embed_comp_replenishbank, ephemeral=True)

        # Отправка сообщений в каналы транзакций
        embed_replenish_ceo = emb_replenish_bank_ceo(full_number, count, description, admin_id)
        ceo_owner_card_channel = inter.client.get_channel(ceo_card_channel)
        ceo_owner_transaction_channel = ceo_owner_card_channel.get_thread(ceo_transaction_channel)
        await ceo_owner_transaction_channel.send(embed=embed_replenish_ceo)

        #Аудит действия
        member_audit = inter.guild.get_channel(bank_audit_channel)
        embed_aud_replenishMoney = emb_aud_replenishBank(count, description, admin_id)
        await member_audit.send(embed=embed_aud_replenishMoney)

        banker_audit = inter.guild.get_channel(banker_invoice_channel_id)
        embed_banker_aud = emb_banker_chat_replenish_bank(count, description, admin_id)
        await banker_audit.send(embed=embed_banker_aud)

        oneLog(f"{command} написанная {inter.user.display_name} успешно выполнена")


def setup(client):
    client.add_cog(ReplenishBank(client))