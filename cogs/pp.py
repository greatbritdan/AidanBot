import discord
from discord.ext import commands
from discord.utils import get

import asyncio

from functions import Error, getEmbed

import json
with open('./desc.json') as file:
    DESC = json.load(file)

def is_pipon_palace(ctx):
	return (ctx.guild.id == 836936601824788520)

class PPCog(commands.Cog):
	def __init__(self, client):
		self.client = client

	@commands.Cog.listener()
	async def on_member_join(self, member):
		if member.guild.id != 836936601824788520:
			return

		channel = get(member.guild.channels, id=836936602281705482) #general-chat
		await channel.send(f"**Welcome to the server** {member.mention}, enjoy your stay!!! <a:Pip0nSpeen:837000733441130567> ")

	@commands.command(description=DESC["emoteify"])
	@commands.check(is_pipon_palace)
	@commands.cooldown(1, 10, commands.BucketType.channel)
	async def emoteify(self, ctx, name=None, addtomain:bool=False):
		if name == None or len(ctx.message.attachments) < 1:
			await Error(ctx, self.client, "Missing un-optional argument for command.")
			return

		if addtomain and ctx.author.id == self.client.owner_id:
			guild = ctx.guild
		else:
			guild = get(self.client.guilds, id=879063875469860874)

		image = await ctx.message.attachments[0].read()
		emoji = await guild.create_custom_emoji(name=name, image=image)

		await ctx.send(emoji)

	@commands.command(description=DESC["addcommand"])
	@commands.check(is_pipon_palace)
	@commands.cooldown(1, 6, commands.BucketType.guild)
	async def addcommand(self, ctx, name=None, *, text=None):
		if name == None or text == None:
			await Error(ctx, self.client, "Missing un-optional argument for command.")
			return
		err = ""
		if len(name) > 24:
			err = "Name is longer than 24 characters."
		elif len(text) > 128:
			err = "Text is longer than 128 characters."
		elif "\n" in name:
			err = "Name can't contain new line."
		elif " " in name:
			err = "Name can't contain spaces. use an _ instead!"
		elif self.client.get_command(name):
			err = "This is already a built in command."
		elif name in self.client.custom_commands:
			err = "This custom command already exists."
		
		if err != "":
			await Error(ctx, self.client, err)
			return
		await self.client.add_custom_command(name, text)
		await ctx.send(f"{self.client.PREFIX}{name} added.")
		
	@commands.command(description=DESC["removecommand"])
	@commands.check(is_pipon_palace)
	@commands.cooldown(1, 6, commands.BucketType.guild)
	async def removecommand(self, ctx, name=None):
		if name == None:
			await Error(ctx, self.client, "Missing un-optional argument for command.")
			return
		if name in self.client.custom_commands:
			await self.client.remove_custom_command(name)
			await ctx.send(f"{self.client.PREFIX}{name} removed.")
		else:
			await ctx.send("This custom command doesn't exist.")

	@commands.command(description=DESC["allcommands"])
	@commands.check(is_pipon_palace)
	@commands.cooldown(1, 3, commands.BucketType.guild)
	async def allcommands(self, ctx):
		pages = [""]
		page, maxpages = 0, 0
		for name in self.client.custom_commands:
			pages[maxpages] += f"**{name}**: {self.client.custom_commands[name]}\n"
			if pages[maxpages].count('\n') > 12:
				maxpages += 1
				pages.append("")

		def getAllEmbed(typ=None):
			title, timeout = "Custom Commands", False
			if typ == "load":
				title = "Custom Commands (loading...)"
			elif typ == "timeout":
				title, timeout = "Custom Commands (timeout)", True
			else:
				title = f"Help (page {page+1} of {maxpages+1})"

			buttons = discord.ui.View(
				discord.ui.Button(label="<<<", style=discord.ButtonStyle.blurple, custom_id="left", disabled=timeout),
				discord.ui.Button(label=">>>", style=discord.ButtonStyle.blurple, custom_id="right", disabled=timeout),
				discord.ui.Button(emoji="✖️", style=discord.ButtonStyle.grey, custom_id="exit", disabled=timeout)
			)

			emb = getEmbed(ctx, title, "**All custom commands:**", pages[page])
			return emb, buttons

		emb, buttons = getAllEmbed("load")
		MSG = await ctx.reply(embed=emb, mention_author=False, view=buttons)

		def check(interaction):
			return (interaction.user.id == ctx.author.id and interaction.message.id == MSG.id)

		while True:
			emb, buttons = getAllEmbed()
			await MSG.edit(embed=emb, view=buttons)

			try:
				interaction = await self.client.wait_for("interaction", timeout=60, check=check)
				if interaction.data["custom_id"] == "left" and page > 0:
					page -= 1
				elif interaction.data["custom_id"] == "right" and page < maxpages:
					page += 1
				elif interaction.data["custom_id"] == "exit":
					emb, buttons = getAllEmbed("timeout")
					await MSG.edit(embed=emb, view=buttons)
					return
			except asyncio.TimeoutError:
				emb, buttons = getAllEmbed("timeout")
				await MSG.edit(embed=emb, view=buttons)
				return

def setup(client):
	client.add_cog(PPCog(client))