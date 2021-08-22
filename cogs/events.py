import discord
from discord.ext import commands

from functions import get_prefix, DELETEDATA, PARCEDATA, userHasPermission, Error, SEND_SYSTEM_MESSAGE

class EventsCog(commands.Cog):
	def __init__(self, client):
		self.client = client

	@commands.Cog.listener()
	async def on_ready(self):
		print(f'Logged in as big boy {self.client.user}')

		activity = discord.Activity(name=f'use {get_prefix()}help for help.', type=discord.ActivityType.playing)
		await self.client.change_presence(activity=activity)

	@commands.Cog.listener()
	async def on_message(self, message):
		if message.author.bot == True:
			return

		if not message.guild:
			await message.channel.send("Not available outside of guilds (servers)")
			return

		if "discord.gg" in message.content.lower():
			delete_invites = await PARCEDATA(message, self.client, "getstatic", "delete_invites")
			if delete_invites and userHasPermission(message.author, "kick_members") == False:
				invite_allow_channel = await PARCEDATA(message, self.client, "getstatic", "invite_allow_channel")
				if message.channel.name != invite_allow_channel:
					await message.delete()
					if invite_allow_channel != False:
						await message.channel.send(f"No invites allowed outside of {invite_allow_channel}! >:(")
					else:
						await message.channel.send(f"No invites allowed! >:(")

	@commands.Cog.listener()
	async def on_guild_join(self, guild):
		await SEND_SYSTEM_MESSAGE(None, self.client, "SOMEONE DID WHAT?!?!", f"Added to {guild.name}!")

	@commands.Cog.listener()
	async def on_guild_remove(self, guild):
		await DELETEDATA(guild.id, None, self.client)
		await SEND_SYSTEM_MESSAGE(None, self.client, "SOMEONE DID WHAT?!?!", f"Removed from {guild.name}!")

	@commands.Cog.listener()
	async def on_command_error(self, ctx, error):
		err = "I seem to have ran into an error, It's best to let Aidan know."
		if isinstance(error, commands.BotMissingPermissions):
			err = err + "\n\nError: Bot Missing Permissions!"
		elif isinstance(error, commands.MissingPermissions):
			err = err + "\n\nError: User Missing Permissions!"
		err = err + f"\n\nFull Error: {error}"

		if ctx.author.id == 384439774972215296 or err.endswith("not found"):
			await Error(ctx, self.client, err)
		else:
			await Error(ctx, self.client, err, True)

def setup(client):
  client.add_cog(EventsCog(client))