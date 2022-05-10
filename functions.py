from discord import Embed, Color
import datetime, math

# embeds
def getEmbed(title, content, color, fields):
	emb = Embed(title=title, description=content, color=color)
	if fields:
		for f in fields:
			emb.add_field(name=f[0], value=f[1], inline=False)
	return emb

def getComEmbed(ctx=None, client=None, title=Embed.Empty, content=Embed.Empty, color=Color.from_rgb(20, 29, 37), fields=None):
	emb = getEmbed(title, content, color, fields)
	emb.timestamp = datetime.datetime.utcnow()
	emb.set_author(name=f"{client.name} > Version: {client.version}", icon_url=client.pfp)
	if ctx:
		emb.set_footer(text=f"Requested by {str(ctx.author)}")
	else:
		emb.set_footer(text=f"Requested by a user")
	return emb

def getErrorEmbed(ctx, client, error="Default error"):
	emb = getComEmbed(ctx, client, "AidanBot ran into and uh-oh error:", f"```{error}```", Color.from_rgb(220, 29, 37))
	return emb

async def SendDM(client, title, description):
	aidan = await client.fetch_user(384439774972215296) # is me :]
	emb = getComEmbed(None, client, "System Message", title, description, Color.from_rgb(70, 29, 37))
	await aidan.send(embed=emb)

# others
def getIntFromText(txt):
	theNEWlist = "1234567890abcdefghijklmnopqrstuvwxyz .,:;/-+`%$"
	sed = ""
	for letter in txt:
		ind = theNEWlist.find(letter)
		if ind:
			sed += str(ind+1)
		else:
			sed += "46"
	return int(sed)

async def userPostedRecently(channel, user, limit):
	async for msg in channel.history(limit=limit):
		if msg.author == user:
			return True
	return False

def getBar(value, maxvalue, size, hashalf=False):
	valueperseg = maxvalue / size
	segsfilled = math.ceil(value / valueperseg)
	ishalf = False
	if hashalf and math.ceil((value - (valueperseg/2)) / valueperseg) < segsfilled:
		ishalf = True

	barmotes = {
		"left": {"full":"<:left_full:862331445526921287>", "half":"<:left_half:862331445700067328>", "fulls":"<:left_fullsingle:862331445750005770>", "empty":"<:left_empty:862331445720121365>"},
		"mid": {"full":"<:middle_full:862331445300428821>", "half":"<:middle_half:862331445845688340>", "fulls":"<:middle_fullsingle:862331445703737364>", "empty":"<:middle_empty:862331445813313606>"},
		"right": {"full":"<:right_full:862331445657468939>", "half":"<:right_half:862331445702819880>", "fulls":"<:right_full:862331445657468939>", "empty":"<:right_empty:862331445313273857>"}
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

def dateToStr(day, month):
	months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
	m, d = months[month-1], day
	if day == 1 or day == 21 or day == 31:
		d = f"{d}st"
	elif day == 2 or day == 22:
		d = f"{d}nd"
	elif day == 3 or day == 23:
		d = f"{d}rd"
	else:
		d = f"{d}th"
	return d + " of " + m
