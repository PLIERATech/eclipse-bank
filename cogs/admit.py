import nextcord as nxc
from nextcord.ext import commands
from const import *

class Admit(commands.Cog):
    def __init__(self, client):
        self.client = client

def setup(client):
    client.add_cog(Admit(client))
