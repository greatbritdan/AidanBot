from functions import argsToTime
import discord
from discord.ext import commands

import datetime

import json
with open('./commanddata.json') as file:
	temp = json.load(file)
	DESC = temp["desc"]

class ModerationCog(commands.Cog):
	def __init__(self, client):
		self.client = client

	@commands.command(description=DESC["slowmode"])
	@commands.cooldown(1, 5)
	@commands.has_permissions(manage_channels=True)
	async def slowmode(self, ctx, seconds:int=0):
		await ctx.channel.edit(slowmode_delay=seconds)
		await ctx.send(f"Set the slowmode delay in this channel to {seconds} seconds!")

	@commands.command(description=DESC["kick"])
	@commands.cooldown(1, 5)
	@commands.has_permissions(kick_members=True)
	async def kick(self, ctx, user:discord.Member, *, reason=None):
		await ctx.guild.kick(user, reason=reason)
		await ctx.send(f"Kicked {user.mention}.")
	
	@commands.command(description=DESC["ban"])
	@commands.cooldown(1, 5)
	@commands.has_permissions(ban_members=True)
	async def ban(self, ctx, user:discord.Member, days:int=0, *, reason=None):
		await ctx.guild.ban(user, reason=reason, delete_message_days=days)
		await ctx.send(f"Banned {user.mention}.")

	@commands.command(description=DESC["clear"])
	@commands.cooldown(1, 5)
	@commands.has_permissions(manage_messages=True)
	async def clear(self, ctx, limit:int=1):
		await ctx.channel.purge(limit=limit+1)

	'''@commands.command(description=DESC["timeout"])
	@commands.cooldown(1, 5)
	@commands.has_permissions(moderate_members=True)
	async def timeout(self, ctx, user:discord.Member, *times):
		time = datetime.datetime.now()
		t, txt = argsToTime(times)
		time += datetime.timedelta( seconds=t["s"], minutes=t["m"], hours=t["h"], days=t["d"] )
		await user.timeout(time)
		await ctx.send(f"Timed out {user.mention} for {txt}.")'''

def setup(client):
	client.add_cog(ModerationCog(client))