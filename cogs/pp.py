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
	async def on_raw_reaction_add(self, payload):
		if payload.guild_id != 836936601824788520:
			return
			
		guild = get(self.client.guilds, id=payload.guild_id)
		channel = get(guild.channels, id=payload.channel_id)
		message = await channel.fetch_message(payload.message_id)
		pin = find(lambda m: m.emoji == "📌", message.reactions)

		if pin and pin.count == 10:
			for reac in message.reactions:
				if reac.emoji == "✖️":
					async for user in reac.users():
						if userHasPermission(user, "manage_messages"):
							return

			await message.pin()

	@commands.Cog.listener()
	async def on_raw_reaction_remove(self, payload):
		if payload.guild_id != 836936601824788520:
			return

		guild = get(self.client.guilds, id=payload.guild_id)
		channel = get(guild.channels, id=payload.channel_id)
		message = await channel.fetch_message(payload.message_id)
		pin = find(lambda m: m.emoji == "📌", message.reactions)

		if message.pinned and pin and pin.count < 10:
			await message.unpin()
		
def setup(client):
  client.add_cog(PPCog(client))
