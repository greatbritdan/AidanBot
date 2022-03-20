import discord
from discord.ext import commands

import asyncio, time, emoji, difflib

from functions import getComEmbed

import json
with open('./data/commanddata.json') as file:
	temp = json.load(file)
	DESC = temp["desc"]
	HELPORDER = temp["help"]

class ImportantCog(commands.Cog):
	def __init__(self, client):
		self.client = client

	@commands.command()
	@commands.cooldown(1, 3)
	async def ping(self, ctx):
		start_time = time.time()
		message = await ctx.reply("Testing Ping...", mention_author=False)
		apitime = start_time - time.time()
		await message.edit(content="Ping Pong motherfliper!```\nBOT: {:.2f} seconds\nAPI: {:.2f} seconds\n```".format(self.client.latency, apitime))

	@commands.command(aliases=["helpmeh"])
	@commands.cooldown(1, 10)
	async def help(self, ctx, name:str=None):
		prefix = self.client.getprefix(self.client, ctx.message)
		if name:
			guess = False
			command = await getCommand(ctx, self.client, name)
			if command == "NotWork":
				guess = True
				command = await getCommand(ctx, self.client, name, True) # couldn't find exact match, get aproximation

			if command != "NotWork": # Get help on a spesific command
				commandname = command.name
				ogcommandname = name
				name = f"{prefix}{commandname}"
				if len(command.aliases) > 0:
					allist = []
					for al in command.aliases:
						allist.append(f"{prefix}{al}")
					tlist = ", ". join(allist)
					name += f" `AKA {tlist}`"

				fs = [
					#["Args:", f"{prefix}{command.name} {command.signature}"],
					["Description:", DESC[commandname][0]],
				]
				if DESC[commandname][1]:
					fs.append(["Cooldown:", f"1 command per {DESC[commandname][1]} seconds"])
				if DESC[commandname][2]:
					fs.append(["Permission(s) Required:", DESC[commandname][2]])
				if DESC[commandname][3]:
					fs.append(["Unstable:", "This command is listed as unstable, [More Info](https://github.com/Aid0nModder/AidanBot/blob/main/README.md#unstable-commands)."])

				emb = getComEmbed(ctx, self.client, f"Help > {prefix}{command.name}", name, f"**{prefix}{command.name} {command.signature}**\n(*<> is required, [] is optional, [blabla=value] means default argument is value.*)", fields=fs)
				if guess:
					await ctx.reply(f"(Aproximated from {ogcommandname})", embed=emb, mention_author=False)
				else:
					await ctx.reply(embed=emb, mention_author=False)
			else:
				await ctx.send("Couldn't find command with that name :/")
				return
		else:
			categorycommands = {"Info":""}
			for order in HELPORDER:
				txt = ""
				for commandname in HELPORDER[order][2]:
					command = await getCommand(ctx, self.client, commandname)
					if command == "NotWork":
						continue
					desc = DESC[commandname][0].format(prefix=prefix) or "No description."
					if DESC[commandname][3]:
						desc += " (unstable) [More Info](https://github.com/Aid0nModder/AidanBot/blob/main/README.md#unstable-commands)"
					txt = txt + f"`{prefix}{command.name}`: {desc}\n"
				if txt != "":
					categorycommands[order] = txt

			page = "Info"
			def getHelpEmbed(typ=None):
				title, timeout = "Help", False
				if typ == "load":
					title = "Help (loading...)"
				elif typ == "timeout":
					title, timeout = "Help (timeout)", True
				else:
					title = f"Help ({page})"

				if page == "Info":
					emb = getComEmbed(ctx, self.client, title, f"Hello, i'm {self.client.name}!", self.client.desc)
				else:
					emb = getComEmbed(ctx, self.client, title, f"All {page} Commands:", f"Run {prefix}help <command> to get more help on a command!\n\n{categorycommands[page]}")

				options = []
				for order in HELPORDER:
					options.append( discord.SelectOption(label=order, description=HELPORDER[order][0], emoji=emoji.emojize(HELPORDER[order][1])) )
				select = discord.ui.View( discord.ui.Select(placeholder="Choose Category", options=options, disabled=timeout, custom_id="select") )
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

	@commands.command(aliases=["config", "gconfig"])
	@commands.cooldown(1, 5)
	@commands.has_permissions(administrator=True)
	async def guildconfig(self, ctx, typ=None, name=None, *, value=None):
		await self.config_command(ctx, self.client.CON, ctx.guild, typ, name, value)

	@commands.command(aliases=["uconfig"])
	@commands.cooldown(1, 5)
	async def userconfig(self, ctx, typ=None, name=None, *, value=None):
		await self.config_command(ctx, self.client.UCON, ctx.author, typ, name, value)

	async def config_command(self, ctx, CON, obj, typ, name, value):
		edited = False
		exists = CON.get_all(obj)
		if not exists:
			CON.values[str(obj.id)] = {}
			edited = True

		for n in CON.default_values:
			if n not in CON.values[str(obj.id)]:
				CON.values[str(obj.id)][n] = CON.default_values[n]
				edited = True

		txt, txt2 = "Please provide a valid action. (Actions are `list`, `get`, `set` or `info`)", ""
		if typ:
			if typ == "list":
				list = CON.get_all(obj)
				txt = f"List of all values for {obj.name}"
				txt2 = ""
				for item in list:
					if item != "id":
						txt2 += f"\n**- {item}**: `{str(list[item])}`"
			elif typ == "get":
				if not name:
					txt = f"Please provide a name."
				else:
					value = CON.get_value(obj, name)
					txt = f"{name} is `{value}`."
			elif typ == "set":
				if not name:
					txt = f"Please provide a name."
				elif not value:
					txt = f"Please provide a value."
				elif CON.is_restricted(name):
					txt = f"This is a restricted value."
				else:
					if value.lower() == "true":
						value = True
					elif value.lower() == "false":
						value = False
					else:
						try:
							value = int(value)
						except ValueError:
							value = str(value)

					suc = CON.set_value(obj, name, value)
					if suc:
						txt = f"{name} has been set to `{str(value)}`."
						edited = True
					else:
						txt = f"{name} cannot be set."
			elif typ == "info":
				if not name:
					txt = f"Please provide a name."
				else:
					if name in CON.desc_values:
						txt = ""
						txt2 = CON.desc_values[name]
					else:
						txt = f"{name} cannot be set."

		emb = getComEmbed(ctx, self.client, "Config", txt, txt2)
		await ctx.reply(embed=emb, mention_author=False)

		if edited:
			await CON.values_msgupdate("save")

async def getCommand(ctx, client, commandparam, getaprox=False):
	com = None
	for command in client.commands:
		if getaprox:
			if commandparam.lower() in command.name.lower():
				com = command
			elif difflib.SequenceMatcher(None,command.name.lower(),commandparam.lower()).ratio() > 0.7: # mostly accurate
				com = command
			# todo: add aliases support
		else:
			if command.name.lower() == commandparam.lower():
				com = command
			elif command.aliases and commandparam.lower() in command.aliases:
				com = command

	if not com:
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