from const import *

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | 📋 %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

def admit_Log(nickname, id, status):
    logging.info(f"❗ {nickname} | {id} =|= Воспользовался командой /принять ({status}) ")