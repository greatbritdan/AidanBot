import discord
import discord.ext.commands as CM
import discord.app_commands as AC
from discord import Interaction as Itr
from discord import Embed, Color

import datetime, re
from github.Issue import Issue

from aidanbot import AidanBot
from functions import getComEmbed
from cooldowns import cooldown_core, cooldown_UwU, cooldown_etc
from checks import ab_check, ab_check_slient, permission_check
from bot import getCONnames, getUCONnames, getGithubtags

import time, asyncio
from random import choice, randint
from typing import Literal

githublabels = getGithubtags()
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
		pass

	@AC.command(name="info", description="Get info about the bot.")
	@CM.dynamic_cooldown(cooldown_etc, CM.BucketType.user)
	async def list(self, itr:Itr):
		configcounts = "Your server has lower limits, get **40** or more members to unlock larger config values!\n\n`String length limit:` 250\n`Number length limit:` 5\n`Stackable objects limit:` 10"
		if itr.guild.member_count >= 40:
			configcounts = "This is only avalable for servers with **40** or more members!\n\n`String length limit:` 750\n`Number length limit:` 10\n`Stackable objects limit:` 25"
		stats = await permissionStates(itr, self.client)

		page = 0
		pages = [
			getComEmbed(str(itr.user), self.client, "Info > General", f'''
				{self.client.info}

				[Aidan's Youtube](https://www.youtube.com/c/AidanMapper)
				[Aidan's Discord Server](https://discord.gg/KXrDUZfBpq)
				[{self.client.name}'s Privacy Policy](https://github.com/Aid0nModder/AidanBot#privacy-policy)
				[{self.client.name}'s Terms of Service](https://github.com/Aid0nModder/AidanBot#terms-of-service)
			'''),
			getComEmbed(str(itr.user), self.client, "Info > Permissions", "```(options marked with a * may become optional in the future)\n\n- Required: must be enabled as it can cause serious issues to both user and bot.\n- Optional: can be enabled or disabled without major disturbance, though some functionality can be lost.\n- Unnecessary: aren't required yet and should be disabled to keep safe.\n\n(Permissions not mentioned are fine as is, enabled or not.)```", fields=stats),
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
	@CM.dynamic_cooldown(cooldown_core, CM.BucketType.user)
	async def ping(self, itr:Itr):
		start_time = time.time()
		await itr.response.send_message("Testing Ping...", ephemeral=True)
		apitime = time.time()-start_time
		await itr.edit_original_response(content="Ping Pong motherfliper!```\nBOT: {:.2f} seconds\nAPI: {:.2f} seconds\n```".format(self.client.latency, apitime))

	@AC.command(name="echo", description="Say something as me.")
	@AC.describe(message="What I will say.", attachment="What attachment to attach.")
	@CM.dynamic_cooldown(cooldown_core, CM.BucketType.user)
	async def echo(self, itr:Itr, message:str, attachment:discord.Attachment=None):
		if len(message) >= 1000: return await itr.response.send_message("Message must be 1000 characters or fewer.", ephemeral=True)
		await itr.response.defer(ephemeral=True)
		if attachment and await ab_check_slient(itr, self.client, is_guild=True, bot_has_permission="attach_files"):
			files = await self.client.attachmentsToFiles([attachment])
		else:
			files = []
		await itr.channel.send(message, files=files, allowed_mentions=discord.AllowedMentions(everyone=False, roles=False))
		await itr.edit_original_response(content="Sent!")

	@AC.command(name="embed", description="Send a custom embed.")
	@AC.describe(
		title="Title of the embed.", description="Description of the embed.", color="Color of the embed.", timestamp="If the embed shows the timestamp.", header="Header of the embed.",
		headerimg="Image (Link) that will appear beside the header.", footer="Footer of the embed.", footerimg="Image (Link) that will appear beside the footer.",
		image="Image (Link) to appear below the embed content", thumbnail="Image (Link) to appear on the right side of the embed content.", field1="A field of the emebd, split title and value with '|'",
		field2="A field of the emebd, split title and value with '|'", field3="A field of the emebd, split title and value with '|'"
	)
	@CM.dynamic_cooldown(cooldown_core, CM.BucketType.user)
	async def embed(self, itr:Itr,
		title:str, description:str, color:Literal["System gray","System red","System dark red","Red","Green","Blue","Gold","Gray"]="System gray", timestamp:bool=False, header:str="",
		headerimg:str=None, footer:str="", footerimg:str=None, image:str=None, thumbnail:str=None, field1:str=None, field2:str=None, field3:str=None
	):
		try:
			await itr.response.defer(ephemeral=True)
			if color == "System gray": color = Color.from_rgb(20, 29, 37)
			if color == "System red": color = Color.from_rgb(220, 29, 37)
			if color == "System dark red": color = Color.from_rgb(120, 29, 37)
			if color == "Red": color = Color.from_rgb(225, 15, 15)
			if color == "Green": color = Color.from_rgb(15, 225, 15)
			if color == "Blue": color = Color.from_rgb(15, 15, 225)
			if color == "Gold": color = Color.from_rgb(225, 120, 15)
			if color == "Gray": color = Color.from_rgb(165, 165, 165)

			if timestamp:
				timestamp = datetime.datetime.now()
			else:
				timestamp = None

			emb = Embed(title=title, description=description, color=color, timestamp=timestamp)
			if footer != "" or footerimg:
				emb.set_footer(text=footer, icon_url=footerimg)
			if header != "" or headerimg:
				emb.set_author(name=header, icon_url=headerimg)
			if image:
				emb.set_image(url=image)
			if thumbnail:
				emb.set_thumbnail(url=thumbnail)

			if field1:
				field1 = field1.split("|")
				if len(field1) > 2 and field1[2] == "true":
					emb.add_field(name=field1[0], value=field1[1], inline=True)
				else:
					emb.add_field(name=field1[0], value=field1[1], inline=False)
			if field2:
				field2 = field2.split("|")
				if len(field2) > 2 and field2[2] == "true":
					emb.add_field(name=field2[0], value=field2[1], inline=True)
				else:
					emb.add_field(name=field2[0], value=field2[1], inline=False)
			if field3:
				field3 = field3.split("|")
				if len(field3) > 2 and field3[2] == "true":
					emb.add_field(name=field3[0], value=field3[1], inline=True)
				else:
					emb.add_field(name=field3[0], value=field3[1], inline=False)

			await itr.channel.send(embed=emb)
			await itr.edit_original_response("Embeded!")
		except ValueError:
			return await itr.response.send_message("Embed was too boog.", ephemeral=True)

	@AC.command(name="clone", description="Say something as another user.")
	@AC.describe(user="User you want to clone.", message="Message you want to send as them.", attachment="What attachment to attach.")
	@CM.dynamic_cooldown(cooldown_core, CM.BucketType.user)
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
			await self.client.sendWebhook(itr.channel, user, message, files, f" (Cloned by {str(itr.user)})")
			await itr.edit_original_response(content="Sent!")

	@AC.command(name="issue", description="Create an issue on GitHub.")
	@AC.describe(title="Title of the post.", body="Body of the embed.", label1="Tag to insert into the post.", label2="Tag to insert into the post.", label3="Tag to insert into the post.")
	@CM.dynamic_cooldown(cooldown_core, CM.BucketType.user)
	async def issue(self, itr:Itr, title:str, body:str, label1:githublabels=None, label2:githublabels=None, label3:githublabels=None):
		if len(title) >= 200: return await itr.response.send_message("Title must be 200 characters or fewer.", ephemeral=True)
		if len(body) >= 1000: return await itr.response.send_message("Body must be 1000 characters or fewer.", ephemeral=True)

		body += f"\n\n[ Submitted by {str(itr.user)} via /issue ]"
		labels = [i for i in [label1, label2, label3] if i]
		if len(labels) > 0:
			issue:Issue = self.client.botrepo.create_issue(title=title, body=body, labels=labels)
		else:
			issue:Issue = self.client.botrepo.create_issue(title=title, body=body)
		await itr.response.send_message(f"Submitted!\n\n{issue.html_url}")

	@CM.dynamic_cooldown(cooldown_UwU, CM.BucketType.channel)
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
			await self.client.sendWebhook(itr.channel, message.author, msg, [], f" (uwuified by {str(itr.user)})")
			await itr.edit_original_response(content="UwUified!")
		except Exception:
			await itr.edit_original_response(content="Error! Try again later!")

	@AC.command(name="role", description="Add a role to you or someone. Can only add [r] roles to yourself without manage_roles.")
	@AC.describe(action="If you want to add or remove a role.", role="Role to add/remove to yourself.", user="User to add/remove the role to.")
	@CM.dynamic_cooldown(cooldown_core, CM.BucketType.user)
	async def role(self, itr:Itr, action:Literal["Add","Remove"], role:discord.Role, user:discord.Member):
		if not await ab_check(itr, self.client, is_guild=True, bot_has_permission="manage_roles"):
			return

		if ((user and user != itr.user) or (not role.name.startswith("[r]"))) and (not itr.channel.permissions_for(itr.user).manage_roles):
			return await itr.response.send_message("Sorry kid, that's for mods only, maybe one day...")
		clientmember = await itr.guild.fetch_member(self.client.user.id)
		if role.position >= clientmember.top_role.position:
			return await itr.response.send_message("Sorry, can't give roles above my top role.")
		if role.position >= itr.user.top_role.position:
			return await itr.response.send_message("Sorry, can't give roles above your top role.")
		user = user or itr.user
		if action == "Add":
			await user.add_roles(role)
			await itr.response.send_message(f"Added {role.mention} to {user.mention}!")
		elif action == "Remove":
			await user.remove_roles(role)
			await itr.response.send_message(f"Removed {role.mention} from {user.mention}!")
		else:
			await itr.response.send_message(f"'We got a, number one victory royale, yeah Fortnite we bou-' how the hell did you get here, get the heck out.\n```'{action}' is not a valid action```")

	configgroup = AC.Group(name="config", description="Commands to do with configeration.")
	
	@configgroup.command(name="guild", description="Guild configerations.")
	@AC.describe(action="Config action.", name="Variable you're performing action on.", value="New value for this variable.")
	@AC.autocomplete()
	@CM.dynamic_cooldown(cooldown_core, CM.BucketType.user)
	async def guildconfig(self, itr:Itr, action:Literal["List","Set","Reset","Info","Getraw"], name:CONvalues=None, value:str=None, guild:str=None):
		if not await ab_check(itr, self.client, is_guild=True, has_mod_role=True):
			return
		await self.config_command(itr, self.client.CON, itr.guild, action, name, value)

	@configgroup.command(name="user", description="User configerations.")
	@AC.describe(action="Config action.", name="Variable you're performing action on.", value="New value for this variable.")
	@CM.dynamic_cooldown(cooldown_core, CM.BucketType.user)
	async def userconfig(self, itr:Itr, action:Literal["List","Set","Reset","Info","Getraw"], name:UCONvalues=None, value:str=None):
		await self.config_command(itr, self.client.UCON, itr.user, action, name, value)
	
	async def config_command(self, itr:Itr, CON, obj, action="List", name=None, value=None):
		values = CON.get_group(obj)
		embed = False
		if action == "List":
			txt = ""
			for name in values:
				if CON.is_restricted(name) != True:
					txt += f"\n**- {name}:** {CON.display_value(name, CON.get_value(obj, name, itr.guild))}"
			embed = getComEmbed(str(itr.user), self.client, f"All values for {obj.name}:", txt)
		elif action == "Info" and name:
			txt = f"**Value:** {CON.display_value(name, values[name])}\n**Default Value:** `{CON.default_values[name]}`\n**Description:** '{CON.desc_values[name]}'\n**Type:** `{CON.type_values[name]}`\n**Stackable:** `{CON.stackable_values[name]}`"
			embed = getComEmbed(str(itr.user), self.client, f"Info for {name}:", txt)
		elif action == "Getraw" and name:
			txt = f"```{CON.raw_value(name, values[name])}```"
			embed = getComEmbed(str(itr.user), self.client, f"Raw of {name}:", txt)
		elif action == "Reset" and name:
			await CON.reset_value(obj, name)
			embed = getComEmbed(str(itr.user), self.client, content=f"Reset {name} to `{CON.default_values[name]}`!")
		elif action == "Set" and name and value:
			fulval, error = await CON.set_value(obj, name, value, itr.guild)
			if error:
				embed = getComEmbed(str(itr.user), self.client, content=error)
			else:
				embed = getComEmbed(str(itr.user), self.client, content=f"Set {name} to {CON.display_value(name, CON.get_value(obj, name, itr.guild))}!")
		else:
			return await itr.response.send_message("Seems like you're missing some arguments. Try again.")
		await itr.response.send_message(embed=embed)

async def setup(client:AidanBot):
	await client.add_cog(CoreCog(client), guilds=client.debug_guilds)
