import discord
from discord.ext import commands
from discord.utils import get

from random import choice

from functions import ComError

import json
with open('./commanddata.json') as file:
	temp = json.load(file)
	DESC = temp["desc"]

def is_pipon_palace(ctx):
	return (ctx.guild.id == 836936601824788520)

class PPCog(commands.Cog):
	def __init__(self, client):
		self.client = client

	@commands.command(description=DESC["emoteify"])
	@commands.check(is_pipon_palace)
	@commands.cooldown(1, 10)
	async def emoteify(self, ctx, name, addtomain:bool=False):
		if len(ctx.message.attachments) < 1:
			await ComError(ctx, self.client, "Needs attachment.")
			return

		if addtomain and ctx.author.id == self.client.owner_id:
			guild = ctx.guild
		else:
			guild = get(self.client.guilds, id=879063875469860874)
		image = await ctx.message.attachments[0].read()
		emoji = await guild.create_custom_emoji(name=name, image=image)
		await ctx.send(emoji)
		
def setup(client):
	client.add_cog(PPCog(client))