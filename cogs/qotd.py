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
from utils.functions import getComEmbed, sendCustomError
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
	"If you had 24 hours left to live, how would you spend that time?"
	"Do you have a morning routine?",
	"What's something small that makes you feel good?",
	"If you could say something and everyone on earth could hear it what would you say?"
]

def tobool(val):
	if val.lower() == "true":
		return True
	return False

def generateID(questions):
	questionids = [q["id"] for q in questions]
	txt = ""
	while txt == "" or txt in questionids:
		txt = ""
		for i in range(6):
			if i % 2 == 0:
				txt += choice("1234567890")
			else:
				txt += choice("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890")
	return txt

class QOTDCog(CM.Cog):
	def __init__(self, client:AidanBot):
		self.client = client

	async def ready(self):
		self.qotdtask0.start()
		self.qotdtask1.start()
		self.qotdtask2.start()
		self.qotdtask3.start()
		self.qotdtask4.start()
		self.qotdtask5.start()
		self.qotdtask6.start()
		self.qotdtask7.start()
		self.qotdtask8.start()
		self.qotdtask9.start()
		self.qotdtask10.start()
		self.qotdtask11.start()
		self.qotdtask12.start()
		self.qotdtask13.start()
		self.qotdtask14.start()
		self.qotdtask15.start()
		self.qotdtask16.start()
		self.qotdtask17.start()
		self.qotdtask18.start()
		self.qotdtask19.start()
		self.qotdtask20.start()
		self.qotdtask21.start()
		self.qotdtask22.start()
		self.qotdtask23.start()
		
	def cog_unload(self):
		self.qotdtask0.cancel()
		self.qotdtask1.cancel()
		self.qotdtask2.cancel()
		self.qotdtask3.cancel()
		self.qotdtask4.cancel()
		self.qotdtask5.cancel()
		self.qotdtask6.cancel()
		self.qotdtask7.cancel()
		self.qotdtask8.cancel()
		self.qotdtask9.cancel()
		self.qotdtask10.cancel()
		self.qotdtask11.cancel()
		self.qotdtask12.cancel()
		self.qotdtask13.cancel()
		self.qotdtask14.cancel()
		self.qotdtask15.cancel()
		self.qotdtask16.cancel()
		self.qotdtask17.cancel()
		self.qotdtask18.cancel()
		self.qotdtask19.cancel()
		self.qotdtask20.cancel()
		self.qotdtask21.cancel()
		self.qotdtask22.cancel()
		self.qotdtask23.cancel()
		
	async def askQuestion(self, guild:discord.Guild=False, dontremove=False, dontping=False):
		if self.client.isbeta and (not dontremove):
			return

		channel = self.client.CON.get_value(guild, "qotd_channel", guild=guild)
		questions = self.client.CON.get_value(guild, "questions")

		if len(questions) == 0:
			quest = choice(defaultquestions)
			emb = getComEmbed(None, self.client, "Question Of The Day", quest)
			emb.set_footer(text=f"Question submitted by AidanBot | 0 questions left!!!")
			await channel.send("", embed=emb, allowed_mentions=discord.AllowedMentions(roles=True))
		
		else:
			questioni = randint(0, len(questions)-1)
			question = questions[questioni]
			quest:str

			quest, author = question["question"], get(guild.members, id=question["author"])
			if not quest.endswith("?"): quest += "?"

			emb = getComEmbed(None, self.client, "Question Of The Day", quest)
			if len(questions) == 2:
				emb.set_footer(text=f"Question submitted by {str(author)} | 1 question left! Consier adding some now!")
			else:
				emb.set_footer(text=f"Question submitted by {str(author)} | {len(questions)-1} questions left.")

			txt = ""
			role = self.client.CON.get_value(guild, "qotd_role", guild=guild)
			if (not dontping) and role:
				txt = f"Wake up sussy's, New QOTD dropped. {role.mention}"

			await channel.send(txt, embed=emb, allowed_mentions=discord.AllowedMentions(roles=True))
			if not dontremove:
				questions.pop(questioni)
				try:
					await self.client.CON.set_value(guild, "questions", questions)
				except Exception:
					await sendCustomError(self.client, "QOTD Error", "Questions was unable to save, please manualy remove question!")

	async def checktime(self, time):
		for guild in await self.client.CON.loopdata():
			channel = self.client.CON.get_value(guild, "qotd_channel", guild=guild)
			if channel:
				timezone = self.client.CON.get_value(guild, "timezone", guild=guild)
				posttime = self.client.CON.get_value(guild, "qotd_posttime", guild=guild)
				if self.client.timetable[timezone][time] == posttime:
					await self.askQuestion(guild)

	@tasks.loop(time=datetime.time(0, 0, 0, 0, datetime.datetime.now().astimezone().tzinfo))
	async def qotdtask0(self):
		await self.checktime("0 AM")

	@tasks.loop(time=datetime.time(1, 0, 0, 0, datetime.datetime.now().astimezone().tzinfo))
	async def qotdtask1(self):
		await self.checktime("1 AM")

	@tasks.loop(time=datetime.time(2, 0, 0, 0, datetime.datetime.now().astimezone().tzinfo))
	async def qotdtask2(self):
		await self.checktime("2 AM")

	@tasks.loop(time=datetime.time(3, 0, 0, 0, datetime.datetime.now().astimezone().tzinfo))
	async def qotdtask3(self):
		await self.checktime("3 AM")

	@tasks.loop(time=datetime.time(4, 0, 0, 0, datetime.datetime.now().astimezone().tzinfo))
	async def qotdtask4(self):
		await self.checktime("4 AM")

	@tasks.loop(time=datetime.time(5, 0, 0, 0, datetime.datetime.now().astimezone().tzinfo))
	async def qotdtask5(self):
		await self.checktime("5 AM")
		
	@tasks.loop(time=datetime.time(6, 0, 0, 0, datetime.datetime.now().astimezone().tzinfo))
	async def qotdtask6(self):
		await self.checktime("6 AM")

	@tasks.loop(time=datetime.time(7, 0, 0, 0, datetime.datetime.now().astimezone().tzinfo))
	async def qotdtask7(self):
		await self.checktime("7 AM")
	
	@tasks.loop(time=datetime.time(8, 0, 0, 0, datetime.datetime.now().astimezone().tzinfo))
	async def qotdtask8(self):
		await self.checktime("8 AM")

	@tasks.loop(time=datetime.time(9, 0, 0, 0, datetime.datetime.now().astimezone().tzinfo))
	async def qotdtask9(self):
		await self.checktime("9 AM")

	@tasks.loop(time=datetime.time(10, 0, 0, 0, datetime.datetime.now().astimezone().tzinfo))
	async def qotdtask10(self):
		await self.checktime("10 AM")

	@tasks.loop(time=datetime.time(11, 0, 0, 0, datetime.datetime.now().astimezone().tzinfo))
	async def qotdtask11(self):
		await self.checktime("11 AM")

	@tasks.loop(time=datetime.time(12, 0, 0, 0, datetime.datetime.now().astimezone().tzinfo))
	async def qotdtask12(self):
		await self.checktime("12 PM")

	@tasks.loop(time=datetime.time(13, 0, 0, 0, datetime.datetime.now().astimezone().tzinfo))
	async def qotdtask13(self):
		await self.checktime("1 PM")
		
	@tasks.loop(time=datetime.time(14, 0, 0, 0, datetime.datetime.now().astimezone().tzinfo))
	async def qotdtask14(self):
		await self.checktime("2 PM")

	@tasks.loop(time=datetime.time(15, 0, 0, 0, datetime.datetime.now().astimezone().tzinfo))
	async def qotdtask15(self):
		await self.checktime("3 PM")
	
	@tasks.loop(time=datetime.time(16, 0, 0, 0, datetime.datetime.now().astimezone().tzinfo))
	async def qotdtask16(self):
		await self.checktime("4 PM")

	@tasks.loop(time=datetime.time(17, 0, 0, 0, datetime.datetime.now().astimezone().tzinfo))
	async def qotdtask17(self):
		await self.checktime("5 PM")

	@tasks.loop(time=datetime.time(18, 0, 0, 0, datetime.datetime.now().astimezone().tzinfo))
	async def qotdtask18(self):
		await self.checktime("6 PM")

	@tasks.loop(time=datetime.time(19, 0, 0, 0, datetime.datetime.now().astimezone().tzinfo))
	async def qotdtask19(self):
		await self.checktime("7 PM")

	@tasks.loop(time=datetime.time(20, 0, 0, 0, datetime.datetime.now().astimezone().tzinfo))
	async def qotdtask20(self):
		await self.checktime("8 PM")

	@tasks.loop(time=datetime.time(21, 0, 0, 0, datetime.datetime.now().astimezone().tzinfo))
	async def qotdtask21(self):
		await self.checktime("9 PM")
		
	@tasks.loop(time=datetime.time(22, 0, 0, 0, datetime.datetime.now().astimezone().tzinfo))
	async def qotdtask22(self):
		await self.checktime("10 PM")

	@tasks.loop(time=datetime.time(23, 0, 0, 0, datetime.datetime.now().astimezone().tzinfo))
	async def qotdtask23(self):
		await self.checktime("11 PM")

	###

	qotdgroup = AC.Group(name="qotd", description="Question Of The Day commands.")

	@qotdgroup.command(name="list", description="List all questions.")
	async def list(self, itr:Itr):	
		if not await ab_check(itr, self.client, is_guild=True, has_value="qotd_channel"):
			return
		questions = self.client.CON.get_value(itr.guild, "questions")
		if len(questions) == 0:
			return await itr.response.send_message("No questions added. Try adding some with /qotd ask!")

		def getqotdlistembed(questions):
			fields = []
			for question in questions:
				member = get(itr.guild.members, id=question["author"])
				fields.append([f"'{question['question']}'", f"Submitted by **{str(member)}** | ID: **{question['id']}**"])
			return getComEmbed(str(itr.user), self.client, f"All Questions for {itr.guild.name}", "Submit your own questions with /qotd ask!", fields=fields)

		page = 0
		pages = []
		for qc in divide_chunks(questions, 5):
			pages.append(getqotdlistembed(qc))

		def getView(timeout=False):
			view = discord.ui.View(timeout=None)
			view.add_item(discord.ui.Button(label="<-", style=discord.ButtonStyle.blurple, custom_id="left", disabled=timeout))
			view.add_item(discord.ui.Button(label=f"{page+1}/{len(pages)}", style=discord.ButtonStyle.gray, custom_id="display", disabled=True))
			view.add_item(discord.ui.Button(label="->", style=discord.ButtonStyle.blurple, custom_id="right", disabled=timeout))
			return view
		
		await itr.response.send_message(embed=pages[page], view=getView())
		MSG = await itr.original_response()

		def check(checkitr:Itr):
			try:
				return (checkitr.message.id == MSG.id)
			except:
				return False
		while True:
			try:
				butitr:Itr = await self.client.wait_for("interaction", timeout=30, check=check)
				if butitr.user == itr.user:
					await butitr.response.defer()
					if butitr.data["custom_id"] == "left":
						page -= 1
						if page < 0: page = len(pages)-1
					elif butitr.data["custom_id"] == "right":
						page += 1
						if page > len(pages)-1: page = 0
					await itr.edit_original_response(embed=pages[page], view=getView())
				else:
					await butitr.response.send_message(self.client.itrFail(), ephemeral=True)
			except asyncio.TimeoutError:
				return await itr.edit_original_response(view=getView(True))

	@qotdgroup.command(name="ask", description="Add a question to the daily questions.")
	@AC.describe(question="The question you want to ask.")
	async def ask(self, itr:Itr, question:str):	
		if not await ab_check(itr, self.client, is_guild=True, has_value="qotd_channel"):
			return
		questions = self.client.CON.get_value(itr.guild, "questions")
		if len(question) > 250:
			return await itr.response.send_message("Too many characters! Questions mustn't be more than 250 characters.")
		if len([q for q in questions if q["question"] == question]) > 0:
			return await itr.response.send_message("You can't send the same question as someone else.")
		qid = generateID(questions)
		questions.append({ "question": question, "author": itr.user.id, "id": qid })
		await self.client.CON.set_value(itr.guild, "questions", questions)
		await itr.response.send_message(embed=getComEmbed(str(itr.user), self.client, f"Added question!", f"With id **{qid}**"))

	@qotdgroup.command(name="remove", description="Remove one of your questions from the daily questions, Mods can remove anyones question.")
	@AC.describe(questionid="The ID of question you want to remove.")
	async def remove(self, itr:Itr, questionid:str):	
		if not await ab_check(itr, self.client, is_guild=True, has_value="qotd_channel"):
			return
		
		questions = self.client.CON.get_value(itr.guild, "questions")
		removequestions = []
		if await ab_check_slient(itr, self.client, is_guild=True, has_mod_role=True):
			removequestions = [q for q in questions if q["id"] == questionid]
		else:
			removequestions = [q for q in questions if q["id"] == questionid and q["author"] == itr.user.id]
			
		if len(removequestions) == 0:
			await itr.response.send_message(embed=getComEmbed(str(itr.user), self.client, f"This question doesn't exist or you can't delete it."))
		else:
			questions = [q for q in questions if q["id"] != questionid]
			await self.client.CON.set_value(itr.guild, "questions", questions)
			await itr.response.send_message(embed=getComEmbed(str(itr.user), self.client, f"Removed question!", f"With id **{questionid}**"))

	@qotdgroup.command(name="edit", description="Modify one of your questions from the daily questions, Mods can modify anyones question.")
	@AC.describe(questionid="The ID of question you want to modify.", question="The modified question you want to ask.")
	async def edit(self, itr:Itr, questionid:str, question:str=""):	
		if not await ab_check(itr, self.client, is_guild=True, has_value="qotd_channel"):
			return
		
		questions = self.client.CON.get_value(itr.guild, "questions")
		editquestions = []
		if await ab_check_slient(itr, self.client, is_guild=True, has_mod_role=True):
			editquestions = [q for q in questions if q["id"] == questionid]
		else:
			editquestions = [q for q in questions if q["id"] == questionid and q["author"] == itr.user.id]
			
		if len(editquestions) == 0:
			await itr.response.send_message(embed=getComEmbed(str(itr.user), self.client, f"This question doesn't exist or you can't edit it."))
		else:
			if question == "":
				questions = [q for q in questions if q["id"] != questionid]
				await self.client.CON.set_value(itr.guild, "questions", questions)
				await itr.response.send_message(embed=getComEmbed(str(itr.user), self.client, f"Removed question!", f"With id **{questionid}**"))
			else:
				for q in questions:
					if q["id"] == questionid:
						q["question"] = question
				await self.client.CON.set_value(itr.guild, "questions", questions)
				await itr.response.send_message(embed=getComEmbed(str(itr.user), self.client, f"Edited question!", f"With id **{questionid}**"))

	@qotdgroup.command(name="reroll", description="Repost a question if the last one wasn't good.")
	@AC.describe(instant="If the reroll should have no vote (Mods only).")
	async def reroll(self, itr:Itr, instant:Literal["Yes","No"]):
		if not await ab_check(itr, self.client, is_guild=True, has_value="qotd_channel"):
			return
		if instant == "Yes" and ab_check_slient(itr, self.client, has_mod_role=True):
			await self.askQuestion(itr.guild, False, True)
			return

		votes = 1
		voters = [itr.user.id]
		threshold = self.client.CON.get_value(itr.guild, "qotd_reroll_threshold", guild=itr.guild)

		def getEmbed():
			view = discord.ui.View(timeout=None)
			view.add_item(discord.ui.Button(style=discord.ButtonStyle.blurple, label="Agree", custom_id="agree"))
			return getComEmbed(str(itr.user), self.client, f"{itr.user.name} is requesting a reroll, press here to agree!", f"Votes: {votes}/{threshold}"), view
		def getTimeoutEmbed():
			view = discord.ui.View(timeout=None)
			view.add_item(discord.ui.Button(style=discord.ButtonStyle.blurple, label="Agree", custom_id="agree", disabled=True))
			return getComEmbed(str(itr.user), self.client, f"{itr.user.name} requested a reroll, not enough votes!", f"Votes: {votes}/{threshold}"), view
		def getSuccessEmbed():
			view = discord.ui.View(timeout=None)
			view.add_item(discord.ui.Button(style=discord.ButtonStyle.blurple, label="Agree", custom_id="agree", disabled=True))
			return getComEmbed(str(itr.user), self.client, f"{itr.user.name} requested a reroll, got enough votes and rerolled!", f"Votes: {votes}/{threshold}"), view

		embed, view = getEmbed()
		await itr.response.send_message(embed=embed, view=view)
		MSG = await itr.original_response()

		def check(checkitr:Itr):
			try:
				return (checkitr.message.id == MSG.id)
			except:
				return False
		while True:
			try:
				butitr:Itr = await self.client.wait_for("interaction", timeout=150, check=check)
				await butitr.response.defer()
				if butitr.data["custom_id"] == "agree" and butitr.user.id not in voters:
					votes += 1
					voters.append(butitr.user.id)
			
				if votes >= threshold:
					embed, view = getSuccessEmbed()
					await itr.edit_original_response(embed=embed, view=view)
					break
				else:
					embed, view = getEmbed()
					await itr.edit_original_response(embed=embed, view=view)

			except asyncio.TimeoutError:
				embed, view = getTimeoutEmbed()
				await itr.edit_original_response(embed=embed, view=view)
				return
		
		await self.askQuestion(itr.guild, False, True)

	'''@qotdgroup.command(name="post", description="Forcefully post a question.")
	@AC.describe(dontremove="If the question isn't removed from the questions list.", dontping="If the question doesn't ping the qotd_role")
	async def post(self, itr:Itr, dontremove:Literal["True","False"], dontping:Literal["True","False"]):
		if not await ab_check(itr, self.client, is_owner=True, is_guild=True, has_value="qotd_channel"):
			return
		await self.askQuestion(itr.guild, tobool(dontremove), tobool(dontping))
		await itr.response.send_message("Question has been askified.")'''

def divide_chunks(l, n):
	for i in range(0, len(l), n):
		yield l[i:i + n]

async def setup(client:AidanBot):
	await client.add_cog(QOTDCog(client), guilds=client.debug_guilds)
