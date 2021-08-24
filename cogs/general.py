import discord
from discord.ext import commands

from random import seed
from random import randint

from functions import is_beta, add_command, getEmbed, Error, addField, getIntFromText, userHasPermission

class GeneralCog(commands.Cog):
	def __init__(self, client):
		self.client = client

	add_command({
		"cog": "general", "category": "General",
		"name": "echo", "description": "Bot says what is passed into it.",
		"arguments": [
			["text", "The text he will say.", "string", False]
		],
		"level": False
	})
	@commands.command()
	async def echo(self, ctx, *, text:str="sample text"):
		await ctx.message.delete()
		await ctx.send(text)

	add_command({
		"cog": "general", "category": "General",
		"name": "reply", "description": "Replys to a message with what is passed into it.",
		"arguments": [
			["message id", "ID of the message it is replying to.", "integer", True],
			["text", "The text he will say.", "string", False]
		],
		"level": False
	})
	@commands.command()
	async def reply(self, ctx, mid:int=None, *, text:str="sample text"):
		if mid == None:
			await Error(ctx, self.client, "Missing un-optional argument for command.")
			return

		MSG = await ctx.channel.fetch_message(mid)
		await ctx.message.delete()
		await MSG.reply(text, mention_author=False)

	add_command({
		"cog": "general", "category": "General",
		"name": "react", "description": "Reacts to latest message.",
		"arguments": [
			["emoji", "The emoji he will react with.", "string", False]
		],
		"level": False
	})
	@commands.command()
	async def react(self, ctx, reaction:str="👋"):
		second = False
		async for message in ctx.channel.history(limit=2):
			if second == False:
				second == True

		await message.add_reaction(reaction)
		await ctx.message.delete()

	add_command({
		"cog": "general", "category": "General",
		"name": "rate", "description": "Rates what you pass into it.",
		"arguments": [
			["thing", "The thing he will rate.", "string", True]
		],
		"level": False
	})
	@commands.command()
	async def rate(self, ctx, *, thing=None):
		if thing.lower() == "me":
			thing = ctx.author.name
		elif thing.lower() == "this server":
			thing = ctx.guild.name

		thing = thing.replace("your", "my")

		seed(getIntFromText(thing.lower()))

		responces = [
			["{0} is worse than anything i have ever rated.", [-10, -10]],
			["{0} is just awful, holy crap!", [-1, 0]],
			["{0} goes right into F tier.", [0, 2]],
			["{0} is really bad.", [0, 2]],
			["I have no opinion on {0}.", [2, 2]],
			["{0}? i can't say that with a straight mout-, uhh hole?", [1, 3]],
			["{0} is alright, but could be better.", [3, 5]],
			["{0} is pretty good!", [4, 6]],
			["{0} is neat!", [4, 6]],
			["{0} is great. Not the best tho.", [5, 8]],
			["Never seen it, but I like the sound of {0}!", [5, 8]],
			["{0} is amazing!", [7, 9]],
			["{0} is the best thing, by far.", [10, 10]],
			["I AM GOD", [11, 11]],
			["HE SUCKS SO GOD DAMN MUCH!!!!!", [-3888292929929922, -3888292929929922]],
			["How... dare you...", [-999999999999999999999999999999999999999999, -999999999999999999999999999999999999999999]]
		]

		# if it's aidanbot/aidanbetabot or aidan, respond differently
		index = randint(0, 12)
		thung = thing.lower()
		if is_beta():
			if thung == "aidanbetabot" or thung == "you":
				index = 13
			elif thung == "aidanbot":
				index = 14
		else:
			if thung == "aidanbot" or thung == "you":
				index = 13
			elif thung == "aidanbetabot":
				index = 14

		if "cursed" in thung:
			index = 12

		if randint(0,99) == 99:
			index = 15

		txt = responces[index][0]
		rating = randint(responces[index][1][0], responces[index][1][1])

		emb = getEmbed(ctx, "Rate", txt.format(thing), "")
		emb = addField(emb, "Score", "**{0}/10**".format(rating))
		await ctx.reply(embed=emb, mention_author=False)

	add_command({
		"cog": "general", "category": "General",
		"name": "ask", "description": "Answers your deepest questions.",
		"arguments": [
			["question", "The question he will answer.", "string", True]
		],
		"level": False
	})
	@commands.command()
	async def ask(self, ctx, *, question:str=None):
		seed(getIntFromText(question.lower()))

		if question == None:
			await Error(ctx, self.client, "Missing un-optional argument for command.")
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

		emb = getEmbed(ctx, "Ask", start_txt + end_txt, "")
		await ctx.reply(embed=emb, mention_author=False)

	add_command({
		"cog": "general", "category": "General",
		"name": "decide", "description": "Picks between the choices given.",
		"arguments": [
			["choice 1", "The first choice.", "string", True],
			["choice 2", "The second choice.", "string", False],
			["choice ...", "The ... choice.", "string", False]
		],
		"level": False
	})
	@commands.command()
	async def decide(self, ctx, *, decisions=None):
		if decisions == None:
			await Error(ctx, self.client, "Missing un-optional argument for command.")
			return

		decisions = decisions.split(" ")
		emb = getEmbed(ctx, "Decide", "I choose... {0}".format(decisions[randint(0, len(decisions)-1)]), "")
		await ctx.reply(embed=emb, mention_author=False)

	add_command({
		"cog": "general", "category": "General",
		"name": "clone", "description": "Make someone say something.",
		"arguments": [
			["user", "The user.", "name/id/mention", True],
			["message", "The message they will send.", "string", True]
		],
		"level": False
	})
	@commands.command()
	async def clone(self, ctx, member:discord.User=None, *, message:str=None):
		if member == None or message == None:
			await Error(ctx, self.client, "Missing un-optional argument for command.")
			return
		
		webhook = await ctx.channel.create_webhook(name=member.name)
		await webhook.send(message, username=member.name + " (fake)", avatar_url=member.avatar_url)
		await webhook.delete()

	add_command({
		"cog": "general", "category": "General",
		"name": "role", "description": "Add or remove any role that begins with [r].",
		"arguments": [
			["name", "The name of the role (or close to it).", "string", True]
		],
		"level": False
	})
	@commands.command()
	async def role(self, ctx, *, name=None):
		if name == None:
			await Error(ctx, self.client, "Missing un-optional argument for command.")
			return

		r = None
		for role in ctx.guild.roles:
			if name.lower() in role.name.lower():
				r = role

		if r == None:
			await ctx.send("Try again, i couldn't find this role.")
			return

		if userHasPermission(ctx.author, "manage_roles") or r.name.startswith("[r]"):
			if r == ctx.author.top_role:
				await ctx.send(f"You can't remove your top role")
				return
			
			if r in ctx.author.roles:
				await ctx.author.remove_roles(r)
				await ctx.send(f"Removed {r.name}")
			else:
				await ctx.author.add_roles(r)
				await ctx.send(f"Added {r.name}")
		else:
			await ctx.send(f"{r.name} is not a role that can be added by anyone")

def setup(client):
  client.add_cog(GeneralCog(client))