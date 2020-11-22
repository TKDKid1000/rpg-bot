import database
import os
import discord
from discord.ext import commands
from discord.utils import get

bot = commands.Bot(command_prefix="!")

if not "data.json" in os.listdir():
    with open("data.json", "w") as newfile:
        newfile.write("[]")
        print("added new file")

@bot.event
async def on_ready():
    print("Started bot as rpgbot#0405")

def add_to_database(member):
    pass

@bot.command()
async def battle():
    pass

@bot.command()
async def items():
    pass

@bot.event
async def on_message(message):
    add_to_database(message.author)