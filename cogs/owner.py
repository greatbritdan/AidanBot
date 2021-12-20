import discord
from discord.ext import commands

import os, time, asyncio, contextlib, io, textwrap, sys
from traceback import format_exception

from functions import getComEmbed

import json
with open('./commanddata.json') as file:
	temp = json.load(file)
	DESC = temp["desc"]

class OwnerCog(commands.Cog):
	def __init__(self, client):
		self.client = client

	@commands.command(description=DESC["ping"])
	@commands.is_owner()
	async def ping(self, ctx):
		start_time = time.time()
		message = await ctx.reply("Testing Ping...", mention_author=False)
		end_time = time.time()
		await message.edit(content=f"Ping Pong motherfliper!\nBot: {round(self.client.latency * 1000)}ms\nAPI: {round((end_time - start_time) * 1000)}ms")

	@commands.command(name="eval", description=DESC["eval"])
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
				exec(f"async def func():\n{textwrap.indent(code, '    ')}", local_variables)
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

	@commands.command(description=DESC["reload"])
	@commands.is_owner()
	async def reload(self, ctx, extension):
		if len(extension) == 1:
			if extension == "g":
				extension = "general"
			if extension == "o":
				extension = "opinion"
			elif extension == "i":
				extension = "important"

		if extension and extension == "owner":
			MSG = await ctx.send(f'```if it crashes you wont be able to load or reload, are you sure?\n(make sure to check you are reloading, not unloading)```', view=discord.ui.View(
				discord.ui.Button(label="Yes", style=discord.ButtonStyle.red, custom_id="accept"), discord.ui.Button(label="No Actually", style=discord.ButtonStyle.green, custom_id="deny")
			))
			def check(interaction):
				return (interaction.user.id == self.client.owner_id and interaction.message.id == MSG.id and (interaction.data["custom_id"] == "accept" or interaction.data["custom_id"] == "deny"))
			try:
				interaction = await self.client.wait_for("interaction", timeout=10, check=check)
				await MSG.delete()
				if interaction.data["custom_id"] == "deny":
					return
			except asyncio.TimeoutError:
				await MSG.edit("```Timeout.```", view=discord.ui.View(
					discord.ui.Button(label="Yes", style=discord.ButtonStyle.red, custom_id="accept", disabled=True),
					discord.ui.Button(label="No Actually", style=discord.ButtonStyle.green, custom_id="deny", disabled=True)
				))
				return
		
		if f"cogs.{extension}" in self.client.extensions:
			self.client.unload_extension(f'cogs.{extension}')
			self.client.load_extension(f'cogs.{extension}')
			await ctx.send('```{} reloaded!```'.format(extension))
		else:
			self.client.load_extension(f'cogs.{extension}')
			await ctx.send('```{} loaded!```'.format(extension))

	@commands.command(description=DESC["restart"])
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
