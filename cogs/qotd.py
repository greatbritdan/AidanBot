import discord
from discord.ext import commands, tasks
from discord.utils import get

import datetime
from functions import Error
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
			
	@tasks.loop(minutes=5)
	async def qotd(self):
		current_time = datetime.datetime.now().strftime("%H:%M")
		times = ["14:00", "14:01", "14:02", "14:03", "14:04"]
		if current_time in times and not self.done:
			questions = await getquestions(self.client)
			if len(questions) > 1:
				questioni = randint(1, len(questions)-1)
				question = questions[questioni]
				questions.pop(questioni)
				await setquestions(self.client, questions)

				guild = get(self.client.guilds, id=836936601824788520)
				channel = get(guild.text_channels, id=856977059132866571)

				if "?" not in question:
					question = question + "?"
				await channel.send(f"**Question of the day:** {question}")
				
			self.done = True
		elseif self.done:
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

		await ctx.send(f"added '{question}' to the list")

	@commands.command(description="Test Question.")
	@commands.is_owner()
	async def qotdtest(self, ctx):
		questions = await getquestions(self.client)
	
		if len(questions) > 1:
			questioni = randint(1, len(questions)-1)
			question = questions[questioni]
			questions.pop(questioni)
			await setquestions(self.client, questions)

			guild = get(self.client.guilds, id=836936601824788520)
			channel = get(guild.text_channels, id=856977059132866571)
			
			if "?" not in question:
				question = question + "?"
			await channel.send(f"**Question of the day:** {question}")

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
