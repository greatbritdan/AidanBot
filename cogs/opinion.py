from discord import Option
from discord.ext import commands
from discord.commands import SlashCommandGroup

import time
from random import random, randint, seed, choice
from functions import getComEmbed, getIntFromText, getBar

class OpinionCog(commands.Cog):
	def __init__(self, client):
		self.client = client

	opiniongroup = SlashCommandGroup("opinion", "Opinion based commands.")

	@opiniongroup.command(name="rate", description="AidanBot will rate a thing.")
	async def rate(self, ctx, 
		thing:Option(str, "Thing AidanBot will rate.", required=True)
	):
		words = thing.split(" ")
		newords = []
		convertwords = {"your":"my", "you":"me", "yourself":"myself", "my":"your", "me":"you", "i":"you", "myself":"yourself","this":"that","these":"those","that":"this","those":"these"}
		removelist = [".",",","/","!","?","'",'"']
		for word in words:
			w = word.lower()
			for l in removelist:
				w = w.replace(l, "")
			if w in convertwords:
				word = word.lower().replace(w, convertwords[w])
			newords.append(word)

		thing = " ".join(newords)
		seed(getIntFromText(thing.lower()))
		responces = [
			["{0} is worse than anything i have ever rated.", [-10, -10]],
			["{0} is just awful, holy crap!", [-1, 0]],
			["{0} goes right into F tier.", [0, 2]],
			["{0} is really bad.", [0, 2]],
			["{0}? i can't say that with a straight mouth!", [0, 2]],
			["I have no opinion on {0}.", [2, 2]],
			["{0} is alright, but could be better.", [3, 5]],
			["{0} is pretty good!", [4, 6]],
			["{0} is neat!", [4, 6]],
			["{0} is great. Not the best tho.", [5, 8]],
			["Never seen it, but I like the sound of {0}!", [5, 8]],
			["{0} is amazing!", [7, 9]],
			["{0} is the best thing, by far.", [10, 10]],
			["I AM GOD", [11, 11]],
			["HE SUCKS SO GOD DAMN MUCH!!!!!", [-3888292929929922, -3888292929929922]]
		]

		# if it's aidanbot/aidanbetabot or aidan, respond differently
		index = randint(0, 12)
		thung = thing.lower()
		if self.client.isbeta:
			if thung == "aidanbetabot" or thung == "me":
				index = 13
			elif thung == "aidanbot":
				index = 14
		else:
			if thung == "aidanbot" or thung == "me":
				index = 13
			elif thung == "aidanbetabot":
				index = 14

		txt = responces[index][0]
		rating = randint(responces[index][1][0], responces[index][1][1])
		embed = getComEmbed(ctx, self.client, txt.format(thing), f"**Score:** `{rating}/10`")
		await ctx.respond(embed=embed)

	@opiniongroup.command(name="percent", description="AidanBot will say what part of something is something.")
	async def percent(self, ctx, 
		something:Option(str, "The something.", required=True),
		someone:Option(str, "The someone.", default="False")
	):
		if someone == "False":
			seed(getIntFromText(something.lower() + ctx.author.name.lower()))
		else:
			seed(getIntFromText(something.lower() + someone.lower()))
		value = randint(0,100)
		end = getBar(value, 100, 10, True)
		
		embed = False
		if someone == "False":
			embed = getComEmbed(ctx, self.client, f"You are **{str(value)}%** {something}.", end)
		else:
			embed = getComEmbed(ctx, self.client, f"{someone} is **{str(value)}%** {something}.", end)
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
			seed(getIntFromText(question.lower()))
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
		option1:Option(str, "Option 1.", required=True),
		option2:Option(str, "Option 2.", required=True),
		option3:Option(str, "Option 3.", required=False),
		option4:Option(str, "Option 4.", required=False),
		option5:Option(str, "Option 5.", required=False),
		option6:Option(str, "Option 6.", required=False),
		option7:Option(str, "Option 7.", required=False),
		option8:Option(str, "Option 8.", required=False)
	):
		opts = [option1, option2, option3, option4, option5, option6, option7, option8]
		options = [i for i in opts if i]
		embed = getComEmbed(ctx, self.client, f"I choose... {choice(options)}")
		await ctx.respond(embed=embed)

def str_time_prop(start, end, time_format):
    stime = time.mktime(time.strptime(start, time_format))
    etime = time.mktime(time.strptime(end, time_format))
    ptime = stime + random() * (etime - stime)
    return time.strftime(time_format, time.localtime(ptime))

def random_date(start, end):
    return str_time_prop(start, end, '%m/%d/%Y %I:%M %p')

def setup(client):
	client.add_cog(OpinionCog(client))