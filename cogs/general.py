import discord
from discord.ext import commands

import time
import random
from random import seed, randint

from functions import get_prefix, is_beta, getEmbed, addField, Error, getIntFromText, getBar

import json
with open('./desc.json') as file:
    DESC = json.load(file)

class GeneralCog(commands.Cog):
	def __init__(self, client):
		self.client = client

	@commands.command(description=DESC["echo"])
	@commands.cooldown(1, 6, commands.BucketType.channel)
	async def echo(self, ctx, *, text:str="sample text"):
		if "love" in text:
			await ctx.send("***no***")
			return

		await ctx.message.delete()
		await ctx.send(text)

	@commands.command(description=DESC["react"])
	@commands.cooldown(1, 6, commands.BucketType.channel)
	async def react(self, ctx, message_id:int=None, reaction:str="👋"):
		if message_id == None:
			await Error(ctx, self.client, "Missing un-optional argument for command.")
			return

		MSG = await ctx.channel.fetch_message(message_id)
		await ctx.message.delete()
		await MSG.add_reaction(reaction)

	@commands.command(description=DESC["rate"])
	@commands.cooldown(1, 6, commands.BucketType.user)
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
		if is_beta():
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

		emb = getEmbed(ctx, "Rate", txt.format(thing), "")
		emb = addField(emb, "Score", "`{0}/10`".format(rating))
		await ctx.reply(embed=emb, mention_author=False)

	@commands.command(description=DESC["ask"])
	@commands.cooldown(1, 6, commands.BucketType.user)
	async def ask(self, ctx, *, question:str=None):
		if question == None:
			await Error(ctx, self.client, "Missing un-optional argument for command.")
			return
		seed(getIntFromText(question.lower()))

		starts = []
		answers = []
		answer = ""
		start = ""
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
			prefix = get_prefix()
			starts = ["i'll go for... ", "100% ", "Yeah that has to be ", "hmm... ", "that's easy, ", ""]
			coms = []
			for command in self.client.commands:
				coms.append(command.name)
			answer = prefix + coms[randint(0, len(coms)-1)]
		else:
			starts = ["how do i put this... ", "my stupid heart tells me ", "uhhhhh, ", "actually. ", "", "", ""]
			answers = ["ye.", "no.", "absolutely not!", "HAH, NO WAY AT ALL.", "maybe, probably...", "uhhh, it's unlikely", "i can't tell, sorry."]

		if len(answers) > 0:
			answer = answers[randint(0, len(answers)-1)]
		if len(starts) > 0:
			start = starts[randint(0, len(starts)-1)]

		fullans = start + answer
		allbutone = len(fullans)-1
		fullans = fullans[:-allbutone].capitalize() + fullans[1:]
		emb = getEmbed(ctx, "Ask", fullans, "")
		await ctx.reply(embed=emb, mention_author=False)

	@commands.command(description=DESC["percent"])
	@commands.cooldown(1, 6, commands.BucketType.user)
	async def percent(self, ctx, something:str=None, *, person:str=None):
		if something == None:
			await Error(ctx, self.client, "Missing un-optional argument for command.")
			return
		if person == None:
			seed(getIntFromText(something.lower() + ctx.author.name))
		else:
			seed(getIntFromText(something.lower() + person))

		value = randint(0,100)
		end = getBar(value, 100, 10, True)
		if person == None:
			emb = getEmbed(ctx, "Percent", f"You are **{str(value)}%** {something}.", end)
		else:
			emb = getEmbed(ctx, "Percent", f"{person} is **{str(value)}%** {something}.", end)
		await ctx.reply(embed=emb, mention_author=False)

	@commands.command(description=DESC["decide"])
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def decide(self, ctx, *decisions):
		if decisions == None:
			await Error(ctx, self.client, "Missing un-optional argument for command.")
			return

		# decisions = decisions.split(" ")
		emb = getEmbed(ctx, "Decide", "I choose... {0}".format(decisions[randint(0, len(decisions)-1)]), "")
		await ctx.reply(embed=emb, mention_author=False)

	@commands.command(description=DESC["clone"])
	@commands.cooldown(1, 6, commands.BucketType.user)
	async def clone(self, ctx, member:discord.Member=None, *, message:str=None):
		if member == None or message == None:
			await Error(ctx, self.client, "Missing un-optional argument for command.")
			return
		
		webhook = await ctx.channel.create_webhook(name=member.name)
		await webhook.send(message, username=member.name + " (fake)", avatar_url=member.display_avatar.url)
		await webhook.delete()

	@commands.command(description=DESC["punish"])
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def punish(self, ctx):
		texts = [
			"AAAAAAAAAAAAAAAAAHHHHHHH!!!!!", "AAAHHH PLEASE STO-P!!!!", "I'M SORRY AHHHHHHH!!!",
			"PLEASE!... HAVE MERCY!...", "STOP...   *CRIES*", "AAAAAAHHHH!!!", "I'M SO SORRY.AAA!!!"
		]
		text = texts[randint(0, len(texts)-1)]
		await ctx.send("**" + text + "**")
    
def str_time_prop(start, end, time_format):
    """Get a time at a proportion of a range of two formatted times.

    start and end should be strings specifying times formatted in the
    given format (strftime-style), giving an interval [start, end].
    prop specifies how a proportion of the interval to be taken after
    start.  The returned time will be in the specified format.
    """

    stime = time.mktime(time.strptime(start, time_format))
    etime = time.mktime(time.strptime(end, time_format))

    ptime = stime + random.random() * (etime - stime)

    return time.strftime(time_format, time.localtime(ptime))

def random_date(start, end):
    return str_time_prop(start, end, '%m/%d/%Y %I:%M %p')

def setup(client):
  client.add_cog(GeneralCog(client))