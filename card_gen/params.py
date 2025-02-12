import os
from supabase import Client
from supabase import *
from dotenv import load_dotenv
from PIL import Image

load_dotenv()

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = Client(url, key)

# font = './assets/font.ttf'
# card_dir = './cards/'
# template_red = Image.open("./assets/template_red.png")
# template_orange = Image.open("./assets/template_orange.png")
# template_yellow = Image.open("./assets/template_yellow.png")
# template_green = Image.open("./assets/template_green.png")
# template_blue = Image.open("./assets/template_blue.png")
# template_purple = Image.open("./assets/template_purple.png")
# template_black = Image.open("./assets/template_black.png")
# template_white = Image.open("./assets/template_white.png")

font = './card_gen/assets/font.ttf'
card_dir = './card_gen/cards/'
template_red = Image.open("./card_gen/assets/template_red.png")
template_orange = Image.open("./card_gen/assets/template_orange.png")
template_yellow = Image.open("./card_gen/assets/template_yellow.png")
template_green = Image.open("./card_gen/assets/template_green.png")
template_blue = Image.open("./card_gen/assets/template_blue.png")
template_purple = Image.open("./card_gen/assets/template_purple.png")
template_black = Image.open("./card_gen/assets/template_black.png")
template_white = Image.open("./card_gen/assets/template_white.png")
template_cio = Image.open("./card_gen/assets/template_cio.png")