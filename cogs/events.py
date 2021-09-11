from discord.ext import commands

from functions import Error, SEND_SYSTEM_MESSAGE

class EventsCog(commands.Cog):
	def __init__(self, client):
		self.client = client
		
	## Archive Coolguy's Community hub messages, due to recent ghost pings ##
	@commands.Cog.listener()
	async def on_message(self, message):
		if message.guild.id == 754952103381696656:
			guild = get(self.client.guilds, id=879063875469860874)
			channel = get(guild.text_channels, id=886191398259392512)

			await channel.send(f"From `{message.author.name}` in `#{message.channel.name}`:  {message.content}")

	@commands.Cog.listener()
	async def on_guild_join(self, guild):
		await SEND_SYSTEM_MESSAGE(None, self.client, "SOMEONE DID WHAT?!?!", f"Added to {guild.name}!")

	@commands.Cog.listener()
	async def on_guild_remove(self, guild):
		await SEND_SYSTEM_MESSAGE(None, self.client, "SOMEONE DID WHAT?!?!", f"Removed from {guild.name}!")

	@commands.Cog.listener()
	async def on_command_error(self, ctx, error):
		# ones that should be ignored
		if isinstance(error, commands.CommandNotFound) or isinstance(error, commands.CheckFailure):
			await Error(ctx, self.client, "This command doesn't exist :/")
			return False

		err = f"I seem to have ran into an error, It's best to let Aidan know.\n\nError: {error}"

		# ones that shouldn't be sent to system messages
		if ctx.author.id == 384439774972215296 or isinstance(error, commands.BotMissingPermissions) or isinstance(error, commands.MissingPermissions):
			await Error(ctx, self.client, err)
		else:
			# REAL errors
			await Error(ctx, self.client, err, True)

def setup(client):
  client.add_cog(EventsCog(client))
