import os
import discord
from discord.ext import commands

import time
import asyncio
import contextlib
import io
import textwrap
import sys
from traceback import format_exception

from discord.utils import resolve_template

from functions import getEmbed

import json
with open('./desc.json') as file:
    DESC = json.load(file)

class OwnerCog(commands.Cog):
	def __init__(self, client):
		self.client = client

	@commands.command(description=DESC["ping"])
	@commands.is_owner()
	async def ping(self, ctx):
		start_time = time.time()
		message = await ctx.reply("Testing Ping...", mention_author=False)
		end_time = time.time()

		await message.edit(content=f"Ping Pong mother||fuck||er!\nBot: {round(self.client.latency * 1000)}ms\nAPI: {round((end_time - start_time) * 1000)}ms")

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
			emb = getEmbed(ctx, "Eval", "Results:", "```\n" + result + "\n```")
			await ctx.send(embed=emb)
		
	### COGS ###

	@commands.command(description=DESC["load"])
	@commands.is_owner()
	async def load(self, ctx, extension):
		await cog_edit(self.client, ctx, "load", extension)

	@commands.command(description=DESC["unload"])
	@commands.is_owner()
	async def unload(self, ctx, extension):
		await cog_edit(self.client, ctx, "unload", extension)
		
	@commands.command(description=DESC["reload"], aliases=["r"])
	@commands.is_owner()
	async def reload(self, ctx, extension):
		await cog_edit(self.client, ctx, "reload", extension)

	@commands.command(description=DESC["restart"])
	@commands.is_owner()
	async def restart(self, ctx):
		await ctx.send("Restarting bot...")
		restart = {
			"channel_id": ctx.channel.id,
			"guild_id": ctx.guild.id,
			"time": time.time()
		}
		with open("restart.json", "w") as fp:
			json.dump(restart, fp)

		os.execv(sys.executable, ['python'] + sys.argv)

	@commands.command(description=DESC["sleep"])
	@commands.is_owner()
	async def sleep(self, ctx):
		if self.client.ASLEAP:
			await ctx.send("zzzzz, HUH WHA, bruh i am already alseep! zzzzz")
		else:
			self.client.ASLEAP = True
			await ctx.send(f"CYA SCRUBS!!!")
			await self.client.change_presence(status=discord.Status.idle)

	@commands.command(description=DESC["wake"])
	@commands.is_owner()
	async def wake(self, ctx):
		if not self.client.ASLEAP:
			await ctx.send("I'm already awake, you dumbass...")
		else:
			self.client.ASLEAP = False
			await ctx.send("Aww, ok fine, ready to take command!")
			await self.client.change_presence(status=discord.Status.online)

async def cog_edit(client, ctx, type, extension=None):
	if len(extension) == 1:
		if extension == "g":
			extension = "general"
		elif extension == "i":
			extension = "important"
		elif extension == "m":
			extension = "moderation"
		elif extension == "e":
			extension = "events"
		elif extension == "o":
			extension = "owner"

	if extension and extension == "owner" and type != "load":
		MSG = await ctx.send(f'```if it crashes you wont be able to load or reload, are you sure?\n(make sure to check you are reloading, not unloading)```', view=discord.ui.View(
			discord.ui.Button(label="Yes", style=discord.ButtonStyle.red, custom_id="accept"),
			discord.ui.Button(label="No Actually", style=discord.ButtonStyle.green, custom_id="deny")
		))

		def check(interaction):
			return (interaction.user.id == client.owner_id and interaction.message.id == MSG.id and (interaction.data["custom_id"] == "accept" or interaction.data["custom_id"] == "deny"))

		try:
			interaction = await client.wait_for("interaction", timeout=10, check=check)
			await MSG.delete()

			if interaction.data["custom_id"] == "deny":
				return

		except asyncio.TimeoutError:
			await MSG.edit("```Timeout.```", view=discord.ui.View(
				discord.ui.Button(label="Yes", style=discord.ButtonStyle.red, custom_id="accept", disabled=True),
				discord.ui.Button(label="No Actually", style=discord.ButtonStyle.green, custom_id="deny", disabled=True)
			))
			return
	
	if type == "load":
		if f"cogs.{extension}" in client.extensions:
			await ctx.send('```{} is already loaded.```'.format(extension))
			return

		client.load_extension(f'cogs.{extension}')
		await ctx.send('```{} loaded!```'.format(extension))

	elif type == "unload":
		client.unload_extension(f'cogs.{extension.lower()}')
		await ctx.send('```{} unloaded!```'.format(extension.lower()))

	elif type == "reload":
		client.unload_extension(f'cogs.{extension}')
		client.load_extension(f'cogs.{extension}')
		await ctx.send('```{} reloaded!```'.format(extension))

def clean_code(content):
	if content.startswith("```") and content.endswith("```"):
		return "\n".join(content.split("\n")[1:])[:-3]
	else:
		return content

def setup(client):
	client.add_cog(OwnerCog(client))