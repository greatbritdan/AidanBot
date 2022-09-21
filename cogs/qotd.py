import discord
from discord.ext import commands, pages
from discord.commands import SlashCommandGroup
from discord.utils import get
from discord import Option

import asyncio, datetime
from random import randint, choice

from functions import getComEmbed, sendCustomError
from checks import command_checks

defaultquestions = [
	"What games would be your top recommendations?",
	"What games would you never recommend?",
	"What skill do you want to learn?",
	"What is the best month of the year?",
	"What is the best holiday?",
	"What website should more people know about?",
	"What is your favorite video game goal?",
	"What emoji describes you best?",
	"What do you hate doing but can't stop doing it",
	"What's your favorite food?",
	"What's your least favorite food?",
	"What's a food combination that seems odd, but you swear by?",
	"What's the best video game controller you've ever used?",
	"If you could have one superpower what would it be?",
	"If you were a millionaire, what would you do with the money?",
	"If laws didn't exist, what old laws would you break regularly?",
	"If you had 24 hours left to live, how would you spend that time?"
]

def tobool(val):
	if val.lower() == "true":
		return True
	return False

async def auto_questions(ctx):
	questions = ctx.bot.CON.get_value(ctx.interaction.guild, "questions")
	qlist = []
	for q in questions:
		if ctx.interaction.channel.permissions_for(ctx.interaction.user).manage_messages or q["author"] == ctx.interaction.user.id:
			jq = q["question"]
			if len(jq) > 95:
				jq = jq[:95]
			qlist.append(jq)
	return qlist

AC = discord.ApplicationContext
class QOTDCog(discord.Cog):
	def __init__(self, client:commands.Bot):
		self.client = client

	async def ready(self):
		self.client.loop.create_task(self.background_task())
		
	async def askQuestion(self, testpost=False, postguild:discord.Guild=False):
		if self.client.isbeta:
			return
		for guild in await self.client.CON.loopdata():
			if (not postguild) or postguild == guild:
				channel = self.client.CON.get_value(guild, "qotd_channel", guild=guild)
				if channel:
					questions = self.client.CON.get_value(guild, "questions")
					defaultq = False
					if len(questions) == 0:
						quest = choice(defaultquestions)
						defaultq = True
					else:
						questioni = randint(0, len(questions)-1)
						question = questions[questioni]

						quest, author = question["question"], get(guild.members, id=question["author"])
						if not quest.endswith("?"): quest += "?"

					emb = getComEmbed(None, self.client, "Question Of The Day", quest)
					if defaultq:
						emb.set_footer(text=f"Question submitted by AidanBot | 0 questions left!!!")
					else:
						if len(questions) == 2:
							emb.set_footer(text=f"Question submitted by {str(author)} | 1 question left! consider adding some now!")
						else:
							emb.set_footer(text=f"Question submitted by {str(author)} | {len(questions)-1} questions left.")

					txt = ""
					if not defaultq:
						role = self.client.CON.get_value(guild, "qotd_role", guild=guild)
						if (not testpost) and role:
							txt = f"Wake up sussy's, New QOTD dropped. {role.mention}"

					await channel.send(txt, embed=emb, allowed_mentions=discord.AllowedMentions(roles=True))
					if (not defaultq) and (not testpost):
						questions.pop(questioni)
						try:
							await self.client.CON.set_value(guild, "questions", questions)
						except:
							await sendCustomError(self.client, "QOTD Error", "Questions was unable to save, please manualy remove question!")
							
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

	'''@qotdgroup.command(name="setposttime", description="Sets the post time for QOTD.")
	async def setposttime(self, ctx:AC,
		posttime:Option(str, "The time where it will be posted.", choices=["0","1","2","3","4","5","6","7","8","9","10","11","12","13","14","15","16","17","18","19","20","21","22","23"], required=True)
	):
		if await command_checks(ctx, self.client, is_guild=True, has_mod_role=True, has_value="qotd_channel"): return
		posttime = int(posttime)

		when = datetime.time(posttime,0,0)
		now = datetime.datetime.utcnow()
		if now.time() > when:
			post = datetime.datetime.combine(now.date()+datetime.timedelta(days=1), datetime.time(0))
		post = datetime.datetime.combine(now.date(), when)
		time = post-now

		await self.client.CON.set_value(ctx.guild, "qotd_posttime", posttime)
		await ctx.respond(embed=getComEmbed(ctx, self.client, f"Set posttime, next question in {math.floor(time.seconds/60/60)} hour(s) and {math.ceil((time.seconds/60)%60)} minute(s).", "(Calculated in UTC, change if incorrect)"))
		#await ctx.respond(embed=getComEmbed(ctx, self.client, f"Set posttime to {format_dt(post,'t')}! Next question will be asked {format_dt(post,'R')}."))'''

	@qotdgroup.command(name="post", description="Forcefully post a question.")
	async def post(self, ctx:AC,
		testpost:Option(str, "If the question isn't removed from the questions list, useful for tests.", choices=["True", "False"], default="True")
	):
		if await command_checks(ctx, self.client, is_owner=True, is_guild=True, has_value="qotd_channel"): return

		await self.askQuestion(tobool(testpost), ctx.guild)
		await ctx.respond("Question has been askified.")

	@qotdgroup.command(name="list", description="List all questions.")
	async def list(self, ctx:AC):	
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
	async def ask(self, ctx:AC,
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
	async def remove(self, ctx:AC,
		questionid:Option(str, "The ID of question you want to remove.", required=True)
	):	
		if await command_checks(ctx, self.client, is_guild=True, has_value="qotd_channel"): return
		questions = self.client.CON.get_value(ctx.guild, "questions")
		questions = [q for q in questions if q["id"] != questionid]
		await self.client.CON.set_value(ctx.guild, "questions", questions)
		await ctx.respond(embed=getComEmbed(ctx, self.client, f"Removed question!"))

	@qotdgroup.command(name="convert", description="Add ID's to every question.")
	async def convert(self, ctx:AC):	
		if await command_checks(ctx, self.client, is_owner=True, is_guild=True, has_value="qotd_channel"): return
		questions = self.client.CON.get_value(ctx.guild, "questions")
		newquestions = []
		for question in questions:
			if "id" in question:
				newquestions.append({ "question": question["question"], "author": question["author"], "id": question["id"] })
			else:
				newquestions.append({ "question": question["question"], "author": question["author"], "id": self.generateID(newquestions) })
		await self.client.CON.set_value(ctx.guild, "questions", newquestions)
		await ctx.respond(embed=getComEmbed(ctx, self.client, f"Converted question!"))

def setup(client):
	client.add_cog(QOTDCog(client))
