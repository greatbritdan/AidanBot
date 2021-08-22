from discord.ext import commands

import contextlib
import io
import textwrap
from traceback import format_exception

from functions import getEmbed

class OwnerCog(commands.Cog):
	def __init__(self, client):
		self.client = client

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