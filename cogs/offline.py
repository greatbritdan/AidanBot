import discord
from discord.commands import slash_command

# for unloading commands once Beta is going offline
class OfflineCog(discord.Cog):
	def __init__(self, client):
		self.client = client

	@slash_command(name="offline", description="If you see this, Beta is not online, this command exists so that the old commands are unregistered.")
	async def post(self, ctx):
		await ctx.respond("How?")

def setup(client):
	client.add_cog(OfflineCog(client))