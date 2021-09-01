import discord
from discord.utils import get

import datetime
import copy
import math

PREFIX = "$"
VERSION = "Beta V3"
COMMANDS = []

def is_beta():
	return (PREFIX == "%")

def get_prefix():
	return PREFIX
def get_version():
	return VERSION
def get_commands():
	return COMMANDS

def add_command(com):
	global COMMANDS
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
	"/": "43", "-": "44", "+": "45", "$": "46", "%": "46"
}

def clamp(n, minn, maxn):
	return max(min(maxn, n), minn)

def getIntFromText(txt):
	sed = ""
	for letter in txt:
		if letter in thelist:
			sed = sed + thelist[letter]
		else:
			sed = sed + "47"

	return (int(sed))

def userHasPermission(member, permission):
	for perm in member.guild_permissions:
		if str(perm[0]) == permission and perm[1] == True:
			return True
	return False

async def SEND_SYSTEM_MESSAGE(ctx, client, title, description):
	guild = get(client.guilds, id=879063875469860874)
	channel = get(guild.text_channels, name="system-messages")

	emb = getSystemEmbed(ctx, title, description)
	await channel.send(embed=emb)

### EMBEDS ###

# make an embed and send it back
def getEmbed(ctx, command, title=False, description=False, color=False, thumb=False):
	if color:
		col = color
	else:
		col = discord.Color.from_rgb(20, 29, 37)

	emb = discord.Embed(title=title, description=description, color=col)
	if thumb:
		emb.set_thumbnail(url=thumb)
	emb.set_footer(text="Requested by {0} in #{1}".format(ctx.author, ctx.channel))
	if is_beta():
		emb.set_author(name="AidanBetaBot > " + command, icon_url="https://cdn.discordapp.com/attachments/879754347200786503/879754420936654908/aidanbetabot.png")
	else:
		emb.set_author(name="AidanBot > " + command, icon_url="https://cdn.discordapp.com/attachments/879754347200786503/879754415068819506/aidanbot.png")
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
		emb.set_footer(text=f"User: {ctx.author}")
	else:
		emb.set_footer(text="Not Via Guild")
	if is_beta():
		emb.set_author(name="AidanBetaBot > System Message", icon_url="https://cdn.discordapp.com/attachments/879754347200786503/879754420936654908/aidanbetabot.png")
	else:
		emb.set_author(name="AidanBot > System Message", icon_url="https://cdn.discordapp.com/attachments/879754347200786503/879754415068819506/aidanbot.png")
	emb.timestamp = datetime.datetime.utcnow()
	return emb

# for when a command fails
async def Error(ctx, client, error, send=None):
	emb = discord.Embed(title="AidanBot Encountered an error and your command was cancelled.", description=error, color=discord.Color.from_rgb(220, 29, 37))
	emb.set_footer(text="Requested by {0} in #{1}".format(ctx.author, ctx.channel))
	if is_beta():
		emb.set_author(name="AidanBetaBot > Error", icon_url="https://cdn.discordapp.com/attachments/879754347200786503/879754420936654908/aidanbetabot.png")
	else:
		emb.set_author(name="AidanBot > Error", icon_url="https://cdn.discordapp.com/attachments/879754347200786503/879754415068819506/aidanbot.png")
	emb.timestamp = datetime.datetime.utcnow()
	if send:
		await SEND_SYSTEM_MESSAGE(ctx, client, "Someone Broke AidanBot lol.", error)
	await ctx.send(embed=emb)

def getBar(value, maxvalue, size, hashalf=False):
	valueperseg = maxvalue / size
	segsfilled = math.ceil(value / valueperseg)
	ishalf = False
	if hashalf and math.ceil((value - (valueperseg/2)) / valueperseg) < segsfilled:
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
