from functions import argsToTime
import discord
from discord.ext import commands

import datetime

import json
with open('./data/commanddata.json') as file:
	temp = json.load(file)
	DESC = temp["desc"]

class ModerationCog(commands.Cog):
	def __init__(self, client):
		self.client = client

	@commands.command(description=DESC["slowmode"])
	@commands.cooldown(1, 3)
	async def slowmode(self, ctx, seconds:int=0):
		if ctx.channel.permissions_for(ctx.author).moderate_members:
			await ctx.channel.edit(slowmode_delay=seconds)
			if seconds == 0:
				await ctx.send(f"Removed the slowmode in {ctx.channel.mention}!")
			else:
				await ctx.send(f"Set the slowmode to {seconds} seconds in {ctx.channel.mention}!")
		else:
			await ctx.send(f"Set the slowmode to 'nice try' seconds in {ctx.channel.mention}!")

	@commands.command(description=DESC["kick"])
	@commands.cooldown(1, 5)
	async def kick(self, ctx, user:discord.Member=None, *, reason=None):
		if ctx.channel.permissions_for(ctx.author).kick_members:
			if user:
				await ctx.guild.kick(user, reason=reason)
				await ctx.send(f"Kicked **{user.mention}**.")
			else:
				await ctx.send("Give me a name and I end their game.")
		else:
			await ctx.send(f"Maybe one day :).")
	
	@commands.command(description=DESC["ban"])
	@commands.cooldown(1, 5)
	async def ban(self, ctx, user:discord.Member, days:int=0, *, reason=None):
		if ctx.channel.permissions_for(ctx.author).ban_members:
			if user:
				await ctx.guild.ban(user, reason=reason, delete_message_days=days)
				await ctx.send(f"Banned **{user.mention}**.")
			else:
				await ctx.send("Give me a name and I end their game.")
		else:
			await ctx.send(f"Maybe one day :).")

	@commands.command(description=DESC["clear"])
	@commands.cooldown(1, 5)
	async def clear(self, ctx, limit:int=1):
		if ctx.channel.permissions_for(ctx.author).manage_messages:
			await ctx.channel.purge(limit=limit+1)
		else:
			await ctx.send(f"Big mood right here.")

	@commands.command(description=DESC["timeout"])
	@commands.cooldown(1, 5)
	async def timeout(self, ctx, user:discord.Member, *times):
		time = datetime.datetime.now()
		t, txt = argsToTime(times)

		if ctx.channel.permissions_for(ctx.author).moderate_members:
			time += datetime.timedelta( seconds=t["s"], minutes=t["m"], hours=t["h"], days=t["d"] )
			await user.timeout(time)
			if txt == "":
				await ctx.send(f"Removed timeout for {user.mention}.")
			else:
				await ctx.send(f"Timed out {user.mention} for {txt}.")
		else:
			time += datetime.timedelta( seconds=15 )
			await ctx.author.timeout(time)
			await ctx.send(f"Timed out {ctx.author.mention} for 100 years. <:problame:869571321967816704>")

def setup(client):
	client.add_cog(ModerationCog(client))