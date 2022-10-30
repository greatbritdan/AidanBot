from discord.ext.commands import Context
from discord.ext.commands import Cooldown

from aidanbot import AidanBot

def cooldown_core(ctx:Context):
	client:AidanBot = ctx.bot
	if ctx.author.id == client.aidan:
		return None # No cooldown (cuz owner)
	elif ctx.command.qualified_name == "issue":
		return Cooldown(2,15) # 2 times every 15 seconds (per user)
	return Cooldown(5,15) # 5 times every 15 seconds (per user)

def cooldown_opinion(ctx:Context):
	client:AidanBot = ctx.bot
	if ctx.author.id == client.aidan:
		return None # No cooldown (cuz owner)
	elif ctx.command.qualified_name == "opinion poll":
		return Cooldown(3,30) # 3 times every 30 seconds (per user)
	return Cooldown(5,10) # 5 times every 10 seconds (per user)

def cooldown_games(ctx:Context):
	client:AidanBot = ctx.bot
	if ctx.author.id == client.aidan:
		return None # No cooldown (cuz owner)
	return Cooldown(1,15) # 1 time every 15 seconds (per guild)

def cooldown_UwU(ctx:Context):
	client:AidanBot = ctx.bot
	if ctx.author.id == client.aidan:
		return None # No cooldown (cuz owner)
	return Cooldown(1,30) # 1 time every 30 seconds (per channel)

def cooldown_etc(ctx:Context):
	client:AidanBot = ctx.bot
	if ctx.author.id == client.aidan:
		return None # No cooldown (cuz owner)
	return Cooldown(3,10) # 3 times every 10 seconds (per user)