import discord
from discord.ext import commands
from discord.utils import find

import asyncio

from functions import getComEmbed

import json
with open('./commanddata.json') as file:
	temp = json.load(file)
	DESC = temp["desc"]
	ORDER = temp["order"]

class ImportantCog(commands.Cog):
	def __init__(self, client):
		self.client = client

	@commands.command(description=DESC["help"], aliases=["helpmeh"])
	@commands.cooldown(1, 10)
	async def help(self, ctx, name:str=None):
		prefix = self.client.prefix

		if name: 
			command = await getCommand(ctx, self.client, name)
			if command != "NotWork": # Get help on a spesific command
				name = f"{prefix}{command.name}"
				if len(command.aliases) > 0:
					allist = []
					for al in command.aliases:
						allist.append(f"{prefix}{al}")
					tlist = ", ". join(allist)
					name += f" `AKA {tlist}`"

				fs = [
					["Args:", f"{prefix}{command.name} {command.signature}"],
					["Description:", command.description.format(prefix=prefix)]
				]

				emb = getComEmbed(ctx, self.client, f"Help > {prefix}{command.name}", name, "*<> is required, [] is optional, [blabla=value] means default argument is value.*", fields=fs)
				await ctx.reply(embed=emb, mention_author=False)
			else:
				await ctx.send("Couldn't find command with that name :/")
				return
		else:
			categoriesselect = {
				"Info": ["Bot info", "📘"],
				"Important": ["Core bot commands.", "⚙️"],
				"Moderation": ["Server moderation commands.", "🔨"],
				"General": ["General bot commands.", "📄"],
				"Opinion": ["The fun commands.", "📣"],
				"Games": ["The game commands.", "🎮"],
				"Image": ["Image manipulation commands.", "🖌️"],
				"Pip0ns Palace": ["Commands exclusive to Pip0n's palace", "<:UpPipe:836997889234042910>"],
				"Owner": ["Commands only Aidan can use.", "<:AidanSmug:837001740947161168>"]
			}
			categories = {
				"Info": ""
			}
			for order in ORDER:
				txt = ""
				for commandname in ORDER[order]:
					command = await getCommand(ctx, self.client, commandname)
					if command == "NotWork":
						continue
					desc = command.description.format(prefix=prefix) or "No description."
					if "\n" in desc:
						desc = desc.splitlines()[0]
					txt = txt + f"`{prefix}{command.name}`: {desc}\n"
				if txt != "":
					categories[order] = txt

			page = "Info"
			def getHelpEmbed(typ=None):
				title, timeout = "Help", False
				if typ == "load":
					title = "Help (loading...)"
				elif typ == "timeout":
					title, timeout = "Help (timeout)", True
				else:
					title = f"Help ({page})"

				emb = getComEmbed(ctx, self.client, title, f"{page}:", f"Run {prefix}help <command> to get more help on a command!\n\n{categories[page]}")
				if page == "Info":
					emb = getComEmbed(ctx, self.client, title, f"Hello, i'm {self.client.name}!", self.client.desc)

				options = []
				for cat in categories:
					options.append(discord.SelectOption(label=cat, description=categoriesselect[cat][0], emoji=categoriesselect[cat][1]))
				select = discord.ui.View(
					discord.ui.Select(placeholder="Choose Category", options=options, disabled=timeout, custom_id="select")
				)

				return emb, select

			emb, buttons = getHelpEmbed("load")
			MSG = await ctx.reply(embed=emb, mention_author=False, view=buttons)

			def check(interaction):
				return (interaction.user.id == ctx.author.id and interaction.message.id == MSG.id)

			while True:
				emb, buttons = getHelpEmbed()
				await MSG.edit(embed=emb)

				try:
					interaction = await self.client.wait_for("interaction", timeout=60, check=check)
					if interaction.data["custom_id"] == "select" and interaction.data["values"][0]:
						page = interaction.data["values"][0]
						emb, buttons = getHelpEmbed()
						await MSG.edit(embed=emb, view=buttons)

				except asyncio.TimeoutError:
					emb, buttons = getHelpEmbed("timeout")
					await MSG.edit(embed=emb, view=buttons)
					return
					
	@commands.command(description=DESC["role"])
	@commands.cooldown(1, 10)
	async def role(self, ctx, *, name):
		r = find(lambda m: name.lower() in m.name.lower(), ctx.guild.roles)
		if r == None:
			await ctx.reply("Try again, i couldn't find this role.", mention_author=False)
			return
		if ctx.author.guild_permissions.manage_roles or r.name.startswith("[r]"):
			if r == ctx.author.top_role:
				await ctx.reply(f"You can't remove your top role", mention_author=False)
				return
			if r in ctx.author.roles:
				await ctx.author.remove_roles(r)
				await ctx.reply(f"Removed {r.name}", mention_author=False)
			else:
				await ctx.author.add_roles(r)
				await ctx.reply(f"Added {r.name}", mention_author=False)
		else:
			await ctx.reply(f"{r.name} is not a role that can be added by anyone", mention_author=False)

async def getCommand(ctx, client, commandparam):
	com = None
	for command in client.commands:
		if command.name.lower() == commandparam.lower():
			com = command
		elif command.aliases and commandparam.lower() in command.aliases:
			com = command
	if not com or com.hidden:
		return "NotWork"
	try:
		succ = await com.can_run(ctx)
		if not succ:
			return "NotWork"
	except commands.CommandError:
		return "NotWork"
	return com

def setup(client):
	client.add_cog(ImportantCog(client))