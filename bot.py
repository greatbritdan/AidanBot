import discord
import os
import asyncio
import datetime
import math

from discord.ext import commands
from discord.ext.commands import has_permissions
from discord.utils import get

# generate random integer values
from random import seed
from random import randint
seed(randint(1, 1000))

PREFIX = "$"
VERSION = "Beta 1.0"

client = commands.Bot(command_prefix=PREFIX, case_insensitive=True)
client.remove_command('help')

##############
### EMBEDS ###
##############

# make an embed and send it back
def getEmbed(ctx, command, title=False, description=False, image=False, red=False):
    if red:
        col = discord.Color.from_rgb(220, 29, 37)
    else:
        col = discord.Color.from_rgb(20, 29, 37)

    emb = discord.Embed(title=title, description=description, color=col)
    if image:
        emb.set_image(url=image)

    emb.set_footer(text="Requested by {0} in #{1}".format(ctx.author, ctx.channel))
    emb.set_author(name="AidanBot > " + command, icon_url="https://cdn.discordapp.com/attachments/806147106054078482/861645806851719188/aidanbot.png")
    emb.timestamp = datetime.datetime.utcnow()

    return emb

# for when a command fails
def getErrorEmbed(ctx, error):
    emb = discord.Embed(title="AidanBot Encountered an error and your command was cancelled.", description=error, color=discord.Color.from_rgb(220, 29, 37))
    emb.set_footer(text="Requested by {0} in #{1}".format(ctx.author, ctx.channel))
    emb.set_author(name="AidanBot > Error", icon_url="https://cdn.discordapp.com/attachments/806147106054078482/861645806851719188/aidanbot.png")
    emb.timestamp = datetime.datetime.utcnow()

    return emb

# add a feild to an embed
def addField(emb, fname, fvalue, fline=False):
    emb.add_field(name=fname, value=fvalue, inline=fline)
    return emb

#################
### FUNCTIONS ###
#################

thelist = {
    "1": "1", "2": "2", "3": "3", "4": "4", "5": "5", "6": "6",
    "7": "7", "8": "8", "9": "9", "0": "0", "a": "11", "b": "12",
    "c": "13", "d": "14", "e": "15", "f": "16", "g": "17", "h": "18",
    "i": "19", "j": "20", "k": "21", "l": "22", "m": "23", "n": "24",
    "o": "25", "p": "26", "q": "27", "r": "28", "s": "29", "t": "30",
    "u": "31", "v": "32", "w": "33", "x": "34", "y": "35", "z": "36",
    " ": "37", ".": "38", ",": "39", ":": "40", ";": "41", "'": "42",
    "/": "43"
}

def clamp(n, minn, maxn):
    return max(min(maxn, n), minn)

def getIntFromText(txt):
    sed = ""
    for letter in txt:
        if letter in thelist:
            sed = sed + thelist[letter]
        else:
            sed = sed + "44"

    return (int(sed))

def userHasPermission(member, permission):
    for perm in member.guild_permissions:
        if str(perm[0]) == permission and perm[1] == True:
            return True

    return False

##############
### EVENTS ###
##############

@client.event
async def on_ready():
    print(f'Logged in as big boy {client.user}')

    activity = discord.Activity(name=f'use {PREFIX}help for help.', type=discord.ActivityType.playing)
    await client.change_presence(activity=activity)

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if not message.guild:
        await message.channel.send("Not available outside of guilds (servers)")
        return
    
    if "discord.gg" in message.content.lower():
        delete_invites = await GETDATA(message, "delete_invites")
        if delete_invites and userHasPermission(message.author, "kick_members") == False:
            invite_allow_channel = await GETDATA(message, "invite_allow_channel")
            if message.channel.name != invite_allow_channel:
                await message.delete()
                if invite_allow_channel != False:
                    await message.channel.send(f"No invites allowed outside of {invite_allow_channel}! >:(")
                else:
                    await message.channel.send(f"No invites allowed! >:(")

    role = get(message.author.roles, name="AidanBotBanned")
    if not role:
        await client.process_commands(message)

@client.event
async def on_guild_join(guild):
    print(f"Added to {guild.name}!")

@client.event
async def on_guild_remove(guild):
    print(f"Left {guild.name}!")

@client.event
async def on_command_error(ctx, error):
    err = "I seem to have ran into an error, It's best to let Aidan know."
    if isinstance(error, commands.BotMissingPermissions):
        err = err + "\n\nError: Bot Missing Permissions!"
    elif isinstance(error, commands.MissingPermissions):
        err = err + "\n\nError: User Missing Permissions!"

    err = err + f"\n\nFull Error: {error}"

    emb = getErrorEmbed(ctx, err)
    await ctx.send(embed=emb)

################
### COMMANDS ###
################

COMMANDS = []

#   IMPORTANT   #

COMMANDS.append(["Important", "help", "Returns a list of most commands.", False])
@client.command()
async def help(ctx):
    commandsections = []
    for i in range(len(COMMANDS)):
        if COMMANDS[i][0] not in commandsections:
            commandsections.append(COMMANDS[i][0])

    emb = getEmbed(ctx, "Help", "All commands you can use:", False)

    for sect in commandsections:
        txt = ""
        for i in range(len(COMMANDS)):
            if COMMANDS[i][0] == sect:
                if COMMANDS[i][3] == False or (COMMANDS[i][3] == "mods" and userHasPermission(ctx.author, "kick_members") == True) or (COMMANDS[i][3] == "admin" and userHasPermission(ctx.author, "administrator") == True):
                    txt = txt + f"`{PREFIX}{COMMANDS[i][1]}`: {COMMANDS[i][2]}"
                    if COMMANDS[i][3] == "mods":
                        txt = txt + " (Mods Only)"
                    elif COMMANDS[i][3] == "admin":
                        txt = txt + " (Admins Only)"
                    txt = txt + "\n"
                
        if txt != "":
            emb = addField(emb, sect, txt)

    await ctx.send(embed=emb)

COMMANDS.append(["Important", "info", "Returns info about the bot.", False])
@client.command()
async def info(ctx):
    emb = getEmbed(ctx, "Info", "Hey, I am AidanBot, A small discord bot created by Aidan#8883 for his server that now anyone can use!", f"[Aidan's Youtube](https://www.youtube.com/c/AidanMapper)\n[Aidan's Twitter](https://twitter.com/AidanMapper)\n[Aidan's Discord Server](https://discord.gg/xBnBEpHdb6)\n[Invite me to your server!](https://discord.com/api/oauth2/authorize?client_id=804319602292949013&permissions=8&scope=bot)\n\nIf you find a bug or he has made a typo <:AidanSmug:837001740947161168>, you can report it to Aidan on his server in one of the bot chats. You can also suggest features in the suggestion channel on his server.\n\nNote: If you are a server admin and want to setup a feature (e.g. if server invites are deleted automaticaly) use {PREFIX}config!")
    emb = addField(emb, "Version:", VERSION)
    await ctx.send(embed=emb)

COMMANDS.append(["Important", "invite", "Add the bot to your server.", False])
@client.command()
async def invite(ctx):
    await ctx.send("Y- you want me on your server??? I'd love too!!! https://discord.com/api/oauth2/authorize?client_id=804319602292949013&permissions=8&scope=bot")

COMMANDS.append(["Important", "lockdown", "Delete all invites.", "admin"])
@client.command()
@has_permissions(administrator=True)
async def lockdown(ctx):
    for invite in await ctx.guild.invites():
        await invite.delete()

    emb = getEmbed(ctx, "Lockdown", ":lock: **!Lockdown!** :lock:", "The owner has decided to lockdown the server! All invites have been deleted, no one can join so be careful not to leave by accident.", False, True)
    await ctx.send(embed=emb)

#   DATA   #

COMMANDS.append(["Values", "setup", "Sets up channel that hold server values and sets up default values.", "admin"])
@client.command()
@has_permissions(administrator=True)
async def setup(ctx):
    overwrites = {
        ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
    }
    channel = await ctx.guild.create_text_channel('aidanbot-serverdata', topic="**DON'T TALK HERE**, For AidanBot's per server data!", overwrites=overwrites)
    await channel.send("delete_invites=false\ninvite_allow_channel=false")
    
# val = await GETDATA(ctx, "teststring")
# suc = await SETDATA(ctx, "teststring", val)

COMMANDS.append(["Values", "config", "Get value or set value.", "admin"])
@client.command()
@has_permissions(administrator=True)
async def config(ctx, action=None, name=None, val=None):
    if action == "get" and name:
        val = await GETDATA(ctx, name)
        await ctx.send(f"{name} is currently set to {val}!")
    elif action == "set" and name and val:
        suc = await SETDATA(ctx, name, val)
        if suc:
            await ctx.send(f"{name} was set to {val}!")
        else:
            await ctx.send(f"{name} was not found!")

#   SAVE AND LOAD   #

async def GETMSG(ctx):
    channel = get(ctx.guild.text_channels, name="aidanbot-serverdata")
    if channel == None:
        await ctx.send(f"You need to run {PREFIX}setup first!")
        return False

    message = await channel.fetch_message(channel.last_message_id)
    if message == None:
        await ctx.send(f"Check the data, see if a message is there. if not, delete the channel and rerun {PREFIX}setup!")
        return False

    return message

async def GETDATA(ctx, name):
    message = await GETMSG(ctx)
    if message == False:
        return

    messcont = message.content

    data = messcont.splitlines()
    for var in data:
        dat = var.split('=')
        if dat[0] == name:
            val = dat[1]
            if dat[1] == "true":
                val = True
            elif dat[1] == "false":
                val = False
            else:
                try:
                    val = int(val)
                except ValueError:
                    kwlksdwlksw = 1

            return val

    return False

async def SETDATA(ctx, name, val):
    message = await GETMSG(ctx)
    if message == False:
        return

    messcont = message.content

    data = messcont.splitlines()
    suc = False
    newdata = []
    for var in data:
        dat = var.split('=')
        if dat[0] == name:
            dat[1] = val
            suc = True

        newdata.append(dat[0] + "=" + dat[1])

    stringdata = ""
    for var in newdata:
        stringdata = stringdata + "\n" + var
    stringdata = stringdata.strip()

    await message.edit(content=stringdata)

    return suc

#   GENERAL   #

COMMANDS.append(["General", "echo", "Says what is passed into it.", False])
@client.command()
async def echo(ctx, *, text:str="***intence nothingness***"):
    # echo echo
    await ctx.message.delete()
    await ctx.send(text)

COMMANDS.append(["General", "rate", "Rates what you pass into it.", False])
@client.command()
async def rate(ctx, *, thing:str="*thing*"):
    # rate dat ass :flushed:
    seed(getIntFromText(thing.lower()))

    responces = [
        ["{0} is worse than anything i have ever rated.", [-10, -10]],
        ["{0} is just awful, holy crap!", [-1, 0]],
        ["{0} is realy bad.", [0, 2]],
        ["{0} is alright, but could be better.", [2, 5]],
        ["I have no opinion on {0}.", [5, 5]],
        ["{0} is pretty good!", [4, 6]],
        ["{0} is great. Not the best tho.", [5, 8]],
        ["{0} is amazing!", [7, 9]],
        ["{0} is almost the best!", [9, 10]],
        ["{0} is the best thing, by far.", [10, 10]],
        ["I AM GOD", [10, 10]],
        ["No comment, I am not dying today :)", [5, 5]]
    ]

    # if it's aidanbot or aidan, respond differently
    index = randint(0, 9)
    if thing.lower() == "aidanbot":
        index = 10
    elif thing.lower() == "aidan":
        index = 11

    txt = responces[index][0]
    rating = randint(responces[index][1][0], responces[index][1][1])

    emb = getEmbed(ctx, "Rate", txt.format(thing), False)
    emb = addField(emb, "Score", "**{0}/10**".format(rating))

    await ctx.send(embed=emb)

COMMANDS.append(["General", "ask", "Answers your deepest quetsions.", False])
@client.command()
async def ask(ctx, *, question:str=None):
    # what is the meanding of life...
    seed(getIntFromText(question.lower()))

    if question == None:
        emb = getErrorEmbed(ctx, "Missing un-optional argument for command.")
        await ctx.send(embed=emb)
        return

    # get start, really easy
    start = ["My heart tells me... ", "In all honestly, ", "hAH, ", "", "", ""]
    start_txt = start[randint(0, len(start)-1)]

    # get end, different if it caonatins "how many"
    if "how many" in question.lower():
        number = str(randint(0,10))
        end = [f"At least {number}.", f"More than {number}, for sure.", f"{number}.", f"Take it or leave it. {number}."]
    else:
        end = ["Yes.", "No, not at all.", "idk, maybe.", "Answer is unclear.", "You will find out soon enough...", "S-sorry, this questions is just... too much for me to handle.", "Maybe the true answer was inside you all along!", "What???"]

    end_txt = end[randint(0, len(end)-1)]

    emb = getEmbed(ctx, "Ask", "What knowledge will i give you today...", False)
    emb = addField(emb, "Question", question)
    emb = addField(emb, "Answer", start_txt + end_txt)

    await ctx.send(embed=emb)

COMMANDS.append(["General", "decide", "Picks between the choices given.", False])
@client.command()
async def decide(ctx, *, decisions:str):
    # way eaiser than i eopected
    decisions = decisions.split(" ")
    emb = getEmbed(ctx, "Decide", False, "I choose... {0}".format(decisions[randint(0, len(decisions)-1)]))
    await ctx.send(embed=emb)

def getHealthBar(health, maxhealth, size, hashalf=False):
    healthperseg = maxhealth / size
    segsfilled = math.ceil(health / healthperseg)
    ishalf = False
    if hashalf and math.ceil((health - (healthperseg/2)) / healthperseg) < segsfilled:
        ishalf = True

    bar = ""
    for i in range(1, size+1):
        if i == 1:
            if i < segsfilled:
                e = "<:left_full:862331445526921287>"
            elif i == segsfilled:
                if ishalf:
                    e = "<:left_half:862331445700067328>"
                else:
                    e = "<:left_fullsingle:862331445750005770>"
            else:
                e = "<:left_empty:862331445720121365>"
        elif i < size:
            if i < segsfilled:
                e = "<:middle_full:862331445300428821>"
            elif i == segsfilled:
                if ishalf:
                    e = "<:middle_half:862331445845688340>"
                else:
                    e = "<:middle_fullsingle:862331445703737364>"
            else:
                e = "<:middle_empty:862331445813313606>"
        else:
            if i < segsfilled:
                e = "<:right_full:862331445657468939>"
            elif i == segsfilled:
                if ishalf:
                    e = "<:right_half:862331445702819880>"
                else:
                    e = "<:right_full:862331445657468939>"
            else:
                e = "<:right_empty:862331445313273857>"

        bar = bar + e

    return bar

COMMANDS.append(["General", "fightplus", "Fight a user or bot to the death. With extra options", False])
@client.command()
async def fightplus(ctx, user1:discord.User=None, user2:discord.User=None):
    if user1 == None:
        emb = getErrorEmbed(ctx, "Missing un-optional argument for command.")
        await ctx.send(embed=emb)
        return
    elif user2 == None:
        v1 = ctx.author
        v2 = user1
    else:
        v1 = user1
        v2 = user2
    
    questions = ["Max & Starter health?", "Max energy?"]
    answers = [100, 10]

    emb = getEmbed(ctx, "fight+ > setup", "N/A", "Type your awnser or `none` to keep default!\nmin is 5, max is 250!")
    MSG = await ctx.send(embed=emb)

    for i in range(0, len(questions)):
        def check(message):
            return (ctx.author == message.author)

        emb = getEmbed(ctx, "fight+ > setup", questions[i] + " (Default: {})".format(answers[i]), "Type your answer or `none` to keep default!")
        await MSG.edit(embed=emb)

        try:
            message = await client.wait_for("message", timeout=60, check=check)

            if message:
                if message.content.lower() != "none":
                    try:
                        answers[i] = int(message.content)
                    except ValueError:
                        emb = getErrorEmbed(ctx, message.content + " is not a valid argument. Needs to be an whole number!")
                        await ctx.send(embed=emb)
                        return

                    answers[i] = clamp(answers[i], 5, 250)

                await message.delete()

        except asyncio.TimeoutError:
            await MSG.delete()
            await ctx.send("Timeout.")
            return

    await MSG.delete()
    await FightNewgame(ctx, v1, v2, answers[0], answers[1])

COMMANDS.append(["General", "fight", "Fight a user or bot to the death.", False])
@client.command()
async def fight(ctx, user1:discord.User=None, user2:discord.User=None):
    if user1 == None:
        emb = getErrorEmbed(ctx, "Missing un-optional argument for command.")
        await ctx.send(embed=emb)
        return
    elif user2 == None:
        v1 = ctx.author
        v2 = user1
    else:
        v1 = user1
        v2 = user2

    await FightNewgame(ctx, v1, v2)

async def FightNewgame(ctx, p1:discord.User, p2:discord.User, mhealth:int=100, menergy:int=10):
    # setup vars and lists
    maxhealth = mhealth
    maxenergy = menergy
    player = {
        "p1": {
            "name": p1.name,
            "id": p1.id,
            "bot": p1.bot,
            "health": maxhealth,
            "energy": 4,
            "heals": 2
        },
        "p2": {
            "name": p2.name,
            "id": p2.id,
            "bot": p2.bot,
            "health": maxhealth,
            "energy": 4,
            "heals": 2
        }
    }

    turn = "p1"
    turnt = "p2"

    # for cheking if move can be used
    def checkMove(rec, typ, eng=0, con=None):
        if con:
            return (str(rec.emoji) == typ and player[turn]["energy"] >= eng and player[turn]["heals"] > 0)
        else:
            return (str(rec.emoji) == typ and player[turn]["energy"] >= eng)

    # for cheking if the right user uses valid reactions on a spesific message
    def check(rec, user):
        return (user.id == player[turn]["id"] and rec.message.id == MSG.id and (checkMove(rec, "❌", 0) or checkMove(rec, "🕓", 0) or checkMove(rec, "👊", 2) or checkMove(rec, "🍷", 0, True)))

    # embed for the fight command
    def getFightEmbed(ctx, action):
        emb = getEmbed(ctx, "Fight", player["p1"]["name"] + " VS " + player["p2"]["name"])
        addField(emb, player["p1"]["name"] + " Stats:", "`Health:` " + getHealthBar(player["p1"]["health"], maxhealth, 10, True) + " (" + str(player["p1"]["health"]) + ")\n`Energy:` " + getHealthBar(player["p1"]["energy"], menergy, 5, True) + " (" + str(player["p1"]["energy"]) + ")")
        addField(emb, player["p2"]["name"] + " Stats:", "`Health:` " + getHealthBar(player["p2"]["health"], maxhealth, 10, True) + " (" + str(player["p2"]["health"]) + ")\n`Energy:` " + getHealthBar(player["p2"]["energy"], menergy, 5, True) + " (" + str(player["p2"]["energy"]) + ")")

        if action:
            emb = addField(emb, action[0], action[1])

        text = f"🕓: `Wait (+1 Energy)`\n👊: `Attack  (-" + str(math.ceil(player[turn]["energy"] / 2)) + " Energy)`"
        if player[turn]["heals"] > 0:
            text = text + "\n🍷: `Heal (0 Energy) (" + str(player[turn]["heals"]) + " left)`"
        text = text + "\n❌: `Flee (0 Energy)`"

        emb = addField(emb, player[turn]["name"] + "'s Turn:", text)

        return emb

    embed = getFightEmbed(ctx, False)
    MSG = await ctx.send(embed=embed)
    
    await MSG.add_reaction("🕓")
    await MSG.add_reaction("👊")
    await MSG.add_reaction("🍷")
    await MSG.add_reaction("❌")

    # the main loop
    playing = True
    while playing:
        # waits for the reaction to be added
        try:
            if player[turn]["bot"]:
                reaction = "🍷"
                if player[turn]["heals"] == 0 or (player[turn]["health"] > 59 or (player[turn]["health"] > 25 and randint(1,4) > 1) or randint(1,2) == 2):
                    reaction = "👊"

                user = get(ctx.guild.members, id=player[turn]["id"])
                await asyncio.sleep(3.5)
            else:
                reaction, user = await client.wait_for("reaction_add", timeout=60, check=check)

            if reaction:
                if type(reaction) != str:
                    reaction = str(reaction.emoji)
                
                # flee (aka quit the game)
                if reaction == "❌":
                    await MSG.delete()
                    await ctx.send(player[turn]["name"] + " fled!\nGG " + player[turnt]["name"] + "!!!")
                    return

                # punch
                # more energy makes the attack stronger but attacking will half your energy
                elif reaction == "👊":
                    num = randint((player[turn]["energy"]*5)-player[turn]["energy"], (player[turn]["energy"]*5)+player[turn]["energy"])
                    enum = math.ceil(player[turn]["energy"] / 2)
                    action = "{name1} hit {name2}!".format(name1=player[turn]["name"] , name2=player[turnt]["name"]), "{name2} lost **{num} health**!\n{name1} lost **{enum} energy**!".format(name1=player[turn]["name"], name2=player[turnt]["name"], num=num, enum=enum)

                    player[turn]["energy"] -= enum

                    player[turnt]["health"] -= num
                    player[turnt]["health"] = clamp(player[turnt]["health"], 0, maxhealth)

                # heal
                elif reaction == "🍷":
                    player[turn]["heals"] -= 1

                    num = 50
                    if player[turn]["heals"] == 0:
                        action = "{name} drank a health potion! That was their last...".format(name=player[turn]["name"]), "{name} gained **{num} health**!".format(name=player[turn]["name"], num=num)
                    else:
                        action = "{name} drank a health potion!".format(name=player[turn]["name"]), "{name} gained **{num} health**!".format(name=player[turn]["name"], num=num)

                    player[turn]["health"] += num
                    player[turn]["health"] = clamp(player[turn]["health"], 0, maxhealth)

                # wait
                elif reaction == "🕓":
                    action = "{name} decided to wait.!".format(name=player[turn]["name"]), "{name} gained **1 energy**!".format(name=player[turn]["name"])

                    player[turn]["energy"] += 1
                    player[turn]["energy"] = clamp(player[turn]["energy"], 0, menergy)

                # if it's a bot don't remove reaction
                if not player[turn]["bot"]:
                    await MSG.remove_reaction(reaction, user)

                # if enemy health at 0, you win!
                if player[turnt]["health"] == 0:
                    win = turn
                    playing = False

                # swap turn
                oldturn = turn
                turn = turnt
                turnt = oldturn

                # gain energy
                player[turn]["energy"] += 1
                player[turn]["energy"] = clamp(player[turn]["energy"], 0, menergy)

                # update embed
                embed = getFightEmbed(ctx, action)
                await MSG.edit(embed=embed)

        # if no reaction is added in a miniue, it's a draw
        except asyncio.TimeoutError:
            win = "timeout"
            playing = False
            break

    # victory message
    await MSG.delete()
    if win == "timeout":
        await ctx.send("Timeout.")
    else:
        await ctx.send("GG " + player[win]["name"] + "!!!")

COMMANDS.append(["General", "clone", "Make someone say something stupid lol.", False])
@client.command()
async def clone(ctx, member:discord.User=None, *, message:str=None):
    if member == None or message == None:
        await ctx.send("You need to give a member id and message.")
        return
		
    webhook = await ctx.channel.create_webhook(name=member.name)
    await webhook.send(message, username=member.name + " (fake)", avatar_url=member.avatar_url)
    await webhook.delete()

#############
### TOKEN ###
#############

# hAH, you thought i'd have it public
client.run(os.environ["DISCORD_TOKEN"])
