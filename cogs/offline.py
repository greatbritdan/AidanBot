from discord.ext import commands

# for unloading commands once Beta is going offline

class OfflineCog(commands.Cog):
	def __init__(self, client):
		self.client = client

	@commands.slash_command(name="offline", description="If you see this, Beta is not online, this command exists so that the old commands are unregistered.")
	async def post(self, ctx):
		await ctx.respond("How?")

def setup(client):
	client.add_cog(OfflineCog(client))