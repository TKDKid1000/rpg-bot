import database
import os
import discord
import random
import time
import asyncio
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
    # otherwise a   dd them to the database with default items and save it
    else:
        members[nameid] = database.load("items.json")
        database.save(members, "data.json")

# COMMANDS

# battle command
@bot.command()
async def battle(ctx):
    enemyhp = 100
    itemdamage = database.load("damage.json")
    members = database.load("data.json")
    enemies = database.load("enemies.json")
    enemy = random.choice(enemies)
    nameid = str(ctx.author.id)
    weapon = members[nameid]["weapon"]

    # check to make sure command is used in correct channel
    def cmdcheck(author):
        def inner_check(message): 
            if message.author != author:
                return False
            else:
                if message.channel == ctx.channel:
                    return True
                else:
                    return False

        return inner_check

    # start of fight
    if members[nameid]["health"] > 25:
        await ctx.send(f"{enemy} appears out of nowhere! Prepare to fight!")
        while True:
            cmd = await bot.wait_for("message", check=cmdcheck(ctx.author))
            # if command is attack 
            if cmd.content.lower().startswith("a"):
                playerdamage = random.randint(1, itemdamage[weapon])
                enemydamage = random.randint(1, 20)
                await ctx.send("Attacking! " + str(playerdamage) + " damage!")
                await ctx.send(enemy + " attacks! " + str(enemydamage) + " damage!")
                members[nameid]["health"] -= enemydamage
                enemyhp -= playerdamage
                await ctx.send("You have " + str(members[nameid]["health"]) + " health left!")
                await ctx.send(enemy + " has " + str(enemyhp) + " health left!")
                if enemyhp < 1:
                    await ctx.send("You killed " + enemy)
                    members[nameid]["kills"] += 1
                    database.save(members, "data.json")
                    break
                    return
                elif members[nameid]["health"] < 1:
                    members[nameid]["deaths"] += 1
                    members[nameid]["health"] = 1
                    await ctx.send("You died to " + enemy)
                    database.save(members, "data.json")
                    break
                    return
            # if command is heal
            elif cmd.content.lower().startswith("h"):
                await ctx.send("Healing!")
                if members[nameid]["items"]["apples"] > 0:
                    members[nameid]["items"]["apples"] -= 1
                    members[nameid]["health"] += 10
                    await ctx.send("Used 1 apple and healed 10 health!")
                    await ctx.send("You have " + str(members[nameid]["health"]) + " health left!")
                elif members[nameid]["items"]["water"] > 0:
                    members[nameid]["items"]["apples"] -= 1
                    members[nameid]["water"] += 10
                    await ctx.send("Used 1 cup of water and healed 10 health!")
                    await ctx.send("You have " + str(members[nameid]["health"]) + " health left!")
                else:
                    await ctx.send("Couldn't heal! You lost a turn!")
                database.save(members, "data.json")
                enemydamage = random.randint(1, 20)
                await ctx.send(enemy + " attacks! " + str(enemydamage) + " damage!")
                members[nameid]["health"] -= enemydamage
                await ctx.send("You have " + str(members[nameid]["health"]) + " health left!")
                if enemyhp < 1:
                    await ctx.send("You killed " + enemy)
                    database.save(members, "data.json")
                    break
                    return
                elif members[nameid]["health"] < 1:
                    members[nameid]["deaths"] += 1
                    members[nameid]["health"] = 1
                    await ctx.send("You died to " + enemy)
                    database.save(members, "data.json")
                    break
                    return
            # if command is special
            elif cmd.content.lower().startswith("s"):
                await ctx.send("Using special!")
                if members[nameid]["magic"] > 40:
                    await ctx.send("Sending in a super magic attack!")
                    enemyhp -= 40
                    await ctx.send(enemy + " has " + str(enemyhp) + " health left!")
                else:
                    await ctx.send("You are too tired to use special!")
                enemydamage = random.randint(1, 20)
                await ctx.send(enemy + " attacks! " + str(enemydamage) + " damage!")
                members[nameid]["health"] -= enemydamage
                await ctx.send("You have " + str(members[nameid]["health"]) + " health left!")
                if enemyhp < 1:
                    await ctx.send("You killed " + enemy)
                    database.save(members, "data.json")
                    break
                    return
                elif members[nameid]["health"] < 1:
                    members[nameid]["deaths"] += 1
                    members[nameid]["health"] = 1
                    await ctx.send("You died to " + enemy)
                    database.save(members, "data.json")
                    break
                    return
            # otherwise default to attack
            else:
                playerdamage = random.randint(1, itemdamage[weapon])
                enemydamage = random.randint(1, 20)
                await ctx.send("Attacking! " + str(playerdamage) + " damage!")
                await ctx.send(enemy + " attacks! " + str(enemydamage) + " damage!")
                members[nameid]["health"] -= enemydamage
                enemyhp -= playerdamage
                await ctx.send("You have " + str(members[nameid]["health"]) + " health left!")
                await ctx.send(enemy + " has " + str(enemyhp) + " health left!")
                if enemyhp < 1:
                    await ctx.send("You killed " + enemy)
                    database.save(members, "data.json")
                    break
                    return
                elif members[nameid]["health"] < 1:
                    members[nameid]["deaths"] += 1
                    members[nameid]["health"] = 1
                    await ctx.send("You died to " + enemy)
                    database.save(members, "data.json")
                    break
                    return
            database.save(members, "data.json")
    else:
        await ctx.send("You don't have enough health to start a fight! Please heal up to 25 hp.")



# heal command
@bot.command()
async def heal(ctx):
    members = database.load("data.json")
    nameid = str(ctx.author.id)
    await ctx.send("Healing!")
    if members[nameid]["items"]["apples"] > 0:
        members[nameid]["items"]["apples"] -= 1
        members[nameid]["health"] += 10
        await ctx.send("Used 1 apple and healed 10 health!")
        await ctx.send("You have " + str(members[nameid]["health"]) + " health left!")
    elif members[nameid]["items"]["water"] > 0:
        members[nameid]["items"]["water"] -= 1
        members[nameid]["health"] += 10
        await ctx.send("Used 1 cup of water and healed 10 health!")
        await ctx.send("You have " + str(members[nameid]["health"]) + " health left!")
    else:
        await ctx.send("Couldn't heal! Maybe collect some water or apples?")
    database.save(members, "data.json")


# search command
@bot.command(aliases=['explore', 'mine', 'find'])
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
            await asyncio.sleep(3)
            await ctx.send(f"You found {amount} rocks.")
            await ctx.send(f"You found {amount2} iron.")
            members[nameid]["items"]["rocks"] += amount
            members[nameid]["items"]["iron"] += amount2
        elif location.lower().startswith("d"):
            await ctx.send("Attempting to search the dessert...")
            await asyncio.sleep(3)
            await ctx.send(f"You found {amount} cactus.")
            await ctx.send(f"You found {amount2} cups of sand")
            members[nameid]["items"]["cactus"] += amount
            members[nameid]["items"]["sand"] += amount2
        elif location.lower().startswith("o"):
            await ctx.send("Attempting to search the ocean...")
            await asyncio.sleep(3)
            await ctx.send(f"You found {amount} fish.")
            await ctx.send(f"You found {amount2} cups of water.")
            members[nameid]["items"]["fish"] += amount
            members[nameid]["items"]["water"] += amount2
        elif location.lower().startswith("f"):
            await ctx.send("Attempting to search the forest...")
            await asyncio.sleep(3)
            await ctx.send(f"You found {amount} apples.")
            await ctx.send(f"You found {amount2} sticks.")
            members[nameid]["items"]["apples"] += amount
            members[nameid]["items"]["sticks"] += amount
        else:
            await ctx.send("Please provide a valid location!")
            await ctx.send("Choose from: mine, dessert, ocean, forest")

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

@bot.command()
async def stats(ctx):
    # load from the database
    members = database.load("data.json")
    memberid = str(ctx.author.id)
    stats = members[memberid]
    statmsg = ""
    statmsg = statmsg + f'Current Health: {stats["health"]}\n'
    statmsg = statmsg + f'Current Magic: {stats["magic"]}\n'
    statmsg = statmsg + f'Kill Count: {stats["kills"]}\n'
    statmsg = statmsg + f'Death Count: {stats["deaths"]}\n'
    await ctx.send(f'''```{statmsg}```''')


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
