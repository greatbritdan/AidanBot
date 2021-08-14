import discord
from discord.ext import commands
from discord.utils import get

import os
import datetime
import copy

PREFIX = "%"
VERSION = "Beta V2"
COMMANDS = []
DEFAULTS = {
	"delete_invites": "false",
	"invite_allow_channel": "false"
}

def get_prefix():
	return PREFIX

def get_version():
	return VERSION

def get_defaults():
	return DEFAULTS

def add_command(com):
	COMMANDS.append(com)

def get_commands():
	return COMMANDS

def clear_command_type(typ):
	global COMMANDS
	newcommands = []
	for com in COMMANDS:
		if com[0] != typ:
			newcommands.append(com)
	COMMANDS = copy.deepcopy(newcommands)

client = commands.Bot(command_prefix=PREFIX, case_insensitive=True, help_command=None)

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
	if message.author.bot == True:
		return

	if not message.guild:
		await message.channel.send("Not available outside of guilds (servers)")
		return

	if "discord.gg" in message.content.lower():
		delete_invites = await PARCEDATA(message, "getstatic", "delete_invites")
		if delete_invites and userHasPermission(message.author, "kick_members") == False:
			invite_allow_channel = await PARCEDATA(message, "getstatic", "invite_allow_channel")
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
	await SEND_SYSTEM_MESSAGE(None, "SOMEONE DID WHAT?!?!", f"Added to {guild.name}!")

@client.event
async def on_guild_remove(guild):
	await SEND_SYSTEM_MESSAGE(None, "SOMEONE DID WHAT?!?!", f"Removed from {guild.name}!")

@client.event
async def on_command_error(ctx, error):
	err = "I seem to have ran into an error, It's best to let Aidan know."
	if isinstance(error, commands.BotMissingPermissions):
		err = err + "\n\nError: Bot Missing Permissions!"
	elif isinstance(error, commands.MissingPermissions):
		err = err + "\n\nError: User Missing Permissions!"
	err = err + f"\n\nFull Error: {error}"

	await Error(ctx, err, True)

############
### COGS ###
############

@client.command()
async def load(ctx, extension):
	client.load_extension(f'cogs.{extension}')
	await ctx.send('```{} loaded!```'.format(extension))

@client.command()
async def unload(ctx, extension):
	client.unload_extension(f'cogs.{extension}')
	clear_command_type(extension)
	await ctx.send('```{} unloaded!```'.format(extension))

@client.command()
async def reload(ctx, extension):
	client.unload_extension(f'cogs.{extension}')
	clear_command_type(extension)
	client.load_extension(f'cogs.{extension}')
	await ctx.send('```{} reloaded!```'.format(extension))

#####################
### SAVE AND LOAD ###
#####################

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

async def PARCEDATA(ctx, action, name, val=None):
	message = await GETMSG(ctx)
	if message == False:
		return

	messcont = message.content
	lines = messcont.splitlines()

	# get all vals from server data
	data = {}
	for var in lines:
		dat = var.split('=')
		data[dat[0]] = dat[1]

	# fill in defaults if missing any
	defaults = get_defaults()
	for key in defaults:
		if key not in data:
			data[key] = defaults[key]

	# returns false if it doesn't exist
	if name not in data:
		return False

	# gets the value and returns value
	if action == "get" or action == "getstatic":
		if data[name] == "true":
			retun = True
		elif data[name] == "false":
			retun = False
		else:
			retun = data[name]

	# sets value and returns True
	elif action == "set":
		data[name] = val
		retun = data[name]

	if action != "getstatic":
		stringdata = []
		for key in data:
			stringdata.append(key + "=" + data[key])

		sep = "\n"
		txt = sep.join(stringdata)
		
		await message.delete()
		await message.channel.send(txt)

	return retun

async def SEND_SYSTEM_MESSAGE(ctx, title, description):
	guild = get(client.guilds, id=760987756985843733)
	channel = get(guild.text_channels, id=875312386674941973)

	emb = getSystemEmbed(ctx, title, description)
	await channel.send(embed=emb)

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
	"/": "43", "-": "44", "+": "45"
}

def clamp(n, minn, maxn):
	return max(min(maxn, n), minn)

def getIntFromText(txt):
	sed = ""
	for letter in txt:
		if letter in thelist:
			sed = sed + thelist[letter]
		else:
			sed = sed + "46"

	return (int(sed))

def userHasPermission(member, permission):
	for perm in member.guild_permissions:
		if str(perm[0]) == permission and perm[1] == True:
			return True

	return False

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

# add a feild to an embed
def addField(emb, fname, fvalue, fline=False):
	emb.add_field(name=fname, value=fvalue, inline=fline)

	return emb

# make a system embed and sends it to aidans server.
def getSystemEmbed(ctx, title=False, description=False):
	emb = discord.Embed(title=title, description=description, color=discord.Color.from_rgb(70, 29, 37))

	if ctx:
		emb.set_footer(text="Guild: {0} - Channel: {1} - User: {2}".format(ctx.guild, ctx.channel, ctx.author))
	else:
		emb.set_footer(text="Not Via Guild")

	emb.set_author(name="AidanBot > System Message", icon_url="https://cdn.discordapp.com/attachments/806147106054078482/861645806851719188/aidanbot.png")
	emb.timestamp = datetime.datetime.utcnow()

	return emb

# for when a command fails
async def Error(ctx, error, send=None):
	emb = discord.Embed(title="AidanBot Encountered an error and your command was cancelled.", description=error, color=discord.Color.from_rgb(220, 29, 37))
	emb.set_footer(text="Requested by {0} in #{1}".format(ctx.author, ctx.channel))
	emb.set_author(name="AidanBot > Error", icon_url="https://cdn.discordapp.com/attachments/806147106054078482/861645806851719188/aidanbot.png")
	emb.timestamp = datetime.datetime.utcnow()

	if send:
		await SEND_SYSTEM_MESSAGE(ctx, "Someone Broke AidanBot lol.", error)

	await ctx.send(embed=emb)

############
### LOAD ###
############

for filename in os.listdir('./cogs'):
	if filename.endswith('.py'):
		client.load_extension(f'cogs.{filename[:-3]}')
		print('{} Loaded!'.format(filename[:-3]))

client.run(os.getenv('DISCORD_TOKEN'))