import discord
from discord.ext import commands

import asyncio, time, emoji, difflib

from functions import getComEmbed, getComEmbedSimple

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
					emb = getComEmbed(ctx, self.client, title, f"Hello, i'm {self.client.name}!", self.client.desc, fields=[["Version:", self.client.version]])
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
		await self.newconfig_command(ctx, self.client.CON, ctx.guild, "guild")

	@commands.command(aliases=["uconfig"])
	@commands.cooldown(1, 5)
	async def userconfig(self, ctx, typ=None, name=None, *, value=None):
		await self.newconfig_command(ctx, self.client.UCON, ctx.author, "user")

	async def newconfig_command(self, ctx, CON, obj, tname):
		class mainView(discord.ui.View):
			@discord.ui.button(label="Set Value", style=discord.ButtonStyle.green, custom_id="set")
			async def set_callback(self, button, interaction):
				modal = ConfigModal("set")
				await interaction.response.send_modal(modal)
			@discord.ui.button(label="Reset Value", style=discord.ButtonStyle.red, custom_id="reset")
			async def reset_callback(self, button, interaction):
				modal = ConfigModal("reset")
				await interaction.response.send_modal(modal)
			@discord.ui.button(label="More Info", style=discord.ButtonStyle.gray, custom_id="more")
			async def more_callback(self, button, interaction):
				modal = ConfigModal("more")
				await interaction.response.send_modal(modal)

		class backView(discord.ui.View):
			@discord.ui.button(label="Go Back", style=discord.ButtonStyle.gray, custom_id="back")
			async def back_callback(self, button, interaction):
				a = "a"

		values = CON.get_group(obj)
		page = "main"
		pagename = False
		pageval = False

		def getconfigembed(timeout=False):
			com = "config"
			if timeout:
				com = com + " (timeout)"

			emb, view = False, False
			if page == "main":
				txt = ""
				for name in values:
					val = str(values[name])
					if len(val) > 32:
						val = val[:32] + "..."
					if not CON.is_restricted(name):
						txt += f"\n**- {name}:** `{val}`"

				emb = getComEmbed(ctx, self.client, com, f"{tname} configeration for {obj.name}:", txt)
				view = mainView()
			else:
				realval = CON.get_value(obj, pagename, guild=ctx.guild)
				if isinstance(realval, discord.TextChannel) or isinstance(realval, discord.VoiceChannel) or isinstance(realval, discord.Role):
					realval = realval.mention
				else:
					realval = f"`{realval}`"

				if page == "more":
					emb = getComEmbed(ctx, self.client, com, f"More info for **{pagename}**:", f"**Value:** {realval}\n**Default Value:** `{CON.default_values[pagename]}`\n**Description:** '{CON.desc_values[pagename]}'\n**Type:** '{CON.type_values[pagename]}'")
				elif page == "set":
					emb = getComEmbed(ctx, self.client, com, "", f"Set **{pagename}** to {realval}.")
				elif page == "setfail":
					emb = getComEmbed(ctx, self.client, com, "", f"Tried to set **{pagename}** to {realval}.\nThe process unfortunatly failed, make sure the type is right!")
				elif page == "reset":
					emb = getComEmbed(ctx, self.client, com, "", f"Reset **{pagename}** to {CON.default_values[pagename]}.")
				view = backView()

			return emb, view

		emb, view = getconfigembed()
		MSG = await ctx.send(embed=emb, view=view)

		def check(interaction):
			return (interaction.user.id == ctx.author.id and interaction.message.id == MSG.id)

		while True:
			try:
				interaction = await self.client.wait_for("interaction", timeout=120, check=check)
				updated = False

				if interaction.data["custom_id"].startswith("configmodel"):
					page = interaction.data["custom_id"].split("-")[1]
					pagename = interaction.data["components"][0]["components"][0]["value"]
					if CON.exists(pagename) and (not CON.is_restricted(pagename)):
						updated = True
						if len(interaction.data["components"]) == 2:
							pageval = interaction.data["components"][1]["components"][0]["value"]

						if page == "set":
							result = await CON.set_value(obj, pagename, pageval, guild=ctx.guild)
							if not result:
								page = "setfail"
						if page == "reset":
							await CON.reset_value(obj, pagename)
					else:
						page = "main"

					await interaction.delete_original_message()
				elif interaction.data["custom_id"] == "back":
					updated = True
					page = "main"

				if updated:
					emb, view = getconfigembed()
					await MSG.edit(embed=emb, view=view)

			except asyncio.TimeoutError:
				emb, view = getconfigembed(True)
				await MSG.edit(embed=emb, view=view)
				return

class ConfigModal(discord.ui.Modal):
	def __init__(self, type):
		self.type = type
		super().__init__(title="Config manager", custom_id="configmodel-"+self.type)

		self.add_item(discord.ui.InputText(style=discord.InputTextStyle.long, label="Please enter a valid name:", placeholder='welcome_message, prefix, etc', value="", required=True))
		if self.type == "set":
			self.add_item(discord.ui.InputText(style=discord.InputTextStyle.long, label="Please enter a new value, be aware of types:", placeholder='for roles and channels, enter a name or id!', value="", required=True))

	async def callback(self, interaction: discord.Interaction):
		await interaction.response.send_message("Working...")
		
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