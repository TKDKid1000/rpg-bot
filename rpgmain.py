import database
import os
import discord
import random
import time
from discord.ext import commands
from discord.utils import get

# define bot
bot = commands.Bot(command_prefix="!")

# check if the data.json file exists. if not, create one
if not "data.json" in os.listdir():
    with open("data.json", "w") as newfile:
        newfile.write("[]")
        print("added new file")

# read the token from the file
tokenf = open("token.txt")
token = tokenf.read()
tokenf.close()

# bot startup event
@bot.event
async def on_ready():
    print("Started bot as rpgbot#0405")


# function to add a discord.Member to the database
def add_to_database(member: discord.Member):
    # save the database as members
    members = database.load("data.json")
    # get the member id (string)
    nameid = str(member.id)
    # if they already exist then return
    if nameid in members:
        return
    # otherwise add them to the database with default items and save it
    else:
        members[nameid] = {
            "items" : {
            "rocks" : 0, "iron" : 0,
            "cactus" : 0, "sand" : 0,
            "fish" : 0, "water" : 0,
            "apples" : 0, "sticks" : 0}, 
            "health" : 100, 
            "weapon" : "stick", 
            "money" : 10.00
            }
        database.save(members, "data.json")

# COMMANDS

# battle command
@bot.command()
async def battle(ctx):
    enemies = database.load("enemies.json")
    enemy = random.choice(enemies)
    def check(author):
        def inner_check(message): 
            if message.author != author:
                return False
            else:
                if message.channel == ctx.channel:
                    return True
                else:
                    return False

        return inner_check
    await ctx.send(f"{enemy} appears out of nowhere! Prepare to fight!")
    cmd = await bot.wait_for("message", check=check(ctx.author))
    if cmd.content.lower().startswith("a"):
        await ctx.send("Attacking!")
    elif cmd.content.lower().startswith("h"):
        await ctx.send("Healing!")
    elif cmd.content.lower().startswith("i"):
        item = await bot.wait_for("message", check=(ctx.author))
        await ctx.send("Used item!")
    else:
        await ctx.send("Attacking!")



# search command
@bot.command()
async def search(ctx, location="None"):
    if location == "None":
        await ctx.send("Please provide a location!")
        await ctx.send("Choose from: mine, dessert, ocean, forest")
    else:
        members = database.load("data.json")
        nameid = str(ctx.author.id)
        amount = random.randint(0, 3)
        amount2 = random.randint(0, 3)
        if location.lower().startswith("m"):
            await ctx.send("Attempting to search the mine...")
            time.sleep(3)
            await ctx.send(f"You found {amount} rocks.")
            await ctx.send(f"You found {amount2} iron.")
            members[nameid]["items"]["rocks"] += amount
            members[nameid]["items"]["iron"] += amount2
        if location.lower().startswith("d"):
            await ctx.send("Attempting to search the dessert...")
            time.sleep(3)
            await ctx.send(f"You found {amount} cactus.")
            await ctx.send(f"You found {amount2} cups of sand")
            members[nameid]["items"]["cactus"] += amount
            members[nameid]["items"]["sand"] += amount2
        if location.lower().startswith("o"):
            await ctx.send("Attempting to search the ocean...")
            time.sleep(3)
            await ctx.send(f"You found {amount} fish.")
            await ctx.send(f"You found {amount2} cups of water.")
            members[nameid]["items"]["fish"] += amount
            members[nameid]["items"]["water"] += amount2
        if location.lower().startswith("f"):
            await ctx.send("Attempting to search the forest...")
            time.sleep(3)
            await ctx.send(f"You found {amount} apples.")
            await ctx.send(f"You found {amount2} sticks.")
            members[nameid]["items"]["apples"] += amount
            members[nameid]["items"]["sticks"] += amount
    database.save(members, "data.json")


# items command
@bot.command()
async def items(ctx):
    # load from the database
    members = database.load("data.json")
    memberid = str(ctx.author.id)
    items = members[memberid]["items"]
    # item display
    itemmsg = ""
    itemmsg = itemmsg + 'Here is your items:\n'
    for item in items:
        itemmsg = itemmsg + f'{item}, {members[memberid]["items"][item]}\n'
    # money display
    itemmsg = itemmsg + f'Here is your money: {members[memberid]["money"]}\n'
    # weapon display
    itemmsg = itemmsg + f'Here is your weapon: {members[memberid]["weapon"]}'
    await ctx.send(f'''```{itemmsg}```''')


# EVENTS

# on_message event, adds a member to the database.
@bot.event
async def on_message(message):
    # if the message author is any bot then return
    if message.author.bot:
        return
    # add them to the database
    add_to_database(message.author)
    # process commands
    await bot.process_commands(message)

bot.run(token)
