import discord
import discord.ext.commands as CM
import discord.app_commands as AC
from discord import Interaction as Itr

import json, re, asyncio
from random import choice
from typing import Literal

from aidanbot import AidanBot
from utils.functions import getComEmbed

class SuggestCog(CM.Cog):
	def __init__(self, client:AidanBot):
		self.client = client

	suggestgroup = AC.Group(name="suggestbot", description="Commands to do with suggestion bot.")

	@suggestgroup.command(name="info", description="Information about suggestbot.")
	async def info(self, itr:Itr):
		if itr.guild.id != self.client.revival_guild:
			await itr.response.send_message(ephemeral=True,content="I have only come back online for the celebration of Pip0n's Palace before it's shutdown, I am very much still deprecated and have not returned. Thank you for keeping me around!")
			return
			
		await itr.response.send_message(embed=getComEmbed(self.client, "What is suggestbot?", "Suggestbot is a remake of the [Mari0 Suggestion Bot](https://twitter.com/Mari0AE_Bot) from twitter made by <@581560073030205460> but for discord, it creates fake and silly suggestions for the game.", command="Suggestion Bot > Info"))
	
	@suggestgroup.command(name="generate", description="Generate some Mari0 AE suggestions.")
	@AC.describe(logs="If older suggestions are saved to a thread.",)
	async def generate(self, itr:Itr, logs:Literal["Enabled", "Disabled"]="Enabled"):
		if itr.guild.id != self.client.revival_guild:
			await itr.response.send_message(ephemeral=True,content="I have only come back online for the celebration of Pip0n's Palace before it's shutdown, I am very much still deprecated and have not returned. Thank you for keeping me around!")
			return
		
		THREAD:discord.Thread|None = None
		page = 0
		pages = [self.returnSuggestion(itr)]

		def getView(timeout=False):
			first = (page == 0)
			view = discord.ui.View(timeout=None)
			view.add_item(discord.ui.Button(label="<-", style=discord.ButtonStyle.blurple, custom_id="left", disabled=(first or timeout)))
			view.add_item(discord.ui.Button(label=f"{page+1}/{len(pages)}", style=discord.ButtonStyle.gray, custom_id="display", disabled=True))
			view.add_item(discord.ui.Button(label="->", style=discord.ButtonStyle.blurple, custom_id="right", disabled=timeout))
			view.add_item(discord.ui.Button(label="x", style=discord.ButtonStyle.red, custom_id="close", disabled=timeout))
			return view
		
		await itr.response.send_message(embeds=pages[page], view=getView())
		MSG = await itr.original_response()

		def check(checkitr:Itr):
			try:
				return (checkitr.message.id == MSG.id)
			except:
				return False
		while True:
			try:
				butitr:Itr = await self.client.wait_for("interaction", timeout=90, check=check)
				if butitr.user == itr.user or butitr.user == self.client.owner.id:
					await butitr.response.defer()
					if butitr.data["custom_id"] == "left":
						page -= 1
						if page < 0:
							page = len(pages)-1
							
					elif butitr.data["custom_id"] == "right":
						page += 1
						if page > len(pages)-1 and len(pages) < 99:
							pages.append(self.returnSuggestion(itr))
							if logs == "Enabled":
								if not THREAD:
									THREAD = await MSG.create_thread(name=f"Older Suggestions ({MSG.id})", auto_archive_duration=60)
								await THREAD.send(content=f"Page {page}:", embeds=pages[page-1])

					elif butitr.data["custom_id"] == "close":
						if logs == "Enabled" and THREAD:
							await THREAD.send(content=f"Page {len(pages)}:", embeds=pages[len(pages)-1])
							await THREAD.edit(archived=True, locked=True)
						return await itr.edit_original_response(view=getView(True))

					await itr.edit_original_response(embeds=pages[page], view=getView())
				else:
					await butitr.response.send_message(self.client.itrFail(), ephemeral=True)
			except asyncio.TimeoutError:
				if logs == "Enabled" and THREAD:
					await THREAD.send(content=f"Page {len(pages)}:", embeds=pages[len(pages)-1])
					await THREAD.edit(archived=True, locked=True)
				return await itr.edit_original_response(view=getView(True))

	def returnSuggestion(self, itr:Itr):
		suggestion, images = self.createSuggestion(itr)
		emb = getComEmbed(self.client, "New suggestion fresh from the oven:", suggestion, command="Suggestion Bot > Generate")
		if len(images) > 0: emb.set_thumbnail(url=images[0])
		return [emb]

	def loadSuggestions(self):
		with open(f'./data/suggestions.json') as file:
			suggestions = json.load(file)

		origin, images, groups = False, False, {}
		for name in suggestions:
			if name == "_origin":
				origin = suggestions[name]
			if name == "_images":
				images = suggestions[name]
			else:
				groups[name] = suggestions[name]

		return origin, images, groups

	def createSuggestion(self, itr:Itr):
		origin, images, groups = self.loadSuggestions()

		result = choice(origin)
		result_images = []
		while "{" in result:
			splited = re.split("{(.*?)}", result)
			result = ""
			text = True
			for s in splited:
				if text:
					result += s
				else:
					decision = choice(groups[s])
					if decision.startswith("$"):
						decision, decisionimg = self.formatDollar(itr, decision[1:])
						if decisionimg:
							result_images.append(decisionimg)
					elif decision in images and images[decision] != "??":
						result_images.append(images[decision])
					result += decision
				text = not text

		result_images = list(dict.fromkeys(result_images))
		result = result.strip()
		result = result[0].upper() + result[1:]
		return result, result_images

	def formatDollar(self, itr:Itr, type):
		if type == "member":
			member = choice(itr.guild.members)
			return member.display_name, member.display_avatar.url
		elif type == "self":
			member = itr.user
			return member.display_name, member.display_avatar.url
		return "N/A", "N/A"

async def setup(client:AidanBot):
	await client.add_cog(SuggestCog(client), guilds=client.debug_guilds)