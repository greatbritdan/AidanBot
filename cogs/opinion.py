from http.client import responses
import discord
from discord.commands import SlashCommandGroup
from discord import Option

import time, hashlib, re
import emoji as em
from datetime import date
from random import random, randint, seed, choice
from functions import getComEmbed, getIntFromText, getBar

def getLikeness(string):
	days = date.today() - date(2022,6,28)
	num = int(hashlib.sha512(string.encode()).hexdigest(), 16)+days.days
	seed(num)
	return randint(0,100)

def limitLikeness(score, newhigh):
	return round(score/(100/newhigh))

def replaceWord(text, find, replace):
	return re.sub(r"\b" + find + r"\b", replace, text)

class OpinionCog(discord.Cog):
	def __init__(self, client):
		self.client = client

	opiniongroup = SlashCommandGroup("opinion", "Opinion based commands.")

	'''@opiniongroup.command(name="likeness", description="Get your likeness score.")
	async def likeness(self, ctx, 
		thing:Option(str, "Thing to get likeness score of. Defaults to you", required=False)
	):
		thing = thing or str(ctx.author)
		await ctx.respond(f"Likeness score for '{thing}': {getLikeness(thing)}")'''

	@opiniongroup.command(name="rate", description="AidanBot will rate a thing.")
	async def rate(self, ctx, 
		thing:Option(str, "Thing AidanBot will rate.", required=True)
	):
		thing = thing.lower()
		repwords = {"your":"my","you":"me","yourself":"myself","my":"your","me":"you","i":"you","myself":"yourself","this":"that","these":"those","that":"this","those":"these"}
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

		embed = getComEmbed(ctx, self.client, response.format(thing), f"**Score:** `{score}/10`")
		await ctx.respond(embed=embed)

	@opiniongroup.command(name="percent", description="AidanBot will say what part of something is something.")
	async def percent(self, ctx, 
		something:Option(str, "The something.", required=True),
		someone:Option(str, "The someone.", default="False")
	):
		if someone == "False":
			score = getLikeness(something.lower() + ":" + ctx.author.name.lower())
		else:
			score = getLikeness(something.lower() + ":" + someone.lower())
		end = getBar(score, 100, 10, True)
		embed = False
		if someone == "False":
			embed = getComEmbed(ctx, self.client, f"You are **{str(score)}%** {something}.", end)
		else:
			embed = getComEmbed(ctx, self.client, f"{someone} is **{str(score)}%** {something}.", end)
		await ctx.respond(embed=embed)

	@opiniongroup.command(name="ask", description="AidanBot will answer your burning questions.")
	async def ask(self, ctx, 
		question:Option(str, "The question you ask.", required=True)
	):
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
		embed = getComEmbed(ctx, self.client, fields=[["Question:", question], ["Answer:", fullans]])
		await ctx.respond(embed=embed)

	@opiniongroup.command(name="decide", description="AidanBot will decide on something for you.")
	async def decide(self, ctx, 
		options:Option(str, "All the options sepperated by commas", required=True),
	):
		options = [i.strip() for i in options.split(",") if i]
		embed = getComEmbed(ctx, self.client, f"I choose... {choice(options)}")
		await ctx.respond(embed=embed)

	@opiniongroup.command(name="tierlist", description="AidanBot will make a tier list to piss you off.")
	async def tierlist(self, ctx,
		options:Option(str, "All the options sepperated by commas", required=True),
	):
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

		tieremojisidx = ["s","a","b","c","d","e","f"]
		tieremojis = { "s":"<:tierS:980025543816781904>", "a":"<:tierA:980025543732891648>", "b":"<:tierB:980025543858733126>", "c":"<:tierC:980025543959408671>", "d":"<:tierD:980025543514800160>", "e":"<:tierE:980025543837757500>", "f":"<:tierF:980025543560953867>" }
		tiers = {"s":[], "a":[], "b":[], "c":[], "d":[], "e":[], "f":[]}
		def makeTierList():
			tierlist = ""
			for tier in tiers:
				tierlist += f"{tieremojis[tier]}`:` {', '.join(tiers[tier])}\n"
			return tierlist

		flippyflop = [6,5,4,3,2,1,0]
		for option in options:
			tier = limitLikeness(getLikeness(em.core.demojize(option).lower()),6)
			tiers[tieremojisidx[flippyflop[tier]]].append(option)
		
		emb = getComEmbed(ctx, self.client, "Tier List", makeTierList())
		await ctx.respond(embed=emb)

def str_time_prop(start, end, time_format):
    stime = time.mktime(time.strptime(start, time_format))
    etime = time.mktime(time.strptime(end, time_format))
    ptime = stime + random() * (etime - stime)
    return time.strftime(time_format, time.localtime(ptime))

def random_date(start, end):
    return str_time_prop(start, end, '%m/%d/%Y %I:%M %p')

def setup(client):
	client.add_cog(OpinionCog(client))