import discord
from discord.ext import pages
from discord.commands import SlashCommandGroup
from discord import Option, Color
from discord.utils import get

import asyncio, datetime, choice
from random import randint

from functions import getComEmbed
from checks import command_checks

def tobool(val):
	if val.lower() == "true":
		return True
	return False

class QOTDCog(discord.Cog):
	def __init__(self, client):
		self.client = client

	async def ready(self):
		self.client.loop.create_task(self.background_task())
		
	async def askQuestion(self, testpost=False, postguild=False):
		if self.client.isbeta:
			return
		for guild in await self.client.CON.loopdata():
			if (not postguild) or postguild == guild:
				channel = self.client.CON.get_value(guild, "qotd_channel", guild=guild)
				if channel:
					questions = self.client.CON.get_value(guild, "questions")
					if len(questions) == 0:
						emb = getComEmbed(None, self.client, "Question Of The Day", f"Looks like we're out of questions, use /qotd config to add more!", Color.from_rgb(145, 29, 37))
						await channel.send(embed=emb)
					else:
						questioni = randint(0, len(questions)-1)
						question = questions[questioni]

						quest, author = question["question"], get(guild.members, id=question["author"])
						if not quest.endswith("?"): quest += "?"
						emb = getComEmbed(None, self.client, "Question Of The Day", quest)
						if len(questions) == 2:
							emb.set_footer(text=f"Question submitted by {str(author)} | 1 question left! Consier adding some now!")
						else:
							emb.set_footer(text=f"Question submitted by {str(author)} | {len(questions)-1} questions left.")

						txt, role = "", self.client.CON.get_value(guild, "qotd_role", guild=guild)
						if (not testpost) and role:
							txt = f"Wake up sussy's, New QOTD dropped. {role.mention}"
						await channel.send(txt, embed=emb, allowed_mentions=discord.AllowedMentions(roles=True))
						if not testpost:
							questions.pop(questioni)
							try:
								await self.client.CON.set_value(guild, "questions", questions)
							except:
								print("QOTD Failed. Propper error will exist in V2")
							
	async def background_task(self):
		when = datetime.time(15,0,0)
		now = datetime.datetime.utcnow()
		if now.time() > when:
			tomorrow = datetime.datetime.combine(now.date() + datetime.timedelta(days=1), datetime.time(0))
			seconds = (tomorrow - now).total_seconds()
			await asyncio.sleep(seconds)
		while True:
			now = datetime.datetime.utcnow()
			target_time = datetime.datetime.combine(now.date(), when)
			seconds_until_target = (target_time - now).total_seconds()
			await asyncio.sleep(seconds_until_target)
			await self.askQuestion()
			tomorrow = datetime.datetime.combine(now.date() + datetime.timedelta(days=1), datetime.time(0))
			seconds = (tomorrow - now).total_seconds()
			await asyncio.sleep(seconds)

	def generateID(self, questions):
		questionids = [q["id"] for q in questions]
		txt = ""
		while txt == "" or txt in questionids:
			txt = ""
			for i in range(6):
				txt += choice("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890")
		return txt
			
	qotdgroup = SlashCommandGroup("qotd", "Question Of The Day commands.")

	@qotdgroup.command(name="post", description="Forcefully post a question.")
	async def post(self, ctx,
		testpost:Option(str, "If the question isn't removed from the questions list, useful for tests.", choices=["True", "False"], default="True")
	):
		if await command_checks(ctx, self.client, is_owner=True, is_guild=True, has_value="qotd_channel"): return

		await self.askQuestion(tobool(testpost), ctx.guild)
		await ctx.respond("Question has been askified.")
		
	@qotdgroup.command(name="list", description="List all questions.")
	async def list(self, ctx):	
		if await command_checks(ctx, self.client, is_guild=True, has_value="qotd_channel"): return
		questions = self.client.CON.get_value(ctx.guild, "questions")

		def getqotdlistembed(questions):
			fields = []
			for question in questions:
				member = get(ctx.guild.members, id=question["author"])
				fields.append([f"'{question['question']}'", f"Submitted by **{str(member)}** | ID: **{question['id']}**"])
			return getComEmbed(ctx, self.client, f"All Questions for {ctx.guild.name}", "Submit your own wil /qotd ask!", fields=fields)

		def divide_chunks(l, n):
			for i in range(0, len(l), n):
				yield l[i:i + n]

		infopages = []
		questionchunks = divide_chunks(questions, 5)
		for qc in questionchunks:
			infopages.append(getqotdlistembed(qc))

		infopagesbuttons = [
			pages.PaginatorButton("prev", label="<-", style=discord.ButtonStyle.blurple),
			pages.PaginatorButton("page_indicator", style=discord.ButtonStyle.gray, disabled=True),
			pages.PaginatorButton("next", label="->", style=discord.ButtonStyle.blurple),
		]
		paginator = pages.Paginator(pages=infopages, loop_pages=True, disable_on_timeout=True, timeout=60, use_default_buttons=False, custom_buttons=infopagesbuttons)
		await paginator.respond(ctx.interaction)

	@qotdgroup.command(name="ask", description="Add a question to the daily questions.")
	async def ask(self, ctx,
		question:Option(str, "The question you want to ask.", required=True)
	):	
		if await command_checks(ctx, self.client, is_guild=True, has_value="qotd_channel"): return
		questions = self.client.CON.get_value(ctx.guild, "questions")
		if len(question) > 250:
			return await ctx.respond("Too many characters! Questions mustn't be more than 250 characters.")
		if len([q for q in questions if q["question"] == question]) > 0:
			return await ctx.respond("You can't send the same question as someone else.")
		questions.append({ "question": question, "author": ctx.author.id, "id": self.generateID(questions) })
		await self.client.CON.set_value(ctx.guild, "questions", questions)
		await ctx.respond(embed=getComEmbed(ctx, self.client, f"Added question!"))

	@qotdgroup.command(name="remove", description="Remove one of your questions from the daily questions, Mods can remove anyones question.")
	async def remove(self, ctx,
		questionid:Option(str, "The ID of question you want to remove.", required=True)
	):	
		if await command_checks(ctx, self.client, is_guild=True, has_value="qotd_channel"): return
		questions = self.client.CON.get_value(ctx.guild, "questions")
		questions = [q for q in questions if q["id"] != questionid]
		await self.client.CON.set_value(ctx.guild, "questions", questions)
		await ctx.respond(embed=getComEmbed(ctx, self.client, f"Removed question!"))

def setup(client):
	client.add_cog(QOTDCog(client))
