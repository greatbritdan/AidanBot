import discord
from discord.ext import commands
from discord.utils import find

import datetime
from requests import get
from random import randint, choice

from functions import ComError, getComEmbed, getComEmbedSimple

import json
with open('./commanddata.json') as file:
	temp = json.load(file)
	DESC = temp["desc"]

class GeneralCog(commands.Cog):
	def __init__(self, client):
		self.client = client
		self.embedargs = {
			"title":["str", ""],"desc":["str", ""],"colorr":["int", 20],"colorg":["int", 29],"colorb":["int", 37],"footer":["str", None],
			"footerimg":["str", None],"author":["str", None],"authorimg":["str", None],"showtime":["bool", False],"img":["str", None],
		}

	@commands.command(description=DESC["echo"])
	@commands.cooldown(1, 5)
	async def echo(self, ctx, *, text:str="\*yawn*"):
		await ctx.message.delete()
		await ctx.send(text, allowed_mentions=discord.AllowedMentions(everyone=False, roles=False))

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
		if not temp:
			emote = find(lambda m: name.lower() == m.name.lower(), ctx.guild.emojis)
			if not emote:
				emote = find(lambda m: name.lower() in m.name.lower(), ctx.guild.emojis)
			if emote:
				temp = {
					"name": emote.name,
					"pfp": emote.url
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

	@commands.command(hidden=True)
	async def bucket(self, ctx):
		urls = ["https://cdn.discordapp.com/attachments/880033942420484157/882333690410197062/cd804_y_bucket-blue.webp", "https://cdn.discordapp.com/attachments/880033942420484157/882333693094547566/cd805_y_bucket-yellow.webp", "https://cdn.discordapp.com/attachments/880033942420484157/882333695162343424/cd807_y_bucket-red.webp"]

		emb = getComEmbed(ctx, self.client, "Bucket", "Buket", "")
		emb.set_image(url=choice(urls))
		await ctx.send(embed=emb)

	@commands.command(description=DESC["meme"])
	@commands.cooldown(1, 3)
	async def meme(self, ctx):
		content = get("https://meme-api.herokuapp.com/gimme").text
		data = json.loads(content,)
		meme = getComEmbedSimple(data['title'], "")
		meme.set_image(url=data['url'])
		await ctx.send(embed=meme)

	@commands.command()
	@commands.cooldown(1, 3)
	async def reddit(self, ctx, name="cleanmemes"):
		content = get(f"https://meme-api.herokuapp.com/gimme/{name}").text
		data = json.loads(content,)
		meme = getComEmbedSimple(data['title'], "")
		meme.set_image(url=data['url'])
		await ctx.send(embed=meme)
		
def setup(client):
	client.add_cog(GeneralCog(client))