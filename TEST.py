import nextcord
from nextcord.ext import commands

TOKEN = "MTA5NTM4OTQ0MjQ4MDU0NTgzMg.GPuXvp.RCjFCn3vhb4JcHEjWFOOX1oP_n4ksNvxA4-Y38"
GUILD_ID = 1338868051222859779
CHANNEL_ID = 1338879396248817795

intents = nextcord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"{bot.user} запущен!")
    guild = bot.get_guild(GUILD_ID)
    channel = guild.get_channel(CHANNEL_ID)
    if channel:
        # Создаем эмбед с картинкой
        embed = nextcord.Embed(
            title="📜 Пользовательское соглашение Eclipse Bank",
            description=(
                "Добро пожаловать в **Eclipse Bank** — банковскую систему Discord-сервера Eclipse Bank, "
                "созданную для игроков Minecraft-сервера **prdx.so**! 🏦\n\n"
                "Используя сервис, вы соглашаетесь с условиями ниже. Ознакомьтесь с ними перед началом использования.\n"
                "⠀"
                "\n\n[📜 Прочитать соглашение](https://opposite-mercury-c77.notion.site/Eclipse-Bank-1aac2c58b3a180e5876dc512bfece9d8)"
            ),
            color=0x3498db
        )
        embed.set_image(url="https://media.discordapp.net/attachments/1322331058255040624/1345787176259944579/Group_1123457176259944579.png?ex=67c5d17a&is=67c47ffa&hm=3ef156eff5fb2dafe7f42e885abbb5650a9cca70ca917eb409459f6a0f292b13&=&format=webp&quality=lossless&width=1811&height=543")

        # Отправляем эмбед с гиперссылкой
        await channel.send(embed=embed)
    else:
        print("Канал не найден!")

bot.run(TOKEN)
