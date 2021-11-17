import discord
from discord.utils import get
import datetime
import math

thelist = {"1": "1", "2": "2", "3": "3", "4": "4", "5": "5", "6": "6", "7": "7", "8": "8", "9": "9", "0": "0", "a": "11", "b": "12", "c": "13", "d": "14", "e": "15", "f": "16", "g": "17", "h": "18", "i": "19", "j": "20", "k": "21", "l": "22", "m": "23", "n": "24", "o": "25", "p": "26", "q": "27", "r": "28", "s": "29", "t": "30", "u": "31", "v": "32", "w": "33", "x": "34", "y": "35", "z": "36", " ": "37", ".": "38", ",": "39", ":": "40", ";": "41", "'": "42", "/": "43", "-": "44", "+": "45", "$": "46", "%": "46"}
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

# make an embed and send it back
def getEmbed(ctx, command, title=False, description=False, color=False, image=False, thumb=False, footer=False):
	if color:
		col = color
	else:
		col = discord.Color.from_rgb(20, 29, 37)
	emb = discord.Embed(title=title, description=description, color=col)
	if image:
		emb.set_image(url=image)
	if thumb:
		emb.set_thumbnail(url=thumb)
	if footer:
		emb.set_footer(text=footer)
	elif ctx:
		emb.set_footer(text=f"Requested by {ctx.author} in #{ctx.channel}")
	else:
		emb.set_footer(text="Requested by AidanBot")
	if ctx.bot.ISBETA:
		emb.set_author(name="AidanBetaBot > " + command, icon_url="https://cdn.discordapp.com/attachments/879754347200786503/879754420936654908/aidanbetabot.png")
	else:
		emb.set_author(name="AidanBot > " + command, icon_url="https://cdn.discordapp.com/attachments/879754347200786503/879754415068819506/aidanbot.png")
	emb.timestamp = datetime.datetime.utcnow()
	return emb

# add a feild to an embed
def addField(emb, fname, fvalue, fline=False):
	emb.add_field(name=fname, value=fvalue, inline=fline)
	return emb

# for when a command fails
async def Error(ctx, client, error):
	emb = getEmbed(ctx, "Error", "AidanBot Encountered an error and your command was cancelled.", error, discord.Color.from_rgb(220, 29, 37))
	await ctx.send(embed=emb)

# for command cooldown
async def CooldownError(ctx, client, error):
	emb = getEmbed(ctx, "Cooldown", error, "", discord.Color.from_rgb(145, 29, 37))
	await ctx.send(embed=emb)

# send me a message
async def sendToWorkshop(ctx, client, title, description):
	guild = get(client.guilds, id=879063875469860874)
	channel = get(guild.text_channels, id=882997912102137896)

	footer = "Not Via Guild"
	if ctx:
		footer = f"User: {ctx.author}"
	emb = getEmbed(ctx, "System Message", title, description, discord.Color.from_rgb(70, 29, 37), False, False, footer)
	await channel.send(embed=emb)

# generats a bar using emotes
def getBar(value, maxvalue, size, hashalf=False):
	valueperseg = maxvalue / size
	segsfilled = math.ceil(value / valueperseg)
	ishalf = False
	if hashalf and math.ceil((value - (valueperseg/2)) / valueperseg) < segsfilled:
		ishalf = True

	barmotes = {
		"left": {
			"full":"<:left_full:862331445526921287>",
			"half":"<:left_half:862331445700067328>",
			"fulls":"<:left_fullsingle:862331445750005770>",
			"empty":"<:left_empty:862331445720121365>"
		},
		"mid": {
			"full":"<:middle_full:862331445300428821>",
			"half":"<:middle_half:862331445845688340>",
			"fulls":"<:middle_fullsingle:862331445703737364>",
			"empty":"<:middle_empty:862331445813313606>"
		},
		"right": {
			"full":"<:right_full:862331445657468939>",
			"half":"<:right_half:862331445702819880>",
			"fulls":"<:right_full:862331445657468939>",
			"empty":"<:right_empty:862331445313273857>"
		}
	}
	
	bar = ""
	for i in range(1, size+1):
		place = "right"
		if i == 1:
			place = "left"
		elif i < size:
			place = "mid"

		if i < segsfilled:
			bar += barmotes[place]["full"]
		elif i == segsfilled:
			if ishalf:
				bar += barmotes[place]["half"]
			else:
				bar += barmotes[place]["fulls"]
		else:
			bar += barmotes[place]["empty"]
	return bar

# oh boy #
def strtolist(inp):
	table = []
	index = -1
	cur = ""
	for letter in inp:
		if letter == "{":
			table.append({})
			index += 1
		elif letter == "," or letter == "}":
			if cur != "":
				i = cur.split("=")
				name, val = i[0], i[1]

				if val.lower() == "true":
					table[index][name] = True
				elif val.lower() == "false":
					table[index][name] = False
				else:
					try:
						table[index][name] = int(val)
					except:
						table[index][name] = val
				cur = ""
		else:
			cur = cur + letter
	return table

def listtostr(inp):
	test = ""
	for list in inp:
		test += "{"
		for name in list:
			val = str(list[name])
			test = test + name + "=" + val + ","
		test = test[:-1] + "},"
	test = test[:-1]
	return test