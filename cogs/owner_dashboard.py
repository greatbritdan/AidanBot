import discord.ext.commands as CM
import discord.app_commands as AC
from discord import Interaction as Itr

import os, sys

from aidanbot import AidanBot
from utils.functions import getComEmbed
from utils.checks import ab_check

from typing import Literal

# Originaly part of owner.py, split because of reload
class DashCog(CM.Cog):
	def __init__(self, client:AidanBot):
		self.client = client

	@AC.command(name="owner-dashboard", description="The dashboard for the owner.")
	@AC.describe(function="The function to run.", argument="Argument for function.")
	async def dashboard(self, itr:Itr, function:Literal["test","reloadcon","reloaducon","restart"]=None, argument:str=None):
		if not await ab_check(itr, self.client, is_owner=True):
			return
		c = self.client
		if not function:
			emb = getComEmbed(c, content="Hello Boss, all systems running as intended!", command="Owner Dashboard", fields=[["Average Latency:", f"{c.latency:.2f} Seconds."],["Memory:", f"Total Commands: N/A\nTotal Cogs: {len(c.cogs)}\n---\nTotal Guilds: {len(c.guilds)}\nCached Emojis: {len(c.emojis)}\nCached Stickers: {len(c.stickers)}\nCached Members: {len(c.users)}"]])
			await itr.response.send_message(embed=emb)
			return

		output = "```no output```"
		outputfields = False
		if function == "test":
			output = f"Test command: {argument}"
		elif function == "reloadcon":
			await c.CON.values_msgupdate("load")
			output = "Reloaded guild config"
		elif function == "reloaducon":
			await c.UCON.values_msgupdate("load")
			output = "Reloaded user config"

		emb = getComEmbed(c, content=output, command=f"Owner Dashboard > {function}", fields=outputfields)
		await itr.response.send_message(embed=emb)
		return

async def setup(client:AidanBot):
	await client.add_cog(DashCog(client), guilds=client.debug_guilds)