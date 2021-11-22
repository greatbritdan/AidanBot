import discord
from discord.ext import commands

import time
import random
import asyncio
from random import seed, choice, randint

from functions import getComEmbed, ComError, getIntFromText, getBar

import json
with open('./commanddata.json') as file:
	temp = json.load(file)
	DESC = temp["desc"]

class OpinionCog(commands.Cog):
	def __init__(self, client):
		self.client = client

	@commands.command(description=DESC["rate"])
	@commands.cooldown(1, 5)
	async def rate(self, ctx, *, thing=None):
		if thing.lower() == "me":
			thing = ctx.author.name
		elif thing.lower() == "this server":
			thing = ctx.guild.name

		words = thing.split(" ")
		newords = []
		for word in words:
			if word == "your":
				newords.append("my")
			elif word == "you":
				newords.append("me")
			elif word == "yourself":
				newords.append("myself")
			elif word == "my":
				newords.append("your")
			elif word == "me" or word == "i":
				newords.append("you")
			elif word == "myself":
				newords.append("yourself")
			else:
				newords.append(word)

		thing = " "
		thing = thing.join(newords)

		seed(getIntFromText(thing.lower()))

		responces = [
			["{0} is worse than anything i have ever rated.", [-10, -10]],
			["{0} is just awful, holy crap!", [-1, 0]],
			["{0} goes right into F tier.", [0, 2]],
			["{0} is really bad.", [0, 2]],
			["I have no opinion on {0}.", [2, 2]],
			["{0}? i can't say that with a straight mout-, uhh hole?", [1, 3]],
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

		emb = getComEmbed(ctx, self.client, "Rate", txt.format(thing), fields=[["Score", "`{0}/10`".format(rating)]])
		await ctx.reply(embed=emb, mention_author=False)

	@commands.command(description=DESC["ask"])
	@commands.cooldown(1, 5)
	async def ask(self, ctx, *, question):
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
		elif question.startswith("who"):
			starts = ["i'll go for... ", "100% ", "Yeah that has to be ", "hmm... ", "that's easy, ", ""]
			member = ctx.guild.members[randint(0, len(ctx.guild.members)-1)]
			answer = member.display_name
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
		elif question.startswith("what command"):
			prefix = self.client.PREFIX
			starts = ["i'll go for... ", "100% ", "Yeah that has to be ", "hmm... ", "that's easy, ", ""]
			coms = []
			for command in self.client.commands:
				coms.append(command.name)
			answer = prefix + coms[randint(0, len(coms)-1)]
			getseed = False
		elif question.startswith("what role"):
			starts = ["i'll go for... ", "100% ", "Yeah that has to be ", "hmm... ", "that's easy, ", ""]
			roles = []
			for role in ctx.guild.roles:
				roles.append(role.name)
			answer = roles[randint(0, len(roles)-1)]
			getseed = False
		elif question.startswith("what channel"):
			starts = ["i'll go for... ", "100% ", "Yeah that has to be ", "hmm... ", "that's easy, ", ""]
			channels = []
			for channel in ctx.guild.text_channels:
				if not (channel.category.name.lower() == "archive" or channel.category.name.lower() == "the hidden ones"):
					channels.append(channel.name)
			answer = channels[randint(0, len(channels)-1)]
			getseed = False
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
		emb = getComEmbed(ctx, self.client, "Ask", fullans)
		await ctx.reply(embed=emb, mention_author=False)

	@commands.command(description=DESC["percent"])
	@commands.cooldown(1, 5)
	async def percent(self, ctx, something, *, person=None):
		if person == None:
			seed(getIntFromText(something.lower() + ctx.author.name))
		else:
			seed(getIntFromText(something.lower() + person))

		value = randint(0,100)
		end = getBar(value, 100, 10, True)
		if person == None:
			emb = getComEmbed(ctx, self.client, "Percent", f"You are **{str(value)}%** {something}.", end)
		else:
			emb = getComEmbed(ctx, self.client, "Percent", f"{person} is **{str(value)}%** {something}.", end)
		await ctx.reply(embed=emb, mention_author=False)

	@commands.command(description=DESC["decide"])
	@commands.cooldown(1, 5)
	async def decide(self, ctx, *decisions):
		if decisions == None:
			await ComError(ctx, self.client, "Decision needs more than 0 choices.")
			return
			
		emb = getComEmbed(ctx, self.client, "Decide", f"I choose... {choice(decisions)}")
		await ctx.reply(embed=emb, mention_author=False)

	@commands.command(description=DESC["poll"])
	@commands.cooldown(1, 5)
	async def poll(self, ctx, question, *options):
		total = 0
		strmax = 0
		results = []
		usersvoted = []
		for op in options:
			if len(op) > strmax:
				strmax = len(op)
			results.append(0)

		def getPollEmbed(timeout=False):
			desc = ""
			buts = []
			for i in range(0, len(results)):
				txt = options[i]
				while len(txt) < strmax:
					txt += " "
				percent = 0
				if total > 0:
					percent = round((100/total)*results[i])

				bar = getBar(percent, 100, 10, True)
				desc = desc + f"`{txt}:` {bar} **({str(percent)}%) ({results[i]} votes)**\n"

				buts.append( discord.ui.Button(label=options[i], style=discord.ButtonStyle.blurple, custom_id=options[i], disabled=timeout) )
			desc = desc + f"**Total votes**: {total}"
			if timeout:
				emb = getComEmbed(ctx, self.client, "Poll (timeout)", question, desc)
			else:
				emb = getComEmbed(ctx, self.client, "Poll", question, desc)
			buttons = discord.ui.View(*buts)
			return emb, buttons

		emb, buttons = getPollEmbed()
		MSG = await ctx.send(embed=emb, view=buttons)

		def check(interaction):
			return (interaction.message.id == MSG.id)

		while True:
			try:
				interaction = await self.client.wait_for("interaction", timeout=60, check=check)

				if interaction.user.id not in usersvoted:
					usersvoted.append(interaction.user.id)
					for i in range(0, len(results)):
						if options[i] == interaction.data["custom_id"]:
							results[i] += 1
							total += 1
							break

				emb, buttons = getPollEmbed()
				await MSG.edit(embed=emb, view=buttons)

			except asyncio.TimeoutError:
				emb, buttons = getPollEmbed(True)
				await MSG.edit(embed=emb, view=buttons)

def str_time_prop(start, end, time_format):
    stime = time.mktime(time.strptime(start, time_format))
    etime = time.mktime(time.strptime(end, time_format))
    ptime = stime + random.random() * (etime - stime)
    return time.strftime(time_format, time.localtime(ptime))

def random_date(start, end):
    return str_time_prop(start, end, '%m/%d/%Y %I:%M %p')

def setup(client):
	client.add_cog(OpinionCog(client))