import discord
from discord.ext import commands

from random import seed
from random import randint

from functions import is_beta, getEmbed, addField, Error, getIntFromText

class GeneralCog(commands.Cog):
	def __init__(self, client):
		self.client = client

	@commands.command(description="Make me say something.")
	async def echo(self, ctx, *, text:str="sample text"):
		await ctx.message.delete()
		await ctx.send(text)

	@commands.command(description="Reply to a message.")
	async def reply(self, ctx, message_id:int=None, *, text:str="sample text"):
		if message_id == None:
			await Error(ctx, self.client, "Missing un-optional argument for command.")
			return

		MSG = await ctx.channel.fetch_message(message_id)
		await ctx.message.delete()
		await MSG.reply(text, mention_author=False)

	@commands.command(description="React to a message.")
	async def react(self, ctx, message_id:int=None, reaction:str="👋"):
		if message_id == None:
			await Error(ctx, self.client, "Missing un-optional argument for command.")
			return

		MSG = await ctx.channel.fetch_message(message_id)
		await ctx.message.delete()
		await MSG.add_reaction(reaction)

	@commands.command(description="Rates something.")
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

	@commands.command(description="Answers a question.")
	async def ask(self, ctx, *, question:str=None):
		seed(getIntFromText(question.lower()))

		if question == None:
			await Error(ctx, self.client, "Missing un-optional argument for command.")
			return

		# get start, really easy
		start = ["My heart tells me... ", "In all honestly, ", "hAH, ", "", "", ""]
		start_txt = start[randint(0, len(start)-1)]

		# get end, different if it caonatins "how many"
		if "how many" in question.lower():
			number = str(randint(0,10))
			end = [f"At least {number}.", f"More than {number}, for sure.", f"{number}.", f"Take it or leave it. {number}."]
		else:
			end = ["Yes.", "No, not at all.", "idk, maybe.", "Answer is unclear.", "You will find out soon enough...", "S-sorry, this questions is just... too much for me to handle.", "Maybe the true answer was inside you all along!", "What???"]

		end_txt = end[randint(0, len(end)-1)]

		emb = getEmbed(ctx, "Ask", start_txt + end_txt, "")
		await ctx.reply(embed=emb, mention_author=False)

	@commands.command(description="What percentage of something is you?")
	async def percent(self, ctx, something:str=None, *, person:str=None):
		if something == None:
			await Error(ctx, self.client, "Missing un-optional argument for command.")
			return

		if person == None:
			seed(getIntFromText(something.lower() + ctx.author.name))
		else:
			seed(getIntFromText(something.lower() + person))
			
		value = randint(0,100)

		end = ""
		if value == 0:
			end = "wow. 0%, didn't expect that."
		elif value == 100:
			end = "FULL HOUSE BABEY!"
		elif value == 69:
			end = "( ͡° ͜ʖ ͡°)"
		elif randint(1,3) == 3:
			endings = ["I don't make the rules.", "that isn't that bad when you think about it.", "LOL!", "¯\_(ツ)_/¯", "don't blame me, blame randint.", "sorry...", "i've seen worse don't worry.", "better than Aidan.", "I know, I know."]

			end = endings[randint(0, len(endings)-1)]

		if person == None:
			emb = getEmbed(ctx, "Percent", f"You are **{str(value)}%** {something}.", end)
		else:
			emb = getEmbed(ctx, "Percent", f"{person} is **{str(value)}%** {something}.", end)
		await ctx.reply(embed=emb, mention_author=False)

	@commands.command(description="Picks between given decisions.")
	async def decide(self, ctx, *, decisions=None):
		if decisions == None:
			await Error(ctx, self.client, "Missing un-optional argument for command.")
			return

		decisions = decisions.split(" ")
		emb = getEmbed(ctx, "Decide", "I choose... {0}".format(decisions[randint(0, len(decisions)-1)]), "")
		await ctx.reply(embed=emb, mention_author=False)

	@commands.command(description="Make a user say anoything you want.")
	async def clone(self, ctx, member:discord.User=None, *, message:str=None):
		if member == None or message == None:
			await Error(ctx, self.client, "Missing un-optional argument for command.")
			return
		
		webhook = await ctx.channel.create_webhook(name=member.name)
		await webhook.send(message, username=member.name + " (fake)", avatar_url=member.avatar_url)
		await webhook.delete()

	@commands.command(description="**Punish**.")
	async def punish(self, ctx):
		texts = [
			"AAAAAAAAAAAAAAAAAHHHHHHH!!!!!",
			"AAAHHH PLEASE STO-P!!!!",
			"I'M SORRY AHHHHHHH!!!",
			"PLEASE!... HAVE MERCY!...",
			"STOP...   *CRIES*", "AAAAAAHHHH!!!",
			"I'M SO SORRY.AAA!!!"
		]
		text = texts[randint(0, len(texts)-1)]

		await ctx.send("**" + text + "**")

def join(l, sep):
    out_str = ''
    for i, el in enumerate(l):
        out_str += '{}{}'.format(el, sep)
    return out_str[:-len(sep)]

def setup(client):
  client.add_cog(GeneralCog(client))
