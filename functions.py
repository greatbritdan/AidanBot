from discord import Embed, Color

import datetime, math

# EMBED STUFF #
def getEmbed(title, desc, col, fields):
	emb = Embed(title=title, description=desc, color=col)
	emb.timestamp = datetime.datetime.utcnow()
	for f in fields:
		emb.add_field(name=f[0], value=f[1], inline=False)
	return emb

def getComEmbed(ctx=None, client=None, command="N/A", title=Embed.Empty, desc=Embed.Empty, col=Color.from_rgb(20, 29, 37), fields=[]):
	emb = getEmbed(title=title, desc=desc, col=col, fields=fields)
	if ctx:
		emb.set_footer(text=f"Requested by {ctx.author} in #{ctx.channel}")
	else:
		emb.set_footer(text=f"(no ctx provided)")
	emb.set_author(name=f"{client.name} > {command}", icon_url=client.pfp)
	return emb
def getComEmbedSimple(title=Embed.Empty, desc=Embed.Empty):
	emb = getEmbed(title=title, desc=desc, col=Color.from_rgb(20, 29, 37), fields=[])
	return emb

async def ClientError(ctx, client, error): # not used for now
    await ctx.send(embed=getComEmbed(ctx, client, "Client Error", "Looks like something's wrong with AidanBot's client. Please try again. If you're having trouble figuring out what it is, see error.", error, Color.from_rgb(220, 29, 37)))
async def ComError(ctx, client, error):
    await ctx.send(embed=getComEmbed(ctx, client, "Error", "AidanBot has ran into an error. Please try your command again. See error for more info. Contact the bot owner if this error can't be fixed in any way whatsoever that you tried.", f"```{error}```", Color.from_rgb(220, 29, 37)))
async def ExistError(ctx, client):
    await ctx.send(embed=getComEmbed(ctx, client, "Error", "This command doesn't seem to exist, make sure you typed it right.", "", Color.from_rgb(220, 29, 37)))
async def ParamError(ctx, client, error):
    await ctx.send(embed=getComEmbed(ctx, client, "Parameter Error", "AidanBot has encountered an error and your command was cancelled. See error for more info. This error occurred because either a missing parameter or argument was detected: ", f"Missing required argument for {client.prefix}{ctx.command}: **{error.param}**\n```{client.prefix}{ctx.command} {ctx.command.signature}```", Color.from_rgb(145, 29, 37)))
async def CooldownError(ctx, client, error):
	await ctx.send(embed=getComEmbed(ctx, client, "Cooldown Error", "Command on cooldown!! ```Try again in {:.2f} seconds.```".format(error.retry_after), "", Color.from_rgb(145, 29, 37)))

async def SendDM(client, title, description):
	aidan = await client.fetch_user(384439774972215296)
	emb = await getComEmbed(None, client, "System Message", title, description, Color.from_rgb(70, 29, 37))
	await aidan.send(embed=emb)

# OTHER #

def getIntFromText(txt):
	theNEWlist = "1234567890abcdefghijklmnopqrstuvwxyz .,:;/-+ `"
	sed = ""
	for letter in txt:
		if letter == "$" or letter == "%":
			sed += "46"
		else:
			ind = theNEWlist.find(letter)
			if ind:
				sed += str(ind+1)
			else:
				sed += "47"
	return int(sed)

# generats a bar using emotes
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

def argstodic(args, typdic):
	dic = {}
	# create the DIC
	for arg in args:
		split = arg.split('=', 1)
		if len(split) == 2:
			dic[split[0]] = split[1]

	# convert types
	for index in typdic:
		if index in dic:
			if typdic[index][0] == "int":
				try:
					dic[index] = int(dic[index])
				except:
					print("int conversion error!")
					dic[index] = 0
			if typdic[index][0] == "bool":
				if typdic[index] == "true":
					typdic[index] = True
				elif typdic[index] == "false":
					typdic[index] = False
				else:
					typdic[index] = None
		else:
			dic[index] = typdic[index][1]

	# return the DIC
	return dic