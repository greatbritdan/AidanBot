import discord
from discord.ext import commands

import datetime
from random import randint

from functions import getEmbed, addField, Error, getIntFromText, getBar

import json
with open('./desc.json') as file:
    DESC = json.load(file)

class GeneralCog(commands.Cog):
	def __init__(self, client):
		self.client = client

	@commands.command(description=DESC["echo"])
	@commands.cooldown(1, 6, commands.BucketType.channel)
	async def echo(self, ctx, *, text:str="sample text"):
		if "love" in text:
			await ctx.send("***no***")
			return
			
		await ctx.message.delete()
		await ctx.send(text, allowed_mentions=discord.AllowedMentions(everyone=False, roles=False))

	@commands.command(description=DESC["react"])
	@commands.cooldown(1, 6, commands.BucketType.channel)
	async def react(self, ctx, message_id:int=None, reaction:str="👋"):
		if message_id == None:
			await Error(ctx, self.client, "Missing un-optional argument for command.")
			return

		MSG = await ctx.channel.fetch_message(message_id)
		await ctx.message.delete()
		await MSG.add_reaction(reaction)

	@commands.command(description=DESC["clone"])
	@commands.cooldown(1, 6, commands.BucketType.user)
	async def clone(self, ctx, member:discord.Member=None, *, message:str=None):
		if member == None or message == None:
			await Error(ctx, self.client, "Missing un-optional argument for command.")
			return
		
		webhook = await ctx.channel.create_webhook(name=member.name)
		await webhook.send(message, username=member.name + " (fake)", avatar_url=member.display_avatar.url)
		await webhook.delete()

	@commands.command(description=DESC["punish"])
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def punish(self, ctx):
		texts = [
			"AAAAAAAAAAAAAAAAAHHHHHHH!!!!!", "AAAHHH PLEASE STO-P!!!!", "I'M SORRY AHHHHHHH!!!",
			"PLEASE!... HAVE MERCY!...", "STOP...   *CRIES*", "AAAAAAHHHH!!!", "I'M SO SORRY.AAA!!!"
		]
		text = texts[randint(0, len(texts)-1)]
		await ctx.send("**" + text + "**")

	@commands.command(description=DESC["embed"])
	async def embed(self, ctx, *args):
		embedargs = {
			"title":["str", ""],
			"desc":["str", ""],
			"colorr":["int", 20],
			"colorg":["int", 29],
			"colorb":["int", 37],
			"footer":["str", None],
			"footerimg":["str", None],
			"author":["str", None],
			"authorimg":["str", None],
			"showtime":["bool", False],
			"img":["str", None],
		}
		args = argstodic(args, embedargs)
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
	async def embedhelp(self, ctx):
		embedargs = {
			"title":["str", ""],
			"desc":["str", ""],
			"colorr":["int", 20],
			"colorg":["int", 29],
			"colorb":["int", 37],
			"footer":["str", None],
			"footerimg":["str", None],
			"author":["str", None],
			"authorimg":["str", None],
			"showtime":["bool", False],
			"img":["str", None],
		}
		emb = getEmbed(ctx, "Embed Help", 'For each element you want to add, you type title=text or "title=more text" followed by a gap!', "")
		txt = ""
		for index in embedargs:
			default = str(embedargs[index][1])
			if default == "":
				default = "Empty String"
			txt = txt + "**" + index + ":** <" + embedargs[index][0] + "> (default " + default + ")\n"
		emb = addField(emb, "**All arguments:**", txt)
		await ctx.send(embed=emb)

	# NEW COMMAND TYPE!??!?!?!

	@commands.message_command(name="Copy Content")
	async def copycontent(self, ctx, message:discord.Message):
		await ctx.respond(f"Message content: ```\n{message.clean_content}\n```", ephemeral=True)

def argstodic(args, typdic):
	dic = {}
	# create the DIC
	for arg in args:
		split = arg.split('=', 1)
		if len(split) == 2:
			dic[split[0]] = split[1]

	# convert types
	for index in typdic:
		if index in dic:
			if typdic[index][0] == "int":
				try:
					dic[index] = int(dic[index])
				except:
					print("int conversion error!")
					dic[index] = 0
			if typdic[index][0] == "bool":
				if typdic[index] == "true":
					typdic[index] = True
				elif typdic[index] == "false":
					typdic[index] = False
				else:
					typdic[index] = None
		else:
			print(index)
			dic[index] = typdic[index][1]

	# return the DIC
	return dic

def setup(client):
	client.add_cog(GeneralCog(client))