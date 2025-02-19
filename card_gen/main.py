from PIL import Image, ImageDraw, ImageFont
from supabase import *
from .params import *

base_color = (240, 240, 240)
unique_color = (42, 42, 42)

nickname_position = (644, 515)
bcard_position = (534, 559)

nickname_font = ImageFont.truetype(font, 48)
bcard_font = ImageFont.truetype(font, 96)

async def card_generate(fullNumber, user_nickname, color):

    template = ""
    font_color = base_color

    if color == "⚪ White":
        font_color = unique_color

    template = color_templates.get(color)

    try:
        template.convert("RGBA")
    except FileNotFoundError:
        print("Ошибка: файл 'template.png' не найден в директории.")
        return

    combine = Image.new("RGBA", template.size)
    combine.paste(template, (0, 0))

    final_card = ImageDraw.Draw(combine)
    final_card.text(nickname_position, user_nickname, fill=font_color, font=nickname_font)
    final_card.text(bcard_position, fullNumber, fill=font_color, font=bcard_font)

    combine.save(f"{card_dir}{fullNumber}.png", "PNG")