from discord.ext import commands
from discord.utils import get, find

from functions import Error, userHasPermission

import json
with open('./desc.json') as file:
    DESC = json.load(file)

def is_pipon_palace(ctx):
	return (ctx.guild.id == 836936601824788520)

class PPCog(commands.Cog):
	def __init__(self, client):
		self.client = client

	@commands.command(description=DESC["emoteify"])
	@commands.check(is_pipon_palace)
	@commands.cooldown(1, 10, commands.BucketType.channel)
	async def emoteify(self, ctx, name=None, addtomain:bool=False):
		if name == None or len(ctx.message.attachments) < 1:
			await Error(ctx, self.client, "Missing un-optional argument for command.")
			return

		if addtomain and ctx.author.id == self.client.owner_id:
			guild = ctx.guild
		else:
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
		if channel:
			message = await channel.fetch_message(payload.message_id)
		else:
			return
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
		if channel:
			message = await channel.fetch_message(payload.message_id)
		else:
			return
		pin = find(lambda m: m.emoji == "📌", message.reactions)

		if message.pinned and pin and pin.count < 10:
			await message.unpin()

	@commands.Cog.listener()
	async def on_member_join(self, member):
		if member.guild.id != 836936601824788520:
			return

		channel = get(member.guild.channels, id=836936602281705482) #general-chat
		await channel.send(f"**Welcome to the server** {member.mention}, enjoy your stay!!! <a:Pip0nSpeen:837000733441130567> ")

def setup(client):
  client.add_cog(PPCog(client))