import discord
import discord.ext.commands as CM
import discord.app_commands as AC
from discord import Interaction as Itr

from aidanbot import AidanBot
from functions import getComEmbed
from checks import ab_check

from typing import Literal

# Originaly part of owner.py, split because of reload
class DashCog(CM.Cog):
	def __init__(self, client:AidanBot):
		self.client = client

	@AC.command(name="owner-dashboard", description="The dashboard for the owner.")
	@AC.describe(function="The function to run.", argument="Argument for function.")
	async def dashboard(self, itr:Itr, function:Literal["test"]=None, argument:str=None):
		if not await ab_check(itr, self.client, is_owner=True):
			return
		c = self.client
		if not function:
			emb = getComEmbed(str(itr.user), c, "- Owner Dashboard -", "Hello Boss, all systems running as intended!", fields=[["Average Latency:", f"{c.latency:.2f} Seconds."],["Memory:", f"Total Commands: N/A\nTotal Cogs: {len(c.cogs)}\n---\nTotal Guilds: {len(c.guilds)}\nCached Emojis: {len(c.emojis)}\nCached Stickers: {len(c.stickers)}\nCached Members: {len(c.users)}"]])
			await itr.response.send_message(embed=emb)
			return

		output = "```no output```"
		outputfields = False
		if function == "test":
			output = f"Test command: {argument}"

		emb = getComEmbed(str(itr.user), c, f"- Owner Dashboard > {function} -", output, fields=outputfields)
		await itr.response.send_message(embed=emb)
		return

async def setup(client:AidanBot):
	await client.add_cog(DashCog(client), guilds=client.debug_guilds)