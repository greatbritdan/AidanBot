import discord
import discord.ext.commands as CM
import discord.app_commands as AC
from discord import Interaction as Itr
from discord.ext import tasks
from discord.utils import get

import datetime, asyncio
from random import randint, choice
from typing import Literal

from aidanbot import AidanBot
from utils.functions import getComEmbed, sendCustomError, getBar
from utils.checks import ab_check, ab_check_slient

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
	"If you had 24 hours left to live, how would you spend that time?",
	"Do you have a morning routine?",
	"What's something small that makes you feel good?",
	"If you could say something and everyone on earth could hear it what would you say?"
]
	
class QOTDView(discord.ui.View):
	def __init__(self, cog:CM.cog, guild:int, options:list=False):
		super().__init__(timeout=None)
		self.cog = cog
		self.guild = guild

		optid = 0
		for opt in options:
			optid += 1
			self.add_item(discord.ui.Button(label=opt, style=discord.ButtonStyle.gray, custom_id=f"qotdview:{self.guild.id}:op{optid}"))

	async def interaction_check(self, itr:Itr):
		await self.cog.optionUsed(itr, itr.data["custom_id"])
		return True

class QOTDCog(CM.Cog):
	def __init__(self, client:AidanBot):
		self.client = client

	async def ready(self):
		for guild in await self.client.CON.loopdata():
			lastquestion = self.client.CON.get_value(guild, "lastquestion", guild=guild)
			if lastquestion and "options" in lastquestion and lastquestion["options"] != False:
				self.client.add_view(QOTDView(self, guild, lastquestion['options']))

		if self.client.isbeta:
			return

		if not self.qotdtask.is_running():
			self.qotdtask.start()

	def cog_unload(self):
		if self.qotdtask.is_running():
			self.qotdtask.cancel()

	async def autoquestion(self, itr:Itr, current:str):
		questions = self.client.CON.get_value(itr.guild, "questions")
		ismod = await ab_check_slient(itr, self.client, is_guild=True, has_mod_role=True)
		choices = []
		for q in questions:
			if ismod or itr.user.id == q["author"]:
				question, qid = q["question"], q["id"]
				member = get(itr.guild.members, id=q["author"])
				if current.lower() in question.lower():
					name = f"({member.name}) {question}"
					name = name[:96] + "..." if len(name) > 100 else name
					choices.append(AC.Choice(name=name, value=qid))
		return choices[:25]

	@tasks.loop(time=datetime.time(15, 0, 0, 0, datetime.datetime.now().astimezone().tzinfo))
	async def qotdtask(self):
		for guild in await self.client.CON.loopdata():
			channel = self.client.CON.get_value(guild, "qotd_channel", guild=guild)
			if channel:
				await self.createQuestion(guild)	

	###		

	async def optionUsed(self, itr:Itr, id:str):
		optid = int(id.split(":")[2][2])-1
		last = self.client.CON.get_value(itr.guild, "lastquestion")
		if not last:
			itr.response.send_message(f"Error: question has corrupted, result wasn't tallied!", ephemeral=True)
			return

		if str(itr.user.id) in last["voters"]:
			last["votes"][last["voters"][str(itr.user.id)]] -= 1
			last["voters"].pop(str(itr.user.id))

		last["votes"][optid] += 1
		last["voters"][str(itr.user.id)] = optid

		await self.client.CON.set_value(itr.guild, "lastquestion", last)
		await self.updateQuestion(itr.guild)
		await itr.response.send_message(f"Set vote to {last['options'][optid]}!", ephemeral=True)

	def getQuestionEmbed(self, question, user, left, votes=None):
		s = "" if left == 1 else "s"
		footer = None
		if votes != None:
			footer = f"Submitted by {user} • {votes} Votes • {left} question{s} left!"
		else:
			footer = f"Submitted by {user} • {left} question{s} left!"
		embed = getComEmbed(None, self.client, question)
		embed.set_footer(text=footer)
		return embed

	async def createQuestion(self, guild:discord.Guild, noping:bool=False, nosave:bool=False, noupdate:bool=False):
		channel = self.client.CON.get_value(guild, "qotd_channel", guild=guild)
		questions = self.client.CON.get_value(guild, "questions")

		if not noupdate:
			await self.createQuestionResults(guild, nosave)
		
		if len(questions) == 0:
			question = choice(defaultquestions)
			embed = self.getQuestionEmbed(question, "AidanBot", 0)
			await channel.send(embed=embed)

			await self.client.CON.set_value(guild, "lastquestion", {
				"messageid": channel.last_message_id, "id": False, "type": "Default",
				"question": question, "author": self.client.user.id, "options": False, "correct": False,
				"votes": False, "voters": False
			})
		else:
			qidx = randint(0, len(questions)-1)
			q = questions[qidx]
			question, author = q["question"], get(guild.members, id=q["author"])

			txt = "Question of the day just dropped!"
			role = self.client.CON.get_value(guild, "qotd_role", guild=guild)
			if role and (not noping):
				txt = f"Question of the day just dropped, {role.mention}"

			if "options" in q:
				embed = self.getQuestionEmbed(question, author.name, len(questions)-1, 0)
				await channel.send(txt, embed=embed, allowed_mentions=discord.AllowedMentions(roles=True), view=QOTDView(self, guild, q["options"]))
			else:
				embed = self.getQuestionEmbed(question, author.name, len(questions)-1)
				await channel.send(txt, embed=embed, allowed_mentions=discord.AllowedMentions(roles=True))

			type = "Classic (Legacy)"
			if "type" in q:
				type = q["type"]

			options, correct, votes, voters = False, False, False, False
			if "options" in q:
				options, votes, voters = q["options"], [0 for o in q["options"]], {}
			if "correct" in q:
				correct = q["correct"]
			await self.client.CON.set_value(guild, "lastquestion", {
				"messageid": channel.last_message_id, "id": q["id"], "type": type,
				"question": question, "author": q["author"], "options": options, "correct": correct,
				"votes": votes, "voters": voters
			})

			if not nosave:
				try:
					questions.pop(qidx)
					await self.client.CON.set_value(guild, "questions", questions)
				except Exception:
					await sendCustomError(self.client, "QOTD Error", "Questions was unable to save, please manualy remove question!")

	async def updateQuestion(self, guild:discord.Guild):
		lastquestion = self.client.CON.get_value(guild, "lastquestion")
		if not lastquestion:
			return
				
		channel = self.client.CON.get_value(guild, "qotd_channel", guild=guild)
		questions = self.client.CON.get_value(guild, "questions")
		lastmessage = await channel.fetch_message(lastquestion["messageid"])

		question, author = lastquestion["question"], get(guild.members, id=lastquestion["author"])
		if "options" in lastquestion and lastquestion["options"] != False:
			embed = self.getQuestionEmbed(question, author.name, len(questions), sum(lastquestion["votes"]))
			await lastmessage.edit(embed=embed)
		else:
			embed = self.getQuestionEmbed(question, author.name, len(questions))
			await lastmessage.edit(embed=embed)

	async def createQuestionResults(self, guild:discord.Guild, nosave:bool=False):
		lastquestion = self.client.CON.get_value(guild, "lastquestion")
		if not (lastquestion and "options" in lastquestion and lastquestion["options"] != False):
			return
	
		channel = self.client.CON.get_value(guild, "qotd_channel", guild=guild)
		lastmessage = await channel.fetch_message(lastquestion["messageid"])
		votes, total = lastquestion["votes"], sum(lastquestion["votes"])

		strmax = 0
		for option in lastquestion["options"]:
			if len(option) > strmax:
				strmax = len(option)
	
		body = ""
		for i, option in enumerate(lastquestion["options"]):
			opt = option
			while len(opt) < strmax:
				opt += " "

			percent = 0
			if total > 0:
				percent = round((100/total)*votes[i])

			extra, color = "", "blue"
			if "correct" in lastquestion and lastquestion["correct"]:
				if option != lastquestion["correct"]:
					color = "red"
				else:
					extra = " :white_check_mark:"
			bar = getBar(percent, 100, 10, True, color)
			body += f"`{opt}:` {bar}{extra} **({str(percent)}%) ({votes[i]} votes)**\n"

		embed = getComEmbed(None, self.client, "Question Of The Day > Results", body)
		embed.set_footer(text=f"{total} Votes")
		await channel.send(embed=embed)

		if not nosave:
			await lastmessage.edit(view=None)
			await self.client.CON.set_value(guild, "lastquestion", False)

	###

	def strtobool(self, val):
		if val == "True":
			return True
		return False

	qotdgroup = AC.Group(name="qotd", description="Question Of The Day commands.")

	@qotdgroup.command(name="test", description="Test qotd.")
	async def test(self, itr:Itr, noping:Literal["True","False"]="True", nosave:Literal["True","False"]="True", typee:Literal["Question","Results","Both"]="False"):
		if not await ab_check(itr, self.client, has_mod_role=True):
			return
		if self.client.isbeta or not await ab_check_slient(itr, self.client, is_guild=True, has_value="qotd_channel"):
			return await itr.response.send_message("Question Of The Day is not setup in this server.", ephemeral=True)
		noping, nosave = self.strtobool(noping), self.strtobool(nosave)
		if typee == "Both":
			await self.createQuestion(itr.guild, noping, nosave)
			await itr.response.send_message("Asked'd & Result'd... yea...", ephemeral=True)
		elif typee == "Results":
			await self.createQuestionResults(itr.guild, nosave)
			await itr.response.send_message("Result'd... yea...", ephemeral=True)
		else:
			await self.createQuestion(itr.guild, noping, nosave, True)
			await itr.response.send_message("Asked'd... yea...", ephemeral=True)

	@qotdgroup.command(name="ask", description="Add a question to qotd.")
	@AC.describe(
		question="The question you are asking.", options="The options members will pick from, leave blank for a normal question, only 2 to 5 options allowed.",
		correct="The correct answer, requires options and for the correct answer to be in the options, leave blank for a normal poll."
	)
	async def ask(self, itr:Itr, question:str, options:str=None, correct:str=None):
		if self.client.isbeta or not await ab_check_slient(itr, self.client, is_guild=True, has_value="qotd_channel"):
			return await itr.response.send_message("Question Of The Day is not setup in this server.", ephemeral=True)
		if len(question) == 0:
			return await itr.response.send_message("Questions Can't Be Blank.", ephemeral=True)
		if len(question) > 250:
			return await itr.response.send_message("Too many characters! Questions mustn't be more than 250 characters.", ephemeral=True)
		
		opts = None
		if options:
			opts = options.strip().split(",")
			opts = [opt.strip() for opt in opts if len(opt.strip()) > 0]
			if len(opts) < 2:
				return await itr.response.send_message("At least 2 options are required, blank options are ignored.", ephemeral=True)
			if len(opts) > 5:
				return await itr.response.send_message("At most 5 options are allowed.", ephemeral=True)
			for opt in opts:
				if len(opt) > 75:
					return await itr.response.send_message(f"Too many characters for `{opt}`! Options mustn't be more than 75 characters.", ephemeral=True)
					
		if correct:
			if correct not in opts:
				return await itr.response.send_message("The correct answer must exist in your options.", ephemeral=True)
			
		if question[-1] != "?":
			question += "?"
		questions = self.client.CON.get_value(itr.guild, "questions")
		qid = generateID(questions)

		plus = ""
		typee = "Unknown"
		if options and correct:
			typee = "Quiz"
			questions.append({"question": question, "author": itr.user.id, "id": qid, "type": "quiz", "options": opts, "correct": correct})
			plus = f"\nOptions : {', '.join(opts)}\nCorrect : {correct}"
		elif options:
			typee = "Choice"
			questions.append({"question": question, "author": itr.user.id, "id": qid, "type": "choice", "options": opts})
			plus = f"\nOptions : {', '.join(opts)}"
		else:
			typee = "Classic"
			questions.append({"question": question, "author": itr.user.id, "id": qid, "type": "classic"})
		await self.client.CON.set_value(itr.guild, "questions", questions)
		await itr.response.send_message(embed=getComEmbed(str(itr.user), self.client, f"Added question!", f"> **'{question}**'\nType    : {typee}{plus}```"), ephemeral=True)

	@qotdgroup.command(name="remove", description="Remove a question from qotd, you can only remove your own unless you are a mod.")
	@AC.describe(question="The question to be removed, remember you can only remove your own unless you are a mod.")
	async def remove(self, itr:Itr, question:str):
		if self.client.isbeta or not await ab_check_slient(itr, self.client, is_guild=True, has_value="qotd_channel"):
			return await itr.response.send_message("Question Of The Day is not setup in this server.", ephemeral=True)

		questions = self.client.CON.get_value(itr.guild, "questions")
		ismod = await ab_check_slient(itr, self.client, is_guild=True, has_mod_role=True)
		questiondata = getQuestionFromID(questions, question, ismod, itr)
		if not questiondata:
			return await itr.response.send_message("Question couldn't be found, try again.", ephemeral=True)

		questions = [q for q in questions if q["id"] != question]
		await self.client.CON.set_value(itr.guild, "questions", questions)
		await itr.response.send_message(embed=getComEmbed(str(itr.user), self.client, f"Removed question!", f"> **'{questiondata['question']}'**"), ephemeral=True)

	@remove.autocomplete("question")
	async def remove_question(self, itr:Itr, current:str):
		if self.client.isbeta or not await ab_check_slient(itr, self.client, is_guild=True, has_value="qotd_channel"):
			return []
		return await self.autoquestion(itr, current)
	
	@qotdgroup.command(name="view", description="Look at all the questions.")
	async def view(self, itr:Itr):
		if self.client.isbeta or not await ab_check_slient(itr, self.client, is_guild=True, has_value="qotd_channel"):
			return await itr.response.send_message("Question Of The Day is not setup in this server.", ephemeral=True)

		questions = self.client.CON.get_value(itr.guild, "questions")
		if len(questions) == 0:
			return await itr.response.send_message("There are currently no questions, be one of the first with /qotd ask!", ephemeral=True)
		
		questiondata = questions[0]
		def getEmbed(timeout=False):
			data = ""
			if "type" in questiondata:
				data += f"Type    : {questiondata['type'].capitalize()}"
			else:
				data += f"Type    : Classic (Legacy)"
			if "options" in questiondata:
				data += f"\nOptions : {', '.join(questiondata['options'])}"
			if "correct" in questiondata:
				if itr.user.id == questiondata["author"]:
					data += f"\nCorrect : {questiondata['correct']}"
				else:
					data += f"\nCorrect : <hidden>"

			choicequestions = []
			for q in questions:
				label = q["question"][:96]+"..." if len(q["question"]) > 100 else q["question"]
				member = get(itr.guild.members, id=q["author"])
				active = True if q["id"] == questiondata["id"] else False
				choicequestions.append(discord.SelectOption(label=label, value=q["id"], description=f"By: {member.name}", default=active))

			datamember = get(itr.guild.members, id=questiondata["author"])

			embed = getComEmbed(str(itr.user), self.client, f"'{questiondata['question']}'", f"**Submitted by:** {datamember.mention}\n```{data}```")
			view = discord.ui.View(timeout=None)
			view.add_item(discord.ui.Select(placeholder="Choose Question", min_values=1, max_values=1, options=choicequestions, disabled=timeout, custom_id="select"))
			return embed, view
		
		embed, view = getEmbed()
		await itr.response.send_message(embed=embed, view=view, ephemeral=True)
		MSG = await itr.original_response()

		def check(checkitr:Itr):
			try:
				return (checkitr.message.id == MSG.id)
			except:
				return False
		while True:
			try:
				butitr:Itr = await self.client.wait_for("interaction", timeout=90, check=check)
				if butitr.user == itr.user:
					await butitr.response.defer()
					if butitr.data["custom_id"] == "select":
						qid = butitr.data["values"][0]
						questiondata = getQuestionFromID(questions, qid)
						embed, view = getEmbed()
						await itr.edit_original_response(embed=embed, view=view)
				else:
					await butitr.response.send_message(self.client.itrFail(), ephemeral=True)
			except asyncio.TimeoutError:
				embed, view = getEmbed(True)
				return await itr.edit_original_response(embed=embed, view=view)

def generateID(questions):
	questionids = [q["id"] for q in questions]
	id = ""
	while id == "" or id in questionids:
		id = "".join([choice("1234567890abcdef") for i in range(0,8)])
	return id

def getQuestionFromID(questions, qid, ismod=True, itr=False):
	for q in questions:
		if q["id"] == qid and (ismod or q["author"] == itr.user.id):
			return q
	return False

async def setup(client:AidanBot):
	await client.add_cog(QOTDCog(client), guilds=client.debug_guilds)
