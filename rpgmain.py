import asyncio
import os
import random
import time
import discord
from discord.ext import commands
from discord.utils import get
import database

# define bot
bot = commands.Bot(command_prefix=".")

# remove uneeded commands
bot.remove_command("help")

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
        members[nameid] = database.load("items.json")
        database.save(members, "data.json")

# COMMANDS

# help command
@bot.command(aliases=['commands'])
async def help(ctx):
    # read the file
    helpmsg = database.load("help.json")
    # set the embed attributes to the sections from the file
    embed=discord.Embed(title=helpmsg["title"], url=helpmsg["link"], description=helpmsg["content"], color=discord.Colour.from_rgb(helpmsg["color"][0], helpmsg["color"][1], helpmsg["color"][2]))
    embed.set_thumbnail(url=helpmsg["image"])
    # send it
    await ctx.send(embed=embed)

# battle command
@bot.command(aliases=['fight', 'monster'])
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
        await ctx.send(f"```{enemy} appears out of nowhere! Prepare to fight!```")
        while True:
            cmd = await bot.wait_for("message", check=cmdcheck(ctx.author))
            # if command is attack
            fightmsg = ""
            if cmd.content.lower().startswith("a"):
                playerdamage = random.randint(1, itemdamage[weapon])
                enemydamage = random.randint(1, 20)
                fightmsg = fightmsg + "Attacking! " + str(playerdamage) + " damage!" + "\n"
                fightmsg = fightmsg + enemy + " attacks! " + str(enemydamage) + " damage!" + "\n"
                members[nameid]["health"] -= enemydamage
                enemyhp -= playerdamage
                fightmsg = fightmsg + "You have " + str(members[nameid]["health"]) + " health left!" + "\n"
                fightmsg = fightmsg + enemy + " has " + str(enemyhp) + " health left!" + "\n"
                if enemyhp < 1:
                    await ctx.send("```You killed " + enemy + "```")
                    if members[nameid]["health"] < 1:
                        members[nameid]["health"] = 1
                    members[nameid]["kills"] += 1
                    database.save(members, "data.json")
                    break
                    return
                elif members[nameid]["health"] < 1:
                    members[nameid]["deaths"] += 1
                    members[nameid]["health"] = 1
                    await ctx.send("```You died to " + enemy + "```")
                    database.save(members, "data.json")
                    break
                    return
            # if command is heal
            elif cmd.content.lower().startswith("h"):
                await ctx.send("Healing!")
                if members[nameid]["items"]["apples"] > 0:
                    members[nameid]["items"]["apples"] -= 1
                    members[nameid]["health"] += 10
                    fightmsg = fightmsg + "Used 1 apple and healed 10 health!" + "\n"
                    fightmsg = fightmsg + "You have " + str(members[nameid]["health"]) + " health left!" + "\n"
                elif members[nameid]["items"]["water"] > 0:
                    members[nameid]["items"]["apples"] -= 1
                    members[nameid]["health"] += 10
                    fightmsg = fightmsg + "Used 1 cup of water and healed 10 health!" + "\n"
                    fightmsg = fightmsg + "You have " + str(members[nameid]["health"]) + " health left!" + "\n"
                else:
                    fightmsg = fightmsg + "Couldn't heal! You lost a turn!" + "\n"
                database.save(members, "data.json")
                enemydamage = random.randint(1, 20)
                fightmsg = fightmsg + enemy + " attacks! " + str(enemydamage) + " damage!" +"\n"
                members[nameid]["health"] -= enemydamage
                fightmsg = fightmsg + "You have " + str(members[nameid]["health"]) + " health left!" + "\n"
                if enemyhp < 1:
                    await ctx.send("```You killed " + enemy + "```")
                    if members[nameid]["health"] < 1:
                        members[nameid]["health"] = 1
                    database.save(members, "data.json")
                    break
                    return
                elif members[nameid]["health"] < 1:
                    members[nameid]["deaths"] += 1
                    members[nameid]["health"] = 1
                    await ctx.send("```You died to " + enemy + "```")
                    database.save(members, "data.json")
                    break
                    return
            # if command is special
            elif cmd.content.lower().startswith("s"):
                fightmsg = fightmsg + "Using special!" + "\n"
                if members[nameid]["magic"] > 40:
                    members[nameid]["magic"] -= 40
                    fightmsg = fightmsg + "Sending in a super magic attack!" + "\n"
                    fightmsg = fightmsg + f"You have {str(members[nameid]['magic'])}" + "\n"
                    enemyhp -= 40
                    fightmsg = fightmsg + enemy + " has " + str(enemyhp) + " health left!" + "\n"
                else:
                    fightmsg = fightmsg + "You are too tired to use special!" + "\n"
                enemydamage = random.randint(1, 20)
                fightmsg = fightmsg + enemy + " attacks! " + str(enemydamage) + " damage!" + "\n"
                members[nameid]["health"] -= enemydamage
                fightmsg = fightmsg + "You have " + str(members[nameid]["health"]) + " health left!" + "\n"
                if enemyhp < 1:
                    await ctx.send("```You killed " + enemy + "```")
                    if members[nameid]["health"] < 1:
                        members[nameid]["health"] = 1
                    database.save(members, "data.json")
                    break
                    return
                elif members[nameid]["health"] < 1:
                    members[nameid]["deaths"] += 1
                    members[nameid]["health"] = 1
                    await ctx.send("```You died to " + enemy + "```")
                    database.save(members, "data.json")
                    break
                    return
            # otherwise default to attack
            else:
                playerdamage = random.randint(1, itemdamage[weapon])
                enemydamage = random.randint(1, 20)
                fightmsg = fightmsg + "Attacking! " + str(playerdamage) + " damage!" + "\n"
                fightmsg = fightmsg + enemy + " attacks! " + str(enemydamage) + " damage!" + "\n"
                members[nameid]["health"] -= enemydamage
                enemyhp -= playerdamage
                fightmsg = fightmsg + "You have " + str(members[nameid]["health"]) + " health left!" + "\n"
                fightmsg = fightmsg + enemy + " has " + str(enemyhp) + " health left!" + "\n"
                if enemyhp < 1:
                    await ctx.send("```You killed " + enemy + "```")
                    if members[nameid]["health"] < 1:
                        members[nameid]["health"] = 1
                    database.save(members, "data.json")
                    break
                    return
                elif members[nameid]["health"] < 1:
                    members[nameid]["deaths"] += 1
                    members[nameid]["health"] = 1
                    await ctx.send("```You died to " + enemy + "```")
                    database.save(members, "data.json")
                    break
                    return
            await ctx.send(f"```{fightmsg}```")
            database.save(members, "data.json")
    else:
        await ctx.send("```You don't have enough health to start a fight! Please heal up to 25 hp.```")


@bot.command()
async def craft(ctx, *, item=None):
    # load members
    members = database.load("data.json")
    # define self
    nameid = str(ctx.author.id)
    # load recipes
    recipes = database.load("recipes.json")
    # check if recipe is None
    if item == None:
        msg = '''```Please select an item from below!\n'''
        for recipe in recipes:
            msg = msg + recipe + "\n"
        msg = msg + "```"
        await ctx.send(msg)
        return
        
    # check if the recipe exists
    if members[nameid]["weapon"] == item:
        await ctx.send("```You already have that item!```")
        return
    if item in recipes:
        # define the recipe
        recipe = recipes[item]
        # check if you have every item
        for material in recipe:
            # if you dont have enough of the item then end loop
            if recipe[material] - members[nameid]["items"][material] > 0:
                await ctx.send("```You don't have enough items! Do some exploring!```")
                return
        # will only run if the first was successful (because it would have returned)
        for material in recipe:
            # subtract the item
            members[nameid]["items"][material] -= recipe[material]
            database.save(members, "data.json")
        members[nameid]["weapon"] = item
        database.save(members, "data.json")
        await ctx.send(f"```Crafted {item}, check your items.```")

    else:
        await ctx.send("```That item does not exist!```")



# heal command
@bot.command(aliases=['regen', 'drink', 'eat'])
async def heal(ctx):
    members = database.load("data.json")
    nameid = str(ctx.author.id)
    msg = await ctx.send("```Healing!```")
    if members[nameid]["items"]["apples"] > 0:
        members[nameid]["items"]["apples"] -= 1
        members[nameid]["health"] += 10
        await msg.edit(content=f"```Used 1 apple and healed 10 health!\nYou have {members[nameid]['health']} health left!```")
    elif members[nameid]["items"]["water"] > 0:
        members[nameid]["items"]["water"] -= 1
        members[nameid]["health"] += 10
        await msg.edit(content=f"```Used 1 cup of water and healed 10 health!\nYou have {members[nameid]['health']} health left!```")
    else:
        await msg.edit(content="```Couldn't heal! Maybe collect some water or apples?```")
    database.save(members, "data.json")


# search command
@bot.command(aliases=['explore', 'mine', 'find', 'collect'])
async def search(ctx, location="None"):
    if location == "None":
        await ctx.send('''Please provide a location!
        Choose from: mine, dessert, ocean, forest''')
    else:
        members = database.load("data.json")
        nameid = str(ctx.author.id)
        amount = random.randint(0, 3)
        amount2 = random.randint(0, 3)
        if location.lower().startswith("m"):
            msg = await ctx.send("```Attempting to search the mine...```")
            await asyncio.sleep(3)
            await msg.edit(content=f'''```You found {amount} rocks.\nYou found {amount2} iron.```''')
            members[nameid]["items"]["rocks"] += amount
            members[nameid]["items"]["iron"] += amount2
        elif location.lower().startswith("d"):
            msg = await ctx.send("```Attempting to search the dessert...```")
            await asyncio.sleep(3)
            await msg.edit(content=f'''```You found {amount} cactus.\nYou found {amount2} cups of sand.```''')
            members[nameid]["items"]["cactus"] += amount
            members[nameid]["items"]["sand"] += amount2
        elif location.lower().startswith("o"):
            msg = await ctx.send("```Attempting to search the ocean...```")
            await asyncio.sleep(3)
            await msg.edit(content=f'''```You found {amount} fish.\nYou found {amount2} cups of water.```''')
            members[nameid]["items"]["fish"] += amount
            members[nameid]["items"]["water"] += amount2
        elif location.lower().startswith("f"):
            msg = await ctx.send("```Attempting to search the forest...```")
            await asyncio.sleep(3)
            await msg.edit(content=f'''```You found {amount} apples.\nYou found {amount2} sticks.```''')
            members[nameid]["items"]["apples"] += amount
            members[nameid]["items"]["sticks"] += amount
        else:
            await ctx.send("```Please provide a valid location!```\nChoose from: mine, dessert, ocean, forest")

    database.save(members, "data.json")


# items command
@bot.command(aliases=['inv', 'inventory'])
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

@bot.command(aliases=['info', 'data'])
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
