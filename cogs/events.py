from discord.ext import commands
from discord.utils import get

from functions import Error, SEND_SYSTEM_MESSAGE

class EventsCog(commands.Cog):
	def __init__(self, client):
		self.client = client

	@commands.Cog.listener()
	async def on_message(self, message):
		if message.content.lower() == "hi five":
			await message.add_reaction("🖐️")

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