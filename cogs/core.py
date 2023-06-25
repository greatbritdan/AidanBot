import discord
import discord.ext.commands as CM
import discord.app_commands as AC
from discord import Interaction as Itr

import datetime, re
from github.Issue import Issue
from discord.utils import format_dt

from aidanbot import AidanBot
from utils.config import ConfigManager
from utils.functions import getComEmbed
from utils.checks import ab_check, ab_check_slient, permission_check
from bot import getCONnames, getUCONnames, getGithubtags

import time, asyncio
from random import choice, randint
from typing import Literal

CONvalues = getCONnames()
UCONvalues = getUCONnames()

def replaceWord(text, find, replace):
	return re.sub(r"\b" + find + r"\b", replace, text)

async def permissionStates(itr:Itr, client:AidanBot):
	permissions = [
		"read_messages","manage_channels","manage_roles","manage_emojis_and_stickers","view_audit_log","view_guild_insights","manage_webhooks","manage_guild", "create_instant_invite",
		"change_nickname","manage_nicknames","kick_members","ban_members","moderate_members","send_messages","send_messages_in_threads","create_public_threads","create_private_threads",
		"embed_links","attach_files","add_reactions","external_emojis","external_stickers","mention_everyone","manage_messages","manage_threads","read_message_history",
		"send_tts_messages","use_application_commands","manage_events","administrator"
	]
	requiredperms = {
		"read_messages": "Needed to send messages for commands",
		"manage_webhooks": "Needed to send messages as users for things like /clone and nitron't*",
		"send_messages": "Needed to send messages for commands",
		"send_messages_in_threads": "Needed to send messages for commands in threads",
		"embed_links": "Needed to embed links in /echo and /issue*",
		"external_emojis": "Needed to send private emojis for several commands including /opinion and /games, as well as nitron't",
		"external_stickers": "Needed to send private stickers for nitron't",
		"read_message_history": "Needed to see past messages for /info"
	}
	optionalperms = {
		"manage_roles":"If disabled /role and birthday_role will no longer be avalable",
		"manage_guild":"If disabled guild invites wont be ignored if remove_invites is enabled",
		"mention_everyone":"If disabled qotd_role will not work",
		"attach_files":"If disabled /echo, /clone and nitron't will not have attachment support",
		"manage_messages":"If disabled remove invites and emojin't won't be avalable"
	}
	unnecessaryperms = [
		"manage_channels","manage_emojis_and_stickers","view_audit_log","view_guild_insights","create_instant_invite",
		"change_nickname","manage_nicknames","kick_members","ban_members","moderate_members","create_public_threads","create_private_threads",
		"add_reactions","manage_threads","send_tts_messages","use_application_commands","manage_events","administrator"
	]
	clientmember = await itr.guild.fetch_member(client.user.id)

	rtxt = ""
	for perm in requiredperms:
		if not permission_check(clientmember, itr.channel, perm):
			rtxt += "`" + perm + " - " + requiredperms[perm] + "`\n"
	if rtxt == "":
		rtxt = f"Hoo ray! You have given {client.name} all the neccacary permissions!"
		
	otxt = ""
	for perm in optionalperms:
		if not permission_check(clientmember, itr.channel, perm):
			otxt += "`" + perm + " - " + optionalperms[perm] + "`\n"
	if otxt == "":
		otxt = f"What a CHAD! You have given {client.name} all the optional permissions!"

	utxt = ""
	for perm in unnecessaryperms:
		if permission_check(clientmember, itr.channel, perm):
			utxt += "`" + perm + " - Not needed in this current version`\n"
	if utxt == "":
		utxt = f"Smart Admin! You have not given {client.name} any unnecessary permissions!"

	return [["Required",rtxt],["Optional",otxt],["Unnecessary",utxt]]

class CoreCog(CM.Cog):
	def __init__(self, client:AidanBot):
		self.client = client

		self.uwuify = AC.ContextMenu(name="UwU", callback=self._uwuify)
		self.client.tree.add_command(self.uwuify, guilds=self.client.debug_guilds)

	async def cog_unload(self):
		self.client.tree.remove_command(self.uwuify.name, type=self.uwuify.type)

	@AC.command(name="info", description="Get info about the bot.")
	async def list(self, itr:Itr):
		configcounts = "This server has lower limits, get **40** or more members to unlock larger config values!\n\n`String length limit:` 250\n`Number length limit:` 5\n`Stackable objects limit:` 10"
		if itr.guild.member_count >= 40:
			configcounts = "This server has higher limits because you have **40** or more members!\n\n`String length limit:` 1000\n`Number length limit:` 10\n`Stackable objects limit:` 25"
		if itr.guild.owner.id == self.client.ownerid:
			configcounts = "This server has no limits because it's owned by **Aidan**!\n\n`String length limit:` None\n`Number length limit:` None\n`Stackable objects limit:` None"
		stats = await permissionStates(itr, self.client)

		info = self.client.info.format(ownerid=self.client.ownerid, ownername=self.client.ownername)

		page = 0
		pages = [
			getComEmbed(str(itr.user), self.client, "Info > General", f'''
				{info}

				**VERSION: {self.client.version}**
				**LAST UPDATED: {self.client.lastupdate}**

				> [Aidan's Youtube]({self.client.youtube})
				> [Aidan's Other Youtube]({self.client.youtubeplus})
				> [Aidan's Discord]({self.client.discord})
				> [AidanBot's Github]({self.client.github})
				> [Privacy Policy]({self.client.privacy})
				> [Terms of Service]({self.client.terms})
			'''),
			getComEmbed(str(itr.user), self.client, "Info > Permissions", fields=stats),
			getComEmbed(str(itr.user), self.client, "Info > Config", configcounts),
		]

		def getView(timeout=False):
			view = discord.ui.View(timeout=None)
			view.add_item(discord.ui.Button(label="<-", style=discord.ButtonStyle.blurple, custom_id="left", disabled=timeout))
			view.add_item(discord.ui.Button(label=f"{page+1}/{len(pages)}", style=discord.ButtonStyle.gray, custom_id="display", disabled=True))
			view.add_item(discord.ui.Button(label="->", style=discord.ButtonStyle.blurple, custom_id="right", disabled=timeout))
			return view
		
		await itr.response.send_message(embed=pages[page], view=getView())
		MSG = await itr.original_response()

		def check(checkitr:Itr):
			try:
				return (checkitr.message.id == MSG.id)
			except:
				return False
		while True:
			try:
				butitr:Itr = await self.client.wait_for("interaction", timeout=30, check=check)
				if butitr.user == itr.user:
					await butitr.response.defer()
					if butitr.data["custom_id"] == "left":
						page -= 1
						if page < 0: page = len(pages)-1
					elif butitr.data["custom_id"] == "right":
						page += 1
						if page > len(pages)-1: page = 0
					await itr.edit_original_response(embed=pages[page], view=getView())
				else:
					await butitr.response.send_message(self.client.itrFail(), ephemeral=True)
			except asyncio.TimeoutError:
				return await itr.edit_original_response(view=getView(True))

	@AC.command(name="ping", description="Check the Bot and API latency.")
	async def ping(self, itr:Itr):
		start_time = time.time()
		await itr.response.send_message("Testing Ping...", ephemeral=True)
		apitime = time.time()-start_time
		await itr.edit_original_response(content="Ping Pong motherfliper!```\nBOT: {:.2f} seconds\nAPI: {:.2f} seconds\n```".format(self.client.latency, apitime))

	@AC.command(name="echo", description="Say something as me.")
	@AC.describe(message="What I will say.", attachment="What attachment to attach.")
	async def echo(self, itr:Itr, message:str, attachment:discord.Attachment=None):
		if len(message) >= 1000: return await itr.response.send_message("Message must be 1000 characters or fewer.", ephemeral=True)
		await itr.response.defer(ephemeral=True)
		if attachment and await ab_check_slient(itr, self.client, is_guild=True, bot_has_permission="attach_files"):
			files = await self.client.attachmentsToFiles([attachment])
		else:
			files = []
		await itr.channel.send(message, files=files, allowed_mentions=discord.AllowedMentions(everyone=False, roles=False))
		await itr.edit_original_response(content="Sent!")

	@AC.command(name="clone", description="Say something as another user.")
	@AC.describe(user="User you want to clone.", message="Message you want to send as them.", attachment="What attachment to attach.")
	async def clone(self, itr:Itr, user:discord.Member, message:str, attachment:discord.Attachment=None):
		if len(message) >= 1000: return await itr.response.send_message("Message must be 1000 characters or fewer.", ephemeral=True)

		if self.client.UCON.get_value(user, "clone_disabled", guild=itr.guild):
			await itr.response.send_message("This user has disabled cloning, try a different user!", ephemeral=True)
		else:
			await itr.response.defer(ephemeral=True)
			if attachment and await ab_check_slient(itr, self.client, is_guild=True, bot_has_permission="attach_files"):
				files = await self.client.attachmentsToFiles([attachment])
			else:
				files = []
			await self.client.sendWebhook(itr.channel, f"{user.display_name} (Cloned by {str(itr.user)})", user.display_avatar, message, files)
			await itr.edit_original_response(content="Sent!")

	@AC.command(name="issue", description="Create an issue on GitHub.")
	@AC.describe(title="Title of the post.", body="Body of the embed.", label1="Tag to insert into the post, must be a valid tag.", label2="Tag to insert into the post, must be a valid tag.")
	async def issue(self, itr:Itr, title:str, body:str, label1:str=None, label2:str=None):
		labels = [i for i in [label1, label2] if i and i in self.client.botrepo.get_labels()]
		body += f"\n\n[ Submitted by {str(itr.user)} via /issue ]"
		
		if len(title) >= 200: return await itr.response.send_message("Title must be 200 characters or fewer.", ephemeral=True)
		if len(body) >= 1000: return await itr.response.send_message("Body must be 1000 characters or fewer.", ephemeral=True)

		if len(labels) > 0:
			issue:Issue = self.client.botrepo.create_issue(title=title, body=body, labels=labels)
		else:
			issue:Issue = self.client.botrepo.create_issue(title=title, body=body)
		await itr.response.send_message(f"Submitted!\n\n{issue.html_url}")

	@issue.autocomplete("label1")
	async def issue_label1(self, itr:Itr, current:str):
		return [AC.Choice(name=tag.name, value=tag.name) for tag in self.client.botrepo.get_labels()]
	
	@issue.autocomplete("label2")
	async def issue_label2(self, itr:Itr, current:str):
		return [AC.Choice(name=tag.name, value=tag.name) for tag in self.client.botrepo.get_labels()]

	async def _uwuify(self, itr:Itr, message:discord.Message):
		endings = [";;w;;", ";w;", "UwU", "OwO", ":3", "X3", "^_^", "\\* *sweats* *", "\\* *screams* *", "\\* *huggles tightly* *"]

		# start with owour message
		msg = message.clean_content

		# add some uwunique words
		repwords = {
			"love":"wuv", "cherish":"chwish",
			"Love":"Wuv", "Cherish":"Chwish",
			"LOVE":"WUV", "CHERISH":"CHWISH"
		}
		for repword in repwords:
			msg = replaceWord(msg,repword,repwords[repword])

		# add s-some dashes to make them s-seem nervowous
		mwords = msg.split()
		newmwords = []
		for i, v in enumerate(mwords):
			if randint(1,12) == 12:
				newmwords.append(v[0] + "-" + v)
			else:
				newmwords.append(v)
		msg = " ".join(newmwords)

		# make them sowounds wike a child
		msg = msg.replace("l","w").replace("r","w").replace("L","W").replace("R","W")
		msg = "*" + msg + "* " + choice(endings)

		# print(msg) # dowone
		await itr.response.defer(ephemeral=True)
		try:
			await self.client.sendWebhook(itr.channel, f"{message.author.display_name} (uwuified by {str(itr.user)})", message.author.display_avatar, msg, [])
			await itr.edit_original_response(content="UwUified!")
		except Exception:
			await itr.edit_original_response(content="Error! Try again later!")

	@AC.command(name="role", description="Add a role to you or someone. Can only add [r] roles to yourself without manage_roles.")
	@AC.describe(action="If you want to add or remove a role.", role="Role to add/remove to yourself.", user="User to add/remove the role to.")
	async def role(self, itr:Itr, action:Literal["Add","Remove"], role:discord.Role, user:discord.Member):
		if not await ab_check(itr, self.client, is_guild=True, bot_has_permission="manage_roles"):
			return
		t = "give"
		if action == "Remove":
			t = "take"

		if ((user and user != itr.user) or (not role.name.startswith("[r]"))) and (not itr.channel.permissions_for(itr.user).manage_roles):
			return await itr.response.send_message("Sorry kid, that's for mods only, maybe one day...")
		if role.is_default():
			return await itr.response.send_message(f"I'm sorry... did you- did- did you just try to {t} the @everyone role, I don't know how I'd even do that so I wont.")
		if role.is_premium_subscriber():
			return await itr.response.send_message(f"Sorry, can't {t} roles that are exclusive to server boosters.")
		if role.is_integration():
			return await itr.response.send_message(f"Sorry, can't {t} roles that are integration managed.")
		if role.is_bot_managed():
			return await itr.response.send_message(f"Sorry, can't {t} roles that are bot managed.")
		
		clientmember = await itr.guild.fetch_member(self.client.user.id)
		if role.position >= clientmember.top_role.position:
			return await itr.response.send_message(f"Sorry, can't {t} roles above my top role.")
		if role.position >= itr.user.top_role.position:
			return await itr.response.send_message(f"Sorry, can't {t} roles above your top role.")
		user = user or itr.user
		if action == "Add":
			await user.add_roles(role)
			await itr.response.send_message(f"Added {role.mention} to {user.mention}!")
		elif action == "Remove":
			await user.remove_roles(role)
			await itr.response.send_message(f"Removed {role.mention} from {user.mention}!")
		else:
			await itr.response.send_message(f"```'{action}' is not a valid action```")

	configgroup = AC.Group(name="config", description="Commands to do with configeration.")
	
	@configgroup.command(name="guild", description="Guild configerations.")
	@AC.describe(action="Config action.", name="Variable you're performing action on.", value="New value for this variable.")
	async def guildconfig(self, itr:Itr, action:Literal["List","Set","Reset","Info","Getraw"], name:CONvalues=None, value:str=None):
		if not await ab_check(itr, self.client, is_guild=True, has_mod_role=True):
			return
		await self.config_command(itr, self.client.CON, itr.guild, action, name, value)

	@configgroup.command(name="user", description="User configerations.")
	@AC.describe(action="Config action.", name="Variable you're performing action on.", value="New value for this variable.")
	async def userconfig(self, itr:Itr, action:Literal["List","Set","Reset","Info","Getraw"], name:UCONvalues=None, value:str=None):
		await self.config_command(itr, self.client.UCON, itr.user, action, name, value)
	
	async def config_command(self, itr:Itr, CON:ConfigManager, obj, action="List", name:str=None, value=None):
		values = CON.get_group(obj)
		embed = False
		if action == "List":
			txt = ""
			for name in values:
				if CON.is_restricted(name) != True:
					txt += f"\n**- {name}:** {CON.display_value(name, CON.get_value(obj, name, itr.guild))}"
			embed = getComEmbed(str(itr.user), self.client, f"All values for {obj.name}:", txt)
		elif action == "Info" and name:
			truename = name.split("_")
			truename = " ".join([n.capitalize() for n in truename])
			truetype = CON.type_values[name] # font
			if CON.stackable_values[name]:
				truetype = f"{truetype} (Stackable)"
			truetype = f"**{truetype}**"
			example = f"`/config guild action:Set name:{name} value:{CON.get_example(name)}`"

			fields = [
				["Current Value:", CON.display_value(name, CON.get_value(obj, name, itr.guild))],
				["Type:",          truetype],
				["Default Value:", CON.display_value(name, CON.default_values[name])],
				["Example:",       example],
			]
			if CON.option_values[name]:
				fields.append(["Options:", f"`{', '.join(CON.option_values[name])}`"])
				
			embed = getComEmbed(str(itr.user), self.client, f"Info on {truename} ({name})", CON.desc_values[name], fields=fields)
		elif action == "Getraw" and name:
			txt = f"```{CON.raw_value(name, values[name])}```"
			embed = getComEmbed(str(itr.user), self.client, f"Raw of {name}:", txt)
		elif action == "Reset" and name:
			await CON.reset_value(obj, name)
			embed = getComEmbed(str(itr.user), self.client, content=f"Reset {name} to `{CON.default_values[name]}`!")
		elif action == "Set" and name and value:
			_, error = await CON.set_value(obj, name, value, itr.guild)
			if error:
				embed = getComEmbed(str(itr.user), self.client, content=error)
			else:
				val = CON.get_value(obj, name, itr.guild)
				embed = getComEmbed(str(itr.user), self.client, content=f"Set {name} to {CON.display_value(name, val)}!")
		else:
			return await itr.response.send_message("Seems like you're missing some arguments. Try again.")
		await itr.response.send_message(embed=embed)

async def setup(client:AidanBot):
	await client.add_cog(CoreCog(client), guilds=client.debug_guilds)
