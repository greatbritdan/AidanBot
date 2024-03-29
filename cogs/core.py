import discord
import discord.ext.commands as CM
import discord.app_commands as AC
from discord import Interaction as Itr

import re, time, asyncio
from typing import Literal

from randfacts import getFact
from github.Issue import Issue

from aidanbot import AidanBot
from utils.functions import getComEmbed
from utils.checks import ab_check, ab_check_slient, permission_check

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

def replaceWord(text, find, replace):
	return re.sub(r"\b" + find + r"\b", replace, text)

async def permissionStates(itr:Itr, client:AidanBot):
	clientmember = await itr.guild.fetch_member(client.user.id)
	
	rtxt = "```"
	for perm in requiredperms:
		if not permission_check(clientmember, itr.channel, perm):
			rtxt += perm + " - " + requiredperms[perm] + "\n"
	rtxt += "```"
	if rtxt == "``````":
		rtxt = f"Hoo ray! You have given {client.name} all the neccacary permissions!"
		
	otxt = "```"
	for perm in optionalperms:
		if not permission_check(clientmember, itr.channel, perm):
			otxt += perm + " - " + optionalperms[perm] + "\n"
	otxt += "```"
	if otxt == "``````":
		otxt = f"What a CHAD! You have given {client.name} all the optional permissions!"

	utxt = "```"
	for perm in unnecessaryperms:
		if permission_check(clientmember, itr.channel, perm):
			utxt += perm + " - Not needed in this current version\n"
	utxt += "```"
	if utxt == "``````":
		utxt = f"Smart Admin! You have not given {client.name} any unnecessary permissions!"

	return [["Required",rtxt],["Optional",otxt],["Unnecessary",utxt]]

class CoreCog(CM.Cog):
	def __init__(self, client:AidanBot):
		self.client = client

	@AC.command(name="botinfo", description="Get info about the bot.")
	async def list(self, itr:Itr):
		permstats = await permissionStates(itr, self.client)
		configstats = [["This server has lower limits, get **40** or more members to unlock larger config values!", "```String length limit: 250\nNumber length limit: 5\nStackable objects limit: 10```"]]
		if itr.guild.member_count >= 40:
			configstats = [["This server has higher limits because you have **40** or more members!", "```String length limit: 1000\nNumber length limit: 10\nStackable objects limit: 25```"]]
		if itr.guild.owner.id == self.client.ownerid:
			configstats = [[f"This server has no limits because it's owned by {self.client.ownername}!", "```String length limit: None\nNumber length limit: None\nStackable objects limit: None```"]]
		info = self.client.info.format(ownerid=self.client.ownerid, ownername=self.client.ownername)

		page = 0
		pages = [
			getComEmbed(self.client, content=f'''
				{info}

				**VERSION: {self.client.version}**
				**LAST UPDATED: {self.client.lastupdate}**

				> [Aidan's Youtube]({self.client.youtube})
				> [Aidan's Other Youtube]({self.client.youtubeplus})
				> [Aidan's Discord]({self.client.discord})
				> [AidanBot's Github]({self.client.github})
				> [Privacy Policy]({self.client.privacy})
				> [Terms of Service]({self.client.terms})
			''', command="Info > General", footer="Page 1/3"),
			getComEmbed(self.client, command="Info > Permissions", footer="Page 2/3", fields=permstats),
			getComEmbed(self.client, command="Info > Configuration", footer="Page 3/3", fields=configstats),
		]

		def getView(timeout=False):
			view = discord.ui.View(timeout=None)
			view.add_item(discord.ui.Button(label="<-", style=discord.ButtonStyle.blurple, custom_id="left", disabled=timeout))
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
		embed = getComEmbed(self.client, "Testing Ping...", command="Ping")
		await itr.response.send_message(embed=embed, ephemeral=True)
		apitime = time.time()-start_time
		embed = getComEmbed(self.client, "Ping Pong motherfliper!", "```\nBOT: {:.2f} seconds\nAPI: {:.2f} seconds\n```".format(self.client.latency, apitime), command="Ping")
		await itr.edit_original_response(embed=embed)

	@AC.command(name="echo", description="Say something as me.")
	@AC.describe(message="What I will say.", attachment="What attachment to attach.")
	async def echo(self, itr:Itr, message:str, attachment:discord.Attachment=None):
		if len(message) >= 1000:
			return await itr.response.send_message("Message must be 1000 characters or fewer, try again!", ephemeral=True)
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
		if len(message) >= 1000:
			return await itr.response.send_message("Message must be 1000 characters or fewer, try again!", ephemeral=True)

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
	@AC.describe(title="Title of the post.", body="Body of the embed.", label1="Tag to insert into the post, must be a valid tag.",
	    label2="Tag to insert into the post, must be a valid tag.", attachment="What attachment to attach.")
	async def issue(self, itr:Itr, title:str, body:str, label1:str=None, label2:str=None, attachment:discord.Attachment=None):
		glabels = [i.name for i in self.client.botrepo.get_labels()]
		labels = [i for i in [label1, label2] if i and i in glabels]

		dbody = body
		body += f"\n\n[ Submitted by {str(itr.user)} via /issue ]"
		
		if len(title) >= 200: return await itr.response.send_message("Title must be 200 characters or fewer.", ephemeral=True)
		if len(body) >= 1000: return await itr.response.send_message("Body must be 1000 characters or fewer.", ephemeral=True)

		if len(labels) > 0:
			issue:Issue = self.client.botrepo.create_issue(title=title, body=body, labels=labels)
		else:
			issue:Issue = self.client.botrepo.create_issue(title=title, body=body)

		dbody = (dbody[:100] + "...") if len(dbody) > 100 else dbody
		embed = getComEmbed(self.client, f"Submitted - {issue.title} #{issue.number}", f"```{dbody}```\n[View Issue]({issue.html_url})", command="Issue")
		embed.set_image(url=f"https://opengraph.githubassets.com/38d571ceec6df9de6f4fce604edf337d9ffc782aa7f123aaaae74c9fbe824428/Aid0nModder/AidanBot/issues/{issue.number}")
		await itr.response.send_message(embed=embed)

	@issue.autocomplete("label1")
	async def issue_label1(self, itr:Itr, current:str):
		tags = [tag.name for tag in self.client.botrepo.get_labels()]
		return [AC.Choice(name=name, value=name) for name in tags if current.lower() in name.lower()][:25]
	
	@issue.autocomplete("label2")
	async def issue_label2(self, itr:Itr, current:str):
		tags = [tag.name for tag in self.client.botrepo.get_labels()]
		return [AC.Choice(name=name, value=name) for name in tags if current.lower() in name.lower()][:25]

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
			await itr.response.send_message(f"'{action}' is not a valid action")

	@AC.command(name="fact", description="Get a random fact.")
	async def fact(self, itr:Itr):
		fact = getFact()
		await itr.response.send_message(f"Did you know? {fact}")

async def setup(client:AidanBot):
	await client.add_cog(CoreCog(client), guilds=client.debug_guilds)