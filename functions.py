import discord
from discord.utils import get

import datetime
import copy

PREFIX = "$"
VERSION = "Beta V2.9"
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
def get_commands():
	return COMMANDS
def add_command(com):
	COMMANDS.append(com)

def clear_command_type(typ):
	global COMMANDS
	newcommands = []
	for com in COMMANDS:
		if com[0] != typ:
			newcommands.append(com)
	COMMANDS = copy.deepcopy(newcommands)

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

### SAVE AND LOAD ###

async def GETMSG(ctx, client):
	guild = client.get_guild(879063875469860874)
	channel = get(guild.text_channels, name=str(ctx.guild.id))
	if channel == None:
		await ctx.send(f"You need to run {PREFIX}setup first!")
		return False

	message = await channel.fetch_message(channel.last_message_id)
	if message == None:
		return False

	return message

async def CREATEDATA(ctx, client):
	guild = client.get_guild(879063875469860874)
	channel = get(guild.text_channels, name=str(ctx.guild.id))
	if channel:
		await ctx.send("Your server is already setup!")
		return False
	
	category = get(guild.categories, name="Guilds")
	channel = await guild.create_text_channel(str(ctx.guild.id), topic=f"AKA {ctx.guild.name}", category=category)

	defaults = get_defaults()
	data = []
	for key in defaults:
		data.append(key + "=" + defaults[key])

	sep = "\n"
	txt = sep.join(data)

	await channel.send(txt)
	return True

async def DELETEDATA(guildid, ctx=None, client=None):
	guild = client.get_guild(879063875469860874)
	channel = get(guild.text_channels, name=str(guildid))
	if channel == None:
		if ctx:
			await ctx.send("Your server has no server data!")
			return False
	
	await channel.delete()
	return True

async def PARCEDATA(ctx, client, action, name=None, val=None):
	message = await GETMSG(ctx, client)
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
	if action != "list":
		if name not in data:
			return False

	# gets all values
	if action == "list":
		retun = data

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

async def SEND_SYSTEM_MESSAGE(ctx, client, title, description):
	guild = get(client.guilds, id=760987756985843733)
	channel = get(guild.text_channels, id=875312386674941973)

	emb = getSystemEmbed(ctx, title, description)
	await channel.send(embed=emb)

### EMBEDS ###

# make an embed and send it back
def getEmbed(ctx, command, title=False, description=False, image=False, color=False, thumb=False):
	if color == "red":
		col = discord.Color.from_rgb(220, 29, 37)
	elif color:
		col = color
	else:
		col = discord.Color.from_rgb(20, 29, 37)

	emb = discord.Embed(title=title, description=description, color=col)
	if image:
		emb.set_image(url=image)
	if thumb:
		emb.set_thumbnail(url=thumb)

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
async def Error(ctx, client, error, send=None):
	emb = discord.Embed(title="AidanBot Encountered an error and your command was cancelled.", description=error, color=discord.Color.from_rgb(220, 29, 37))
	emb.set_footer(text="Requested by {0} in #{1}".format(ctx.author, ctx.channel))
	emb.set_author(name="AidanBot > Error", icon_url="https://cdn.discordapp.com/attachments/806147106054078482/861645806851719188/aidanbot.png")
	emb.timestamp = datetime.datetime.utcnow()

	if send:
		await SEND_SYSTEM_MESSAGE(ctx, client, "Someone Broke AidanBot lol.", error)

	await ctx.send(embed=emb)
