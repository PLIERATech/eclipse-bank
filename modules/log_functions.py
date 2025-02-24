from const import *
from db import *

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | 📋 %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

def PermsLog(nickname, id, command, status):
    logging.info(f"❗ {nickname} | {id} =|= Воспользовался командой {command} ({status}) ")

def cardCreateLog(banker, number, user):
    logging.info(f" • {banker} оформил карту {number} для {user}")

def clientCreateLog(user):
    logging.info(f"• {user} стал клиентом Eclipse Bank!")

def clientDeleteLog(user):
    logging.info(f"• Банковский счёт {user} был удалён!")