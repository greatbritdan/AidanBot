import discord
import discord.ext.commands as CM
import discord.app_commands as AC
from discord import Interaction as Itr
from discord.utils import format_dt

import time, hashlib, re, asyncio, datetime
import emoji as em
from random import random, randint, seed, choice

from aidanbot import AidanBot
from functions import getComEmbed, getBar
from cooldowns import cooldown_opinion

def getLikeness(string):
	days = datetime.date.today() - datetime.date(2022,6,28)
	num = int(hashlib.sha512(string.encode()).hexdigest(), 16)+days.days
	seed(num)
	return randint(0,100)
def limitLikeness(score, newhigh):
	return round(score/(100/newhigh))
def replaceWord(text, find, replace):
	return re.sub(r"\b" + find + r"\b", replace, text)

class OpinionCog(CM.Cog):
	def __init__(self, client:AidanBot):
		self.client = client

	opiniongroup = AC.Group(name="opinion", description="Commands to do with opinion.")

	'''@opiniongroup.command(name="likeness", description="Get your likeness score.")
	@AC.describe(thing="Thing to get likeness score of. Defaults to you")
	async def likeness(self, itr, thing:str=None):
		thing = thing or str(itr.user)
		await itr.response.send_message(f"Likeness score for '{thing}': {getLikeness(thing)}")'''

	@opiniongroup.command(name="rate", description="I will rate a thing.")
	@AC.describe(thing="Thing I will rate.")
	@CM.dynamic_cooldown(cooldown_opinion, CM.BucketType.user)
	async def rate(self, itr:Itr, thing:str):
		repwords = {
			"your":"my","you":"me","yourself":"myself","my":"your","me":"you","i":"you","myself":"yourself","this":"that","these":"those","that":"this","those":"these",
			"Your":"My","You":"Me","Yourself":"Myself","My":"Your","Me":"You","Myself":"Yourself","This":"That","These":"Those","That":"This","Those":"These",
			"YOUR":"MY","YOU":"ME","YOURSELF":"MYSELF","MY":"YOUR","ME":"YOU","I":"YOU","MYSELF":"YOURSELF","THIS":"THAT","THESE":"THOSE","THAT":"THIS","THOSE":"THESE"
		}
		for name in repwords:
			thing = replaceWord(thing,name,repwords[name])

		responses = {
			"0": ["{0} is the worst thing I have ever rated.", "{0}? I feel sick...", "{0} is not even so bad it's funny...", "{0} is... awful... in every way."],
			"1": ["{0} is not the worst, that's the only good thing i can say.", "I prefer {0} over 2020. IG", "{0} is not awful, but still utterly disgusting!"],
			"2": "1",
			"3": ["{0} isn't great, but i can handle it.", "{0} is ok on a rainy day.", "There are things much better than {0} but also much worse things."],
			"4": "3",
			"5": ["{0} is ok. Just ok.", "I like {0} from time to time.", "I'm mutural on {0}.", "{0} is, pretty good."],
			"6": "5",
			"7": ["I really like {0}!", "{0} is quite good.", "There are better things than {0} but overall it's good.", "{0} is very good!"],
			"8": "7",
			"9": ["{0} is great, really great!", "{0} is a top pick for sure!", "{0} is almost perfect.", "{0} is amazing!!"],
			"10": ["I love {0}, it's incredible!", "{0} is a top pick for sure!!", "{0}? 10/10, enough said.", "{0} is just, the best thing."]
		}

		score = limitLikeness(getLikeness(thing),10)
		r = responses[str(score)]
		response = choice(responses[r]) if type(r) == str else choice(r)

		embed = getComEmbed(str(itr.user), self.client, response.format(thing), f"**Score:** `{score}/10`")
		await itr.response.send_message(embed=embed)

	@opiniongroup.command(name="percent", description="I will say what part of something is something.")
	@AC.describe(something="The something.", someone="The someone.")
	@CM.dynamic_cooldown(cooldown_opinion, CM.BucketType.user)
	async def percent(self, itr:Itr, something:str, someone:str="False"):
		if someone == "False":
			score = getLikeness(something.lower() + ":" + itr.user.name.lower())
		else:
			score = getLikeness(something.lower() + ":" + someone.lower())
		end = getBar(score, 100, 10, True)
		embed = False
		if someone == "False":
			embed = getComEmbed(str(itr.user), self.client, f"You are **{str(score)}%** {something}.", end)
		else:
			embed = getComEmbed(str(itr.user), self.client, f"{someone} is **{str(score)}%** {something}.", end)
		await itr.response.send_message(embed=embed)

	@opiniongroup.command(name="ask", description="I will answer your burning questions.")
	@AC.describe(question="The question you ask.")
	@CM.dynamic_cooldown(cooldown_opinion, CM.BucketType.user)
	async def ask(self, itr:Itr, question:str):
		starts = []
		answers = []
		answer = ""
		start = ""
		getseed = True
		question = question.lower()
		if question.startswith("how many"):
			num = str(randint(0, 20))
			starts = ["OH! ", "my stupid heart tells me ", "uhhhhh, ", "imho, ", "", "", ""]
			answers = [f"100% not {num}!", f"at least {num} idfk...", f"{num}, take it or leave it.", f"i know this one, {num}."]
		elif question.startswith("why"):
			if "you" in question:
				answers = ["i did no such thing.", "no comment.", "that's crazy and false... yeah."]
			else:
				answers = ["beacuse... yes.", "i have been warned not to give an answer...", "why not? lol!"]
		elif question.startswith("where"):
			starts = ["how do i put this... ", "my stupid heart tells me ", "uhhhhh, ", "", ""]
			answers = ["Aidan's basement.", "my attic.", "Brazil!", "China.", "the middle of the ocean.", "somewhere idk...", "gone, never to be found again...", "Britan!", "The void..."]
		elif question.startswith("when"):
			if question.startswith("when will") or question.startswith("when is"):
				answer = random_date("1/1/2022 12:00 AM", "1/1/2122 12:00 AM")
			else:
				answer = random_date("1/1/2000 12:00 AM", "1/1/2021 12:00 AM")
		else:
			starts = ["how do i put this... ", "my stupid heart tells me ", "uhhhhh, ", "actually. ", "", "", ""]
			answers = ["ye.", "no.", "absolutely not!", "HAH, NO WAY AT ALL.", "maybe, probably...", "uhhh, it's unlikely", "i can't tell, sorry."]

		if getseed:
			getLikeness(question.lower())
		if len(answers) > 0:
			answer = answers[randint(0, len(answers)-1)]
		if len(starts) > 0:
			start = starts[randint(0, len(starts)-1)]
			
		fullans = start + answer
		allbutone = len(fullans)-1
		fullans = fullans[:-allbutone].capitalize() + fullans[1:]
		embed = getComEmbed(str(itr.user), self.client, fields=[["Question:", question], ["Answer:", fullans]])
		await itr.response.send_message(embed=embed)

	@opiniongroup.command(name="decide", description="I will decide on something for you.")
	@AC.describe(options="All the options sepperated by commas.")
	@CM.dynamic_cooldown(cooldown_opinion, CM.BucketType.user)
	async def decide(self, itr:Itr, options:str):
		options = [i.strip() for i in options.split(",") if i]
		embed = getComEmbed(str(itr.user), self.client, f"I choose... {choice(options)}")
		await itr.response.send_message(embed=embed)

	@opiniongroup.command(name="tierlist", description="I will make a tier list to annoy you lol.")
	@AC.describe(options="All the options sepperated by commas.", tiers="List of tier names/emojis (CAN'T HAVE BOTH) sepperated by commas.")
	@CM.dynamic_cooldown(cooldown_opinion, CM.BucketType.user)
	async def tierlist(self, itr:Itr, options:str, tiers:str=None):
		allemoji = True
		if tiers:
			tieremojisidx = []
			tieremojis = {}
			tierlists = {}
			
			tierssplit = [i.strip() for i in tiers.split(",") if i]
			if (len(tierssplit) < 2 or len(tierssplit) > 10) and (not self.client.aidan == itr.user.id):
				return await itr.response.send_message("Invalid number of tiers! There must be at least 2 and no more than 10!")
			
			for tier in tierssplit:
				if not "<" in tier:
					allemoji = False
				tieremojisidx.append(tier)
				tieremojis[tier] = tier
				tierlists[tier] = []

			if not allemoji:
				tiermax = 0
				for tier in tierssplit:
					if len(tier) > tiermax:
						tiermax = len(tier)
		else:
			tieremojisidx = ["s","a","b","c","d","e","f"]
			tieremojis = { "s":"<:tierS:980025543816781904>", "a":"<:tierA:980025543732891648>", "b":"<:tierB:980025543858733126>", "c":"<:tierC:980025543959408671>", "d":"<:tierD:980025543514800160>", "e":"<:tierE:980025543837757500>", "f":"<:tierF:980025543560953867>" }
			tierlists = {"s":[], "a":[], "b":[], "c":[], "d":[], "e":[], "f":[]}

		opts = [i.strip() for i in options.split(",") if i]
		options = []
		for opt in opts:
			emoji = em.core.distinct_emoji_lis(opt)
			if len(emoji) > 0:
				options.append(emoji[0])
			else:
				options.append(opt)
			
		def sort(e):
			if ":" in em.core.demojize(e):
				return 1
			return 2
		options.sort(key=sort)

		def makeTierList():
			tierlist = ""
			for tier in tierlists:
				if allemoji:
					tierlist += f"{tieremojis[tier]}`:` {', '.join(tierlists[tier])}\n"
				else:
					name = tieremojis[tier]
					while len(name) < tiermax:
						name += " "
					tierlist += f"`{name}:` {', '.join(tierlists[tier])}\n"

			return tierlist

		tiercount = len(tieremojisidx)-1
		for option in options:
			if tiercount == 0:
				tier = 0
			else:
				tier = (-limitLikeness(getLikeness(em.core.demojize(option).lower()),tiercount))+tiercount
			tierlists[tieremojisidx[tier]].append(option)
		
		emb = getComEmbed(str(itr.user), self.client, "Tier List", makeTierList())
		await itr.response.send_message(embed=emb)

	@opiniongroup.command(name="poll", description="Create a poll for people to vote on.")
	@AC.describe(question="The question you are asking.", answers="LAll the answers sepperated by commas.", duration="The timelimit of the poll.")
	@CM.dynamic_cooldown(cooldown_opinion, CM.BucketType.user)
	async def poll(self, itr:Itr, question:str, answers:str, duration:AC.Range[int,30,1500]):
		answers = [i.strip() for i in answers.split(",")]
		if (len(answers) < 2 or len(answers) > 10) and (not self.client.aidan == itr.user.id):
			return await itr.response.send_message("Invalid number of answers! There must be at least 2 and no more than 10!")
		if len(answers) != len(set(answers)):
			return await itr.response.send_message("Invalid answers! It can not contain duplicates!")
		if "_end_" in answers or "_revoke_" in answers:
			return await itr.response.send_message("Invalid answers! It can not contain system button names (`_end_` & `_revoke_`)!")
		totalvotes = 0
		votes = [0 for i in answers]
		votesusers = {}

		strmax = 0
		for a in answers:
			if len(a) > strmax:
				strmax = len(a)

		def now():
			return datetime.datetime.now()

		endtime = now() + datetime.timedelta(seconds=duration)
		def getPollEmbed(timeout=False):
			txt = ""
			view = discord.ui.View(timeout=None)
			for i in range(0, len(answers)):
				ans = answers[i]
				while len(ans) < strmax:
					ans += " "

				percent = 0
				if totalvotes > 0:
					percent = round((100/totalvotes)*votes[i])

				bar = getBar(percent, 100, 10, True)
				txt += f"`{ans}:` {bar} **({str(percent)}%) ({votes[i]} votes)**\n"

				view.add_item( discord.ui.Button(label=answers[i], style=discord.ButtonStyle.blurple, custom_id=answers[i], disabled=timeout) )
			
			view.add_item( discord.ui.Button(label="Remove Vote", style=discord.ButtonStyle.gray, custom_id="_revoke_", disabled=timeout, row=2) )
			view.add_item( discord.ui.Button(label="End Poll (Author only)", style=discord.ButtonStyle.red, custom_id="_end_", disabled=timeout, row=2) )

			quest = question + " (finished)" if timeout else question

			if timeout:
				txt = txt + f"\n**Total Votes**: {totalvotes}\n**Duration**: {duration} Seconds."
			else:
				txt = txt + f"\n**Total Votes**: {totalvotes}\n**Time Remaining**: {format_dt(endtime,'R')}"

			embed = getComEmbed(str(itr.user), self.client, quest, txt)
			return embed, view

		embed, view = getPollEmbed()
		await itr.response.send_message(embed=embed, view=view)
		MSG = await itr.original_response()

		def check(checkitr:Itr):
			try:
				return (checkitr.message.id == MSG.id)
			except:
				return False
		start = now()
		while True:
			try:
				seconds = ((start+datetime.timedelta(seconds=duration))-now()).seconds # but hacky but it works
				butitr:Itr = await self.client.wait_for("interaction", timeout=seconds, check=check)

				await butitr.response.defer()
				if butitr.data["custom_id"] == "_revoke_":
					if str(butitr.user.id) in votesusers:
						votes[votesusers[str(butitr.user.id)]] -= 1
						votesusers.pop(str(butitr.user.id))
						totalvotes -= 1
				elif butitr.data["custom_id"] == "_end_":
					if butitr.user.id == itr.user.id:
						embed, view = getPollEmbed(True)
						await itr.edit_original_response(embed=embed, view=view)
						return
				else:
					if str(butitr.user.id) in votesusers: # change vote
						votes[votesusers[str(butitr.user.id)]] -= 1
					else:
						totalvotes += 1 # first vote

					for i in range(0, len(answers)):
						if answers[i] == butitr.data["custom_id"]:
							votesusers[str(butitr.user.id)] = i
							votes[i] += 1
							break
				
				embed, view = getPollEmbed()
				await itr.edit_original_response(embed=embed, view=view)
			except asyncio.TimeoutError:
				embed, view = getPollEmbed(True)
				await itr.edit_original_response(embed=embed, view=view)
				
def str_time_prop(start, end, time_format):
	stime = time.mktime(time.strptime(start, time_format))
	etime = time.mktime(time.strptime(end, time_format))
	ptime = stime + random() * (etime - stime)
	return time.strftime(time_format, time.localtime(ptime))

def random_date(start, end):
	return str_time_prop(start, end, '%m/%d/%Y %I:%M %p')

async def setup(client:AidanBot):
	await client.add_cog(OpinionCog(client), guilds=client.debug_guilds)