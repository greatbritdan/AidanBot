from discord.ext import commands
from discord.utils import get

import asyncio

from functions import Error, getEmbed

def is_pipon_palace(ctx):
	return (ctx.guild.id == 836936601824788520)

class PPCog(commands.Cog):
	def __init__(self, client):
		self.client = client

	@commands.command(description="Create an emote from an image that you can use in the server with NQN.")
	@commands.check(is_pipon_palace)
	async def emoteify(self, ctx, name=None):
		if name == None or len(ctx.message.attachments) < 1:
			await Error(ctx, self.client, "Missing un-optional argument for command.")
			return

		guild = get(self.client.guilds, id=879063875469860874)
		image = await ctx.message.attachments[0].read()
		emoji = await guild.create_custom_emoji(name=name, image=image)

		await ctx.send(emoji)
		
def setup(client):
  client.add_cog(PPCog(client))
