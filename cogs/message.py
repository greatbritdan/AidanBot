import discord
from discord.commands import message_command

from random import choice

# only for message commands
class MessageCog(discord.Cog):
	def __init__(self, client):
		self.client = client

	@message_command(name="UwU")
	async def uwuify(self, ctx:AC, message:discord.Message):
		endings = [";;w;;", ";w;", "UwU", "OwO", ":3", "X3", "^_^", "\\* *sweats* *", "\\* *screams* *", "\\* *huggles tightly* *"]

		# start with owour message
		msg = message.clean_content

		# add some uwunique words
		repwords = {
			"love":"wuv", "cherish":"chwish",
			"Love":"Wuv", "Cherish":"Chwish",
			"LOVE":"WUV", "CHERISH":"CHWISH"
		}
		for repword in repwords:
			msg = replaceWord(msg,repword,repwords[repword])

		# add s-some dashes to make them s-seem nervowous
		mwords = msg.split()
		newmwords = []
		for i, v in enumerate(mwords):
			if randint(1,12) == 12:
				newmwords.append(v[0] + "-" + v)
			else:
				newmwords.append(v)
		msg = " ".join(newmwords)

		# make them sowounds wike a child
		msg = msg.replace("l","w").replace("r","w").replace("L","W").replace("R","W")
		msg = "*" + msg + "* " + choice(endings)

		# print(msg) # dowone
		await ctx.defer(ephemeral=True)
		try:
			await self.client.sendWebhook(ctx.channel, message.author, msg, [], " (fake)")
			await ctx.respond("UwUified!", ephemeral=True)
		except:
			await ctx.respond("Error! Try again later!", ephemeral=True)

def setup(client):
	client.add_cog(MessageCog(client))
