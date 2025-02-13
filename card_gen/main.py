from PIL import Image, ImageDraw, ImageFont
from supabase import *
from .params import *

base_color = (240, 240, 240)
unique_color = (42, 42, 42)

nickname_position = (644, 515)
bcard_position = (534, 559)

nickname_font = ImageFont.truetype(font, 48)
bcard_font = ImageFont.truetype(font, 96)

# red orange yellow green blue purple black white

def card_generate(dsc_id, number, user_nickname, color):

    fullNumber = ""
    suffix = ""
    template = ""
    font_color = base_color

    get = supabase.table("cards").select("*").eq("owner", dsc_id).eq("number", number).execute()

    type = str(get.data[0]["type"])
    owner = get.data[0]["owner"]

    templates = {
        "red": template_red,
        "orange": template_orange,
        "yellow": template_yellow,
        "green": template_green,
        "blue": template_blue,
        "purple": template_purple,
        "black": template_black,
        "white": template_white,
        "cio": template_cio,
    }

    suffixes = {
        "private": "EBP-",
        "team": "EBT-",
        "banker": "EBS-",
        "cio": "CIO-",
    }

    template = templates.get(color, None)
    suffix = suffixes.get(type, "")

    if color == "white":
        font_color = unique_color

    if type == "cio":
        template = template_cio
        color = ""

    fullNumber = f"{suffix}{number}"

    try:
        template.convert("RGBA")
    except FileNotFoundError:
        print("Ошибка: файл 'template.png' не найден в директории.")
        return
    
    if get.data:
        nickname_text = user_nickname
        card_text = fullNumber

        combine = Image.new("RGBA", template.size)
        combine.paste(template, (0, 0))

        final_card = ImageDraw.Draw(combine)
        final_card.text(nickname_position, nickname_text, fill=font_color, font=nickname_font)
        final_card.text(bcard_position, card_text, fill=font_color, font=bcard_font)

        combine.save(f"{card_dir}{fullNumber}.png", "PNG")

    else:
        print("Такой записи нет!")