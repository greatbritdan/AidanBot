import discord
from discord.ext import commands, tasks

import datetime
from random import randint

from discord.ext.commands.core import is_owner

from functions import getComEmbed, ComError

import json
with open('./commanddata.json') as file:
	temp = json.load(file)
	DESC = temp["desc"]

def is_pipon_palace(ctx):
	return (ctx.guild.id == 836936601824788520)

class QOTDCog(commands.Cog):
	def __init__(self, client):
		self.client = client
		self.done = False
		self.qotd.start()

	def cog_unload(self):
		if self.qotd.is_running():
			self.qotd.cancel()

	@tasks.loop(seconds=59)
	async def qotd(self):
		if not self.client.isbeta:
			self.qotd.stop()

		current_time = datetime.datetime.now().strftime("%H:%M")
		if current_time == "14:00" and not self.done:
			await self.qotd_ask()
			self.done = True
		elif current_time != "14:00" and self.done:
			self.done = False

	@qotd.before_loop
	async def before_qotd(self):
		await self.client.wait_until_ready()

	async def qotd_ask(self, ctx=None):
		chan = ctx.channel if ctx else self.client.qotd_channel

		emb = None
		questions = await self.qotd_questions("get")
		if len(questions) > 1:	
			questioni = randint(1, len(questions)-1)
			question = questions[questioni]
			question += "?" if "?" not in question else ""
			questions.pop(questioni)
			await self.qotd_questions("set", questions)

			emb = getComEmbed(ctx, self.client, "qotdask", "**Question of the day:**", question)
		else:
			emb = getComEmbed(ctx, self.client, "qotdask", "**All out of questions!**", "Use qotdadd to add some new ones!")

		await chan.send(embed=emb)

	async def qotd_questions(self, action, data=None):
		chan = self.client.qotd_store_channel
		last = await chan.fetch_message(chan.last_message_id)
		if action == "get":
			data = last.content
			return data.split("\n")
		elif action == "set":
			await last.delete()
			new = "\n".join(data)
			await chan.send(new)

	@commands.command(name="qotd", description="sasd")
	@commands.cooldown(1, 5)
	@commands.check(is_pipon_palace)
	async def qotd_(self, ctx, action="get", *, extra=None):
		questions = await self.qotd_questions("get")
		if action == "get":
			questions.pop(0)
			questions = "\n- ".join(questions)
			emb = getComEmbed(ctx, self.client, "qotd get", "**Questions:**", f"```- {questions}```")
			if len(questions) == 0:
				emb = getComEmbed(ctx, self.client, "qotd get", "**Questions:**", f"```None yet, Use 'qotd add' to add some new ones!```")
			await ctx.send(embed=emb)
		elif action == "add":
			if extra:
				questions.append(extra)
				await self.qotd_questions("set", questions)
				emb = getComEmbed(ctx, self.client, "qotd add", "**Question added:**", f"```{extra}```\nRemember not to answer it yet! wait until it's asked by me.")
				await ctx.send(embed=emb)
			else:
				await ComError(ctx, self.client, "Needs question.")
				return
		elif action == "ask" and self.client.is_owner(ctx.author):
			await self.qotd_ask()

def setup(client):
	client.add_cog(QOTDCog(client))