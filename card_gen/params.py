import os
from supabase import Client
from supabase import *
from dotenv import load_dotenv
from PIL import Image
from const import *

load_dotenv()

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = Client(url, key)

font = './card_gen/assets/font.ttf'
card_dir = './card_gen/cards/'

type_info = suffixes

color_templates = {
        "🔴 Red": Image.open("./card_gen/assets/template_red.png"),
        "🟠 Orange": Image.open("./card_gen/assets/template_orange.png"),
        "🟡 Yellow": Image.open("./card_gen/assets/template_yellow.png"),
        "🟢 Green": Image.open("./card_gen/assets/template_green.png"),
        "🔵 Blue": Image.open("./card_gen/assets/template_blue.png"),
        "🟣 Purple": Image.open("./card_gen/assets/template_purple.png"),
        "⚫ Black": Image.open("./card_gen/assets/template_black.png"),
        "⚪ White": Image.open("./card_gen/assets/template_white.png"),
        "💸 Banker": Image.open("./card_gen/assets/template_banker.png"),
        "💎 CEO": Image.open("./card_gen/assets/template_ceo.png")
    }