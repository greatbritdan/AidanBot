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

	@commands.Cog.listener()
	async def on_member_join(self, member):
		if member.guild.id != 836936601824788520 or self.client.isbeta:
			return

		msgs = ["Make sure to take off your shoes.", "Enjoy your stay!", "Cursed Goomba hopes you enjoy your stay", "||Help i'm being forced to say this||"]
		channel = get(member.guild.channels, id=836936602281705482) #general-chat
		await channel.send(f"**Welcome to the server** {member.mention}, {choice(msgs)} <a:Pip0nSpeen:837000733441130567>")

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

	@commands.command(description="just for one thing so yeah...")
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