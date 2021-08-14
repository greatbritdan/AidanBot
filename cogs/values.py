import discord
from discord.ext import commands

from bot import add_command, get_defaults
from bot import PARCEDATA

class ValuesCog(commands.Cog):
	def __init__(self, client):
		self.client = client

	add_command(["values", "Values", "setup", "Sets up channel that hold server values and sets up default values.", "admin"])
	@commands.command()
	@commands.has_permissions(administrator=True)
	async def setup(self, ctx):
		overwrites = {
			ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
		}
		channel = await ctx.guild.create_text_channel('aidanbot-serverdata', topic="**DON'T TALK HERE**, For AidanBot's per server data!", overwrites=overwrites)

		defaults = get_defaults()
		data = []
		for key in defaults:
			data.append(key + "=" + defaults[key])

		sep = "\n"
		txt = sep.join(data)

		await channel.send(txt)

	add_command(["values", "Values", "config", "Get value or set value.", "admin"])
	@commands.command()
	@commands.has_permissions(administrator=True)
	async def config(self, ctx, action=None, name=None, val=None):
		if action == "get" and name:
			val = await PARCEDATA(ctx, "get", name)
			if val:
				await ctx.send(f"{name} is currently set to {val}!")
				return

		elif action == "set" and name and val:
			suc = await PARCEDATA(ctx, "set", name, val)
			if suc:
				await ctx.send(f"{name} was set to {val}!")
				return

		await ctx.send(f"{name} was not found!")

def setup(client):
  client.add_cog(ValuesCog(client))
