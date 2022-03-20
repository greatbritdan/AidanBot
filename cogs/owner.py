import discord
from discord.ext import commands

import os, contextlib, io, textwrap, sys
from traceback import format_exception

from functions import getComEmbed, areyousure

class OwnerCog(commands.Cog):
	def __init__(self, client):
		self.client = client

	@commands.command()
	@commands.is_owner()
	async def echo(self, ctx, *, text:str="*yawn*"):
		await ctx.message.delete()
		await ctx.send(text, allowed_mentions=discord.AllowedMentions(everyone=False, roles=False))

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
				exec(f"import discord\n\nasync def func():\n{textwrap.indent(code, '    ')}", local_variables)
				obj = await local_variables["func"]()
				if obj and obj == "NoSend":
					return
				else:
					result = f"{stdout.getvalue()}"
		except Exception as e:
			result = "".join(format_exception(e, e, e.__traceback__))
		if result != "":
			emb = getComEmbed(ctx, self.client, "Eval", "Results:", f"```\n{result}\n```")
			await ctx.send(embed=emb)

	@commands.command()
	@commands.is_owner()
	async def reload(self, ctx, extension):
		if len(extension) == 1:
			if extension == "g":
				extension = "general"
			if extension == "o":
				extension = "opinion"
			elif extension == "i":
				extension = "important"
			elif extension == "m":
				extension = "moderation"

		if extension and extension == "owner":
			await areyousure(self.client, ctx, f'```if it crashes you wont be able to reload, are you sure?```')
		
		if f"cogs.{extension}" in self.client.extensions:
			self.client.unload_extension(f'cogs.{extension}')
			self.client.load_extension(f'cogs.{extension}')
			await ctx.send('```{} reloaded!```'.format(extension))
		else:
			self.client.load_extension(f'cogs.{extension}')
			await ctx.send('```{} loaded!```'.format(extension))

	@commands.command()
	@commands.is_owner()
	async def restart(self, ctx):
		await ctx.send("Restarting bot...")
		os.execv(sys.executable, ['python'] + sys.argv)

def clean_code(content):
	if content.startswith("```") and content.endswith("```"):
		return "\n".join(content.split("\n")[1:])[:-3]
	else:
		return content

def setup(client):
	client.add_cog(OwnerCog(client))