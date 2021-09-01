import time
import contextlib
import io
import textwrap
from traceback import format_exception

from discord.ext import commands

from functions import getEmbed

class OwnerCog(commands.Cog):
	def __init__(self, client):
		self.client = client

	@commands.command(description="Gets bot/api latency.")
	@commands.is_owner()
	async def ping(self, ctx):
		start_time = time.time()
		message = await ctx.reply("Testing Ping...", mention_author=False)
		end_time = time.time()

		await message.edit(content=f"Ping Pong motherfucker! {round(self.client.latency * 1000)}ms\nAPI: {round((end_time - start_time) * 1000)}ms")

	@commands.command(name="eval", description="Run code.")
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
				if obj and obj == "NoSend":
					return
				else:
					result = f"{stdout.getvalue()}"
		except Exception as e:
			result = "".join(format_exception(e, e, e.__traceback__))

		emb = getEmbed(ctx, "Eval", "Results:", "```\n" + result + "\n```")
		await ctx.send(embed=emb)
		
	### COGS ###

	@commands.command(hidden=True)
	@commands.is_owner()
	async def load(self, ctx, extension):
		self.client.load_extension(f'cogs.{extension}')
		await ctx.send('```{} loaded!```'.format(extension))

	@commands.command(hidden=True)
	@commands.is_owner()
	async def unload(self, ctx, extension):
		if extension == "owner":
			await ctx.send('```owner can not be unloaded, it holds the $load, $unload and $reload function!```')
			return
			
		self.client.unload_extension(f'cogs.{extension}')
		await ctx.send('```{} unloaded!```'.format(extension))

	@commands.command(hidden=True)
	@commands.is_owner()
	async def reload(self, ctx, extension):
		self.client.unload_extension(f'cogs.{extension}')
		self.client.load_extension(f'cogs.{extension}')
		await ctx.send('```{} reloaded!```'.format(extension))

def clean_code(content):
	if content.startswith("```") and content.endswith("```"):
		return "\n".join(content.split("\n")[1:])[:-3]
	else:
		return content

def setup(client):
	client.add_cog(OwnerCog(client))