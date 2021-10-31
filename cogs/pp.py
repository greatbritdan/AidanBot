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

	@commands.Cog.listener()
	async def on_reaction_add(self, reaction, user):
		if self.BUSY and reaction.message.id == self.MSGID and reaction.emoji == "🔨":
			self.QUEUE += 1
			await reaction.message.remove_reaction(reaction, user)

	@commands.command(description="Bad bot.")
	@commands.check(is_pipon_palace)
	async def badbot(self, ctx, timer:int=60):
		HITS = 0
		STATES = {
			"bad": "https://cdn.discordapp.com/attachments/896833918685306891/899379971095674950/bad.png",
			"bot": "https://cdn.discordapp.com/attachments/896833918685306891/899379979249397831/bot.png"
		}

		self.BUSY = False
		self.QUEUE = 0

		emb = getEmbed(ctx, "badbot (loading)", "**Hits: 0** (queue: 0)", "", None, STATES["bad"])
		MSG = await ctx.send(embed=emb, mention_author=False)
		self.MSGID = MSG.id
		await MSG.add_reaction("🔨")

		def check(reaction, user):
			return (reaction.message.id == self.MSGID and reaction.emoji == "🔨" and not self.BUSY)

		async def edit(state):
			emb = getEmbed(ctx, "badbot", f"**Hits: {str(HITS)}** (queue: {str(self.QUEUE)})", "", None, STATES[state])
			await MSG.edit(embed=emb)

		while True:
			try:
				await edit("bad")
				await asyncio.sleep(0.4)
				if self.QUEUE == 0:
					self.BUSY = False

					reaction, user = await self.client.wait_for("reaction_add", timeout=timer, check=check)
					await MSG.remove_reaction(reaction, user)

					self.BUSY = True
				else:
					self.QUEUE -= 1

				HITS += 1
				await edit("bot")
				await asyncio.sleep(0.4)

			except asyncio.TimeoutError:
				await MSG.delete()
				await ctx.send(f"AidanBot has fled, you hit him **{str(HITS)}** times!")
				return

def setup(client):
  client.add_cog(PPCog(client))
