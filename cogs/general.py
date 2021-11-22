import discord
from discord.ext import commands
import datetime
from random import randint

from functions import ComError, argstodic, getComEmbed

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
	async def clone(self, ctx, member:discord.Member, *, message):
		if self.client.prefix in message:
			await ComError(ctx, self.client, "No running commands in clone.")
			return
		
		webhook = await ctx.channel.create_webhook(name=member.name)
		await webhook.send(message, username=member.name + " (fake)", avatar_url=member.display_avatar.url)
		await webhook.delete()

	@commands.command(description=DESC["embed"])
	@commands.cooldown(1, 10)
	async def embed(self, ctx, *args):
		args = argstodic(args, self.embedargs)
		emb = discord.Embed(
			title=args["title"].format(author=ctx.author, guild=ctx.guild, channel=ctx.channel),
			description=args["desc"].format(author=ctx.author, guild=ctx.guild, channel=ctx.channel),
			color=discord.Color.from_rgb(args["colorr"], args["colorg"], args["colorb"])
		)
		if args["img"]:
			emb.set_image(url=args["img"])
		if args["footer"]:
			if args["footerimg"]:
				emb.set_footer(text=args["footer"].format(author=ctx.author, guild=ctx.guild, channel=ctx.channel), icon_url=args["footerimg"])
			else:
				emb.set_footer(text=args["footer"].format(author=ctx.author, guild=ctx.guild, channel=ctx.channel))
		if args["author"]:
			if args["authorimg"]:
				emb.set_footer(name=args["author"].format(author=ctx.author, guild=ctx.guild, channel=ctx.channel), icon_url=args["authorimg"])
			else:
				emb.set_footer(name=args["author"].format(author=ctx.author, guild=ctx.guild, channel=ctx.channel))
		if args["showtime"]:
			emb.timestamp = datetime.datetime.utcnow()

		await ctx.send(embed=emb)

	@commands.command(description=DESC["embedhelp"])
	@commands.cooldown(1, 10)
	async def embedhelp(self, ctx):
		txt = ""
		for index in self.embedargs:
			default = str(self.embedargs[index][1])
			if default == "":
				default = "Empty String"
			txt = txt + "**" + index + ":** <" + self.embedargs[index][0] + "> (default " + default + ")\n"
		emb = getComEmbed(ctx, self.client, "Embed Help", 'For each element you want to add, you type title=text or "title=more text" followed by a gap!', fields=[["**All arguments:**", txt]])
		await ctx.send(embed=emb)

	@commands.command(description=DESC["punish"])
	@commands.cooldown(1, 5)
	async def punish(self, ctx):
		texts = ["AAAAAAAAAAAAHHHHHHH!!!!!","AAAHH PLEASE STO-P!!!!","I'M SORRY AAHHH!!!","PLEASE!... HAVE MERCY!...","STOP...   *CRIES*","AAAAAAHHHH!!!","I'M SO SORRY.AAA!!!"]
		text = texts[randint(0, len(texts)-1)]
		await ctx.send("**" + text + "**")

def setup(client):
	client.add_cog(GeneralCog(client))