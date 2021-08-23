from discord.ext import commands

import contextlib
import io
import textwrap
from traceback import format_exception

import asyncio

from functions import getEmbed, clear_command_type

class OwnerCog(commands.Cog):
	def __init__(self, client):
		self.client = client

	### COGS ###

	@commands.command()
	@commands.is_owner()
	async def load(self, ctx, extension):
		self.client.load_extension(f'cogs.{extension}')
		await ctx.send('```{} loaded!```'.format(extension))

	@commands.command()
	@commands.is_owner()
	async def unload(self, ctx, extension):
		if extension == "owner":
			await ctx.send('```owner can not be unloaded, it holds the $load, $unload and $reload function!```')
			return
			
		self.client.unload_extension(f'cogs.{extension}')
		clear_command_type(extension)
		await ctx.send('```{} unloaded!```'.format(extension))

	@commands.command()
	@commands.is_owner()
	async def forceunload(self, ctx, extension):
		MSG = await ctx.send('```are you sure you want to unload {}?```'.format(extension))
		await MSG.add_reaction("✅")
		await MSG.add_reaction("❎")

		def check(reaction, user):
			return (user == ctx.author and reaction.message.id == MSG.id and reaction.emoji == "✅" or reaction.emoji == "❎")

		try:
			reaction, user = await self.client.wait_for("reaction_add", timeout=10, check=check)
			if reaction.emoji == "✅":
				self.client.unload_extension(f'cogs.{extension}')
				clear_command_type(extension)
				await ctx.send('```{} unloaded!```'.format(extension))
			else:
				await ctx.send('```No action was taken.```')

		except asyncio.TimeoutError:
			await ctx.send('```Timeout```')

	@commands.command()
	@commands.is_owner()
	async def reload(self, ctx, extension):
		self.client.unload_extension(f'cogs.{extension}')
		clear_command_type(extension)
		self.client.load_extension(f'cogs.{extension}')
		await ctx.send('```{} reloaded!```'.format(extension))

	@commands.command()
	@commands.is_owner()
	async def ping(self, ctx):
		emb = getEmbed(ctx, "Ping", "Ping Pong motherfucker!", "{0}ms".format(round(self.client.latency, 3)))
		await ctx.send(embed=emb)

	@commands.command(name="eval")
	@commands.is_owner()
	async def _eval(self, ctx, *, code:str):
		code = clean_code(code)

		local_variables = {
			"client": self.client,
			"ctx": ctx,
			"author": ctx.author,
			"channel": ctx.channel,
			"guild": ctx.guild,
		}
		stdout = io.StringIO()

		try:
			with contextlib.redirect_stdout(stdout):
				exec(f"async def func():\n{textwrap.indent(code, '    ')}", local_variables,)
				obj = await local_variables["func"]()
				if obj:
					if obj == "NoSend":
						return

					result = f"{stdout.getvalue()}\n-- {obj}"
				else:
					result = f"{stdout.getvalue()}"
		except Exception as e:
			result = "".join(format_exception(e, e, e.__traceback__))

		emb = getEmbed(ctx, "Eval", "Results:", "```py\n" + result + "\n```")
		await ctx.send(embed=emb)

def clean_code(content):
	if content.startswith("```") and content.endswith("```"):
		return "\n".join(content.split("\n")[1:])[:-3]
	else:
		return content

def setup(client):
	client.add_cog(OwnerCog(client))