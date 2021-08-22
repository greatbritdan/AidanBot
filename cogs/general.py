import discord
from discord.ext import commands
from discord.utils import get

from random import seed
from random import randint

from functions import add_command, getEmbed, Error, addField, getIntFromText, userHasPermission

class GeneralCog(commands.Cog):
	def __init__(self, client):
		self.client = client

	add_command(["general", "General", "ping", "Get bot latency.", False])
	@commands.command()
	async def ping(self, ctx):
		emb = getEmbed(ctx, "Ping", "Ping Pong motherfucker!", "{0}ms".format(round(self.client.latency, 3)))
		await ctx.send(embed=emb)

	add_command(["general", "General", "echo", "Says what is passed into it.", False])
	@commands.command()
	async def echo(self, ctx, *, text:str="sample text"):
		await ctx.message.delete()
		await ctx.send(text)

	add_command(["general", "General", "react", "Reacts to latest message.", False])
	@commands.command()
	async def react(self, ctx, reaction:str="👋"):
		second = False
		async for message in ctx.channel.history(limit=2):
			if second == False:
				second == True

		await message.add_reaction(reaction)
		await ctx.message.delete()

	add_command(["general", "General", "rate", "Rates what you pass into it.", False])
	@commands.command()
	async def rate(self, ctx, *, thing:str="thing"):
		seed(getIntFromText(thing.lower()))

		responces = [
			["{0} is worse than anything i have ever rated.", [-10, -10]],
			["{0} is just awful, holy crap!", [-1, 0]],
			["{0} is really bad.", [0, 2]],
			["{0} is alright, but could be better.", [2, 5]],
			["I have no opinion on {0}.", [0, 0]],
			["{0} is pretty good!", [4, 6]],
			["{0} is great. Not the best tho.", [5, 8]],
			["{0} is amazing!", [7, 9]],
			["{0} is the best thing, by far.", [10, 10]],
			["I AM GOD", [10, 10]],
			["No comment, I am not dying today :)", [5, 5]]
		]

		# if it's aidanbot or aidan, respond differently
		index = randint(0, 9)
		if thing.lower() == "aidanbot":
			index = 9
		elif thing.lower() == "aidan":
			index = 10

		txt = responces[index][0]
		rating = randint(responces[index][1][0], responces[index][1][1])

		emb = getEmbed(ctx, "Rate", txt.format(thing), "")
		emb = addField(emb, "Score", "**{0}/10**".format(rating))
		await ctx.send(embed=emb)

	add_command(["general", "General", "ask", "Answers your deepest quetsions.", False])
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

		emb = getEmbed(ctx, "Ask", "What knowledge will i give you today...", "")
		emb = addField(emb, "Question", question)
		emb = addField(emb, "Answer", start_txt + end_txt)
		await ctx.send(embed=emb)

	add_command(["general", "General", "decide", "Picks between the choices given.", False])
	@commands.command()
	async def decide(self, ctx, *, decisions:str):
		decisions = decisions.split(" ")
		emb = getEmbed(ctx, "Decide", "I choose... {0}".format(decisions[randint(0, len(decisions)-1)]), "")
		await ctx.send(embed=emb)

	add_command(["general", "General", "clone", "Make someone say something stupid lol.", False])
	@commands.command()
	async def clone(self, ctx, member:discord.User=None, *, message:str=None):
		if member == None or message == None:
			await Error(ctx, self.client, "Missing un-optional argument for command.")
			return
		
		webhook = await ctx.channel.create_webhook(name=member.name)
		await webhook.send(message, username=member.name + " (fake)", avatar_url=member.avatar_url)
		await webhook.delete()

	add_command(["general", "General", "role", "Add or remove any role that begins with [r].", False])
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
