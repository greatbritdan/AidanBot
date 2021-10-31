import discord
from discord.ext import commands, tasks
from discord.utils import get

import datetime
from functions import Error, getEmbed
from random import randint

def is_pipon_palace(ctx):
	return (ctx.guild.id == 836936601824788520)

class QOTDCog(commands.Cog):
	def __init__(self, client):
		self.client = client
		self.done = False
		self.qotd.start()

	def cog_unload(self):
		self.qotd.cancel()
			
	@tasks.loop(minutes=1)
	async def qotd(self):
		current_time = datetime.datetime.now().strftime("%H:%M")
		times = ["14:00", "14:01"]
		if current_time in times and not self.done:
			await qotdask(self.client)	
			self.done = True
		elif self.done:
			self.done = False
		
	@commands.command(description="Submit Question.")
	@commands.check(is_pipon_palace)
	async def qotdadd(self, ctx, *, question:str=None):
		if question == None:
			await Error(ctx, self.client, "Missing un-optional argument for command.")
			return

		questions = await getquestions(self.client)
		questions.append(question)
		await setquestions(self.client, questions)

		emb = getEmbed(ctx, "qotdadd", "**Question added:**", f"```- {question}```")
		await ctx.send(embed=emb)

	@commands.command(description="Get All Questions.")
	@commands.check(is_pipon_palace)
	async def qotdget(self, ctx):
		questions = await getquestions(self.client)
		questions.pop(0)
		split = "\n- "
		questions = split.join(questions)

		emb = getEmbed(ctx, "qotdget", "**Questions:**", f"```- {questions}```")
		await ctx.send(embed=emb)

	@commands.command(name="qotdask", description="Ask Question.")
	@commands.check(is_pipon_palace)
	@commands.is_owner()
	async def qotdask_(self, ctx):
		await qotdask(self.client, ctx)

async def qotdask(client, ctx=None):
	questions = await getquestions(client)
	if len(questions) > 1:
		questioni = randint(1, len(questions)-1)
		question = questions[questioni]
		if "?" not in question:
			question = question + "?"

		questions.pop(questioni)
		await setquestions(client, questions)

		guild = get(client.guilds, id=836936601824788520)
		channel = get(guild.text_channels, id=856977059132866571)

		emb = getEmbed(ctx, "qotdask", "**Question of the day:**", question)
		if ctx:
			await ctx.send(embed=emb)
		else:
			await channel.send(embed=emb)

async def getquestions(client):
	guild = get(client.guilds, id=879063875469860874)
	channel = get(guild.text_channels, id=895727615573360650)
	message = await channel.fetch_message(channel.last_message_id)
	message = message.content

	qs = message.split("\n")
	return qs

async def setquestions(client, questions):
	guild = get(client.guilds, id=879063875469860874)
	channel = get(guild.text_channels, id=895727615573360650)
	await channel.purge(limit=1)

	message = "\n"
	message = message.join(questions)
	await channel.send(message)

def setup(client):
  client.add_cog(QOTDCog(client))
