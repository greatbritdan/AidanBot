from discord import Embed, Color
import datetime, math

# embeds
def getEmbed(title, content, color, fields):
	emb = Embed(title=title, description=content, color=color)
	if fields:
		for f in fields:
			inline = True if len(f) > 2 else False
			emb.add_field(name=f[0], value=f[1], inline=inline)
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
def getErrorEmbed(client, error="ha"):
	emb = getComEmbed(None, client, "Oh noes! AidanBot ran into an error:", f"```{error}```", Color.from_rgb(220, 29, 37))
	emb.remove_footer()
	return emb
def getComErrorEmbed(ctx, client, error="ha"):
	emb = getComEmbed(None, client, f"Oh noes! AidanBot ran into an error while prossesing {ctx.command}:", f"```{error}```", Color.from_rgb(220, 29, 37))
	emb.remove_footer()
	return emb
def getCheckErrorEmbed(ctx, client, error="ha"):
	emb = getComEmbed(None, client, f"Oh noes! One or more checks failed while prossesing {ctx.command}:", f"```{error}```", Color.from_rgb(120, 29, 37))
	emb.remove_footer()
	return emb

async def SendDM(client, title, description):
	aidan = await client.fetch_user(384439774972215296) # is me :]
	emb = getComEmbed(None, client, title, description, Color.from_rgb(70, 29, 37))
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
