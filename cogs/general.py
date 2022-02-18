import discord
from discord.ext import commands
from discord.utils import find

import randfacts
from random import randint

from functions import ComError

import json
with open('./data/commanddata.json') as file:
	temp = json.load(file)
	DESC = temp["desc"]

class GeneralCog(commands.Cog):
	def __init__(self, client):
		self.client = client

	@commands.command(description=DESC["react"])
	@commands.cooldown(1, 5)
	async def react(self, ctx, reaction:str="👋", message_id:int=None):
		MSG = ""
		if message_id:
			MSG = await ctx.channel.fetch_message(message_id)
		else:
			yes = False
			async for message in ctx.channel.history(limit=2):
				if yes:
					MSG = message
				else:
					yes = True

		await ctx.message.delete()
		await MSG.add_reaction(reaction)

	@commands.command(description=DESC["clone"])
	@commands.cooldown(1, 5)
	@commands.has_permissions(manage_webhooks=True)
	async def clone(self, ctx, name, *, message):
		if self.client.prefix in message:
			await ComError(ctx, self.client, "No running commands in clone.")
			return

		extra = {
			"Alesan99": "https://cdn.discordapp.com/attachments/885203191485050941/916394696350236712/Alesannew.png",
			"(fake)": "https://cdn.discordapp.com/attachments/896833918685306891/916400101533040700/fake.png",
			"Pip0n": "https://cdn.discordapp.com/attachments/885203191485050941/916738423467958312/Pip0n.png",
			"Box": "https://cdn.discordapp.com/attachments/885203191485050941/916738620730277888/Box.png"
		}

		temp = None
		for nam in extra:
			if name.lower() == nam.lower() or name.lower() in nam.lower():
				temp = {
					"name": nam,
					"pfp": extra[nam]
				}
				break
		if not temp:
			member = ctx.guild.get_member_named(name)
			if not member:
				member = find(lambda m: name.lower() in m.display_name.lower(), ctx.guild.members)
			if not member:
				member = find(lambda m: name.lower() in m.name.lower(), ctx.guild.members)
			if member:
				temp = {
					"name": member.display_name,
					"pfp": member.display_avatar.url
				}

		if temp:
			hook = ""
			for w in await ctx.channel.webhooks():
				if w.name == "AidanBotCloneHook":
					hook = w
			if not hook:
				hook = await ctx.channel.create_webhook(name="AidanBotCloneHook")

			await hook.send(message, username=temp["name"] + " (fake)", avatar_url=temp["pfp"])
		else:
			await ComError(ctx, self.client, f"Member '{name}' not found.")
			return

	@commands.command(description=DESC["punish"])
	@commands.cooldown(1, 5)
	async def punish(self, ctx):
		texts = ["AAAAAAAAAAAAHHHHHHH!!!!!","AAAHH PLEASE STO-P!!!!","I'M SORRY AAHHH!!!","PLEASE!... HAVE MERCY!...","STOP...   *CRIES*","AAAAAAHHHH!!!","I'M SO SORRY.AAA!!!"]
		text = texts[randint(0, len(texts)-1)]
		await ctx.send("**" + text + "**")

	@commands.command(description=DESC["fact"])
	@commands.cooldown(1, 5)
	async def fact(self, ctx):
		fact = randfacts.get_fact()
		await ctx.send(f"Did you know, {fact}")

def setup(client):
	client.add_cog(GeneralCog(client))