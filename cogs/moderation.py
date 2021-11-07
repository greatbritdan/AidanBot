import discord
from discord.ext import commands

from functions import Error

import json
with open('./desc.json') as file:
    DESC = json.load(file)

class ModerationCog(commands.Cog):
	def __init__(self, client):
		self.client = client

	@commands.command(description=DESC["slowmode"])
	@commands.has_permissions(manage_channels=True)
	async def slowmode(self, ctx, seconds:int=0):
		await ctx.channel.edit(slowmode_delay=seconds)
		await ctx.send(f"Set the slowmode delay in this channel to {seconds} seconds!")

	@commands.command(description=DESC["kick"])
	@commands.has_permissions(kick_members=True)
	async def kick(self, ctx, user:discord.Member=None, *, reason:str=None):
		if user == None:
			await Error(ctx, self.client, "Please spesify a member.")
			return

		await ctx.guild.kick(user, reason=reason)
		await ctx.send(f"Kicked {user.mention}.")
	
	@commands.command(description=DESC["ban"])
	@commands.has_permissions(ban_members=True)
	async def ban(self, ctx, user:discord.Member=None, days:int=0, *, reason:str=None):
		if user == None:
			await Error(ctx, self.client, "Please spesify a member.")
			return

		await ctx.guild.ban(user, reason=reason, delete_message_days=days)
		await ctx.send(f"Banned {user.mention}.")

	@commands.command(description=DESC["clear"])
	@commands.has_permissions(manage_messages=True)
	async def clear(self, ctx, limit:int=1):
		await ctx.channel.purge(limit=limit+1)

def setup(client):
  client.add_cog(ModerationCog(client))