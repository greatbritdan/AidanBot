from discord.ext import commands
from discord.utils import get

from functions import Error, CooldownError, SEND_SYSTEM_MESSAGE

class EventsCog(commands.Cog):
	def __init__(self, client):
		self.client = client
						
	@commands.Cog.listener()
	async def on_guild_join(self, guild):
		await SEND_SYSTEM_MESSAGE(None, self.client, "SOMEONE DID WHAT?!?!", f"Added to {guild.name}!")

	@commands.Cog.listener()
	async def on_guild_remove(self, guild):
		await SEND_SYSTEM_MESSAGE(None, self.client, "SOMEONE DID WHAT?!?!", f"Removed from {guild.name}!")

	@commands.Cog.listener()
	async def on_command_error(self, ctx, error):
		# cooldown
		if isinstance(error, commands.CommandOnCooldown):
			await CooldownError(ctx, self.client, "Command on cooldown!! Try again in {:.2f} seconds".format(error.retry_after))
			return False

		# ones that should be ignored
		if isinstance(error, commands.CommandNotFound):
			await Error(ctx, self.client, "This command doesn't exist :/")
			return False
		elif isinstance(error, commands.CheckFailure):
			await Error(ctx, self.client, "You don't have permission to run this command :/")
			return False
		elif isinstance(error, commands.BotMissingPermissions):
			await Error(ctx, self.client, "I am missing permissions to do this :/")
			return False
		elif isinstance(error, commands.MissingPermissions):
			await Error(ctx, self.client, "You am missing permissions to do this :/")
			return False

		err = f"I seem to have ran into an error, It's best to let Aidan know.\n\nError: {error}"

		# ones that shouldn't be sent to system messages
		if ctx.author.id == self.client.owner_id:
			await Error(ctx, self.client, err)
		else:
			# REAL errors
			await Error(ctx, self.client, err, True)

def setup(client):
  client.add_cog(EventsCog(client))