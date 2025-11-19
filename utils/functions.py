import discord
from discord.ext import commands
from discord.utils import get
from discord import Embed, Color

#from aidanbot import AidanBot

import traceback, datetime, math

# embeds
def getEmbed(title, content, color, fields):
	emb = Embed(title=title, description=content, color=color)
	if fields:
		for f in fields:
			inline = True if len(f) > 2 else False
			emb.add_field(name=f[0], value=f[1], inline=inline)
	return emb

def getComEmbed(client:commands.Bot=None, title=None, content=None, color=False, command=None, footer=None, fields=None):
	if color and isinstance(color, str) and color[0] == "#":
		color = Color.from_str(color)
	elif color and isinstance(color, discord.Color):
		color = color # COLOR IS COLOR
	elif client:
		if color == "error":
			color = Color.from_str(client.embedcolorerror)
		else:
			color = Color.from_str(client.embedcolor)

	emb = getEmbed(title, content, color, fields)
	if command:
		emb.set_author(name=f"{client.name} > {command}", icon_url=client.pfp)
	else:
		emb.set_author(name=f"{client.name}", icon_url=client.pfp)
	if footer:
		emb.set_footer(text=f"{footer} • {client.version}")
	else:
		emb.set_footer(text=f"{client.version}")
	return emb
	
def getCheckEmbed(client:commands.Bot, details):
	emb = getComEmbed(client, content=f"```{details}```", color="error", command="Checks failed!")
	emb.remove_footer()
	return emb

def getErrorEmbed(client:commands.Bot, error="error not passed"):
	emb = getComEmbed(client, content=f"```{error}```", color="error", command=f"{client.name} error'd!")
	emb.remove_footer()
	return emb

async def sendComError(client:commands.Bot, ctx:commands.Context, error):
	guild = get(client.guilds, id=879063875469860874)
	channel = get(guild.channels, name="error-logs")
	err = traceback.format_exception_only(error)[0]
	trac = '\n'.join(traceback.format_exception(error))
	await channel.send(embed=getComEmbed(client, f"Command Error received [/{ctx.command.qualified_name}]:", f"**Error:** `{err}`\n**Traceback:** ```\n{trac}\n```", color="error", command=f"{client.name} error'd!"))

async def sendError(client:commands.Bot, event, error):
	guild = get(client.guilds, id=879063875469860874)
	channel = get(guild.channels, name="error-logs")
	err = traceback.format_exception_only(error[1])[0]
	trac = '\n'.join(traceback.format_exception(error[1]))
	await channel.send(embed=getComEmbed(client, f"Event Error received [{event}]:", f"**Error:** `{err}`\n**Traceback:** ```\n{trac}\n```", color="error", command=f"{client.name} error'd!"))

async def sendCustomError(client:commands.Bot, event, error):
	guild = get(client.guilds, id=879063875469860874)
	channel = get(guild.channels, name="error-logs")
	await channel.send(embed=getComEmbed(client, f"Custom Error received [{event}]:", f"**Error:**\n```{error}```", color="error", command=f"{client.name} error'd!"))

async def userPostedRecently(channel:discord.TextChannel, user:discord.Member, limit):
	async for msg in channel.history(limit=limit):
		if msg.author == user:
			return True
	return False

def getBar(value, maxvalue, size, hashalf=False, color="blue"):
	valueperseg = maxvalue / size
	segsfilled = math.ceil(value / valueperseg)
	ishalf = False
	if hashalf and math.ceil((value - (valueperseg/2)) / valueperseg) < segsfilled:
		ishalf = True

	barmotes = {
		"left": {
			"empty": "<:left_empty:974754778376724600>",
			"blue": ["<:left_blue_full:974754804859543602>", "<:left_blue_half:974754805094428732>", "<:left_blue_fullstop:974754805006352464>"],
			"red": ["<:left_red_full:974754858697633833>", "<:left_red_half:974754858735403028>", "<:left_red_fullstop:974754859003817986>"]
		},
		"mid": {
			"empty": "<:mid_empty:974754778460602428>",
			"blue": ["<:mid_blue_full:974754804939259974>", "<:mid_blue_half:974754804964413460>", "<:mid_blue_fullstop:974754804956004432>"],
			"red": ["<:mid_red_full:974754858752176229>", "<:mid_red_half:974754858806702080>", "<:mid_red_fullstop:974754858555043914>"]
		},
		"right": {
			"empty": "<:right_empty:974754778217336873>",
			"blue": ["<:right_blue_full:974754804951822376>", "<:right_blue_half:974754804565958677>", "<:right_blue_full:974754804951822376>"],
			"red": ["<:right_red_full:974754858894782524>", "<:right_red_half:974754858865422376>", "<:right_red_full:974754858894782524>"]
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
			bar += barmotes[place][color][0]
		elif i == segsfilled:
			if ishalf:
				bar += barmotes[place][color][1]
			else:
				bar += barmotes[place][color][2]
		else:
			bar += barmotes[place]["empty"]
	return bar

def dateToStr(day, month):
	months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December", "Out-Of-Rangeary"]

	m = month
	try:
		m = months[month-1]
	except IndexError:
		m = months[12]

	d = day
	if day == 1 or day == 21 or day == 31:
		d = f"{d}st"
	elif day == 2 or day == 22:
		d = f"{d}nd"
	elif day == 3 or day == 23:
		d = f"{d}rd"
	else:
		d = f"{d}th"
	return d + " of " + m