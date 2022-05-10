from discord.ext import commands

from random import choice

# only for message commands
class MessageCog(commands.Cog):
	def __init__(self, client):
		self.client = client

	@commands.message_command(name="Raw")
	async def raw(self, ctx, message):
		msg = message.clean_content.replace("`","'")
		await ctx.respond(f"Raw text from this message:```{msg}```", ephemeral=True)
	
	@commands.message_command(name="UwU")
	async def uwuify(self, ctx, message):
		endings = ["UwU", "OwO", ":3", "X3"]
		msg = message.clean_content.replace("l","w").replace("r","w")
		msg = "*" + msg + " " + choice(endings) + "*"
		await ctx.respond(msg)

def setup(client):
	client.add_cog(MessageCog(client))