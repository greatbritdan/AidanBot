import discord
from discord.ext import commands, pages
from discord.commands import slash_command, SlashCommandGroup
from discord.utils import get
from discord import Option

from github import Issue

import time
from bot import getCONnames, getUCONnames, getGithubtags
from functions import getComEmbed
from checks import command_checks, command_checks_silent, permission_check

CONvaluenames = getCONnames()
UCONvaluenames = getUCONnames()
GithubTags = getGithubtags()

AC = discord.ApplicationContext
def permissionStates(ctx:AC, client:commands.Bot):
	permissions = [
		"view_channel","manage_channels","manage_roles","manage_emojis_and_stickers","view_audit_log","view_guild_insights","manage_webhooks","manage_guild", "create_instant_invite",
		"change_nickname","manage_nicknames","kick_members","ban_members","moderate_members","send_messages","send_messages_in_threads","create_public_threads","create_private_threads",
		"embed_links","attach_files","add_reactions","external_emojis","external_stickers","mention_everyone","manage_messages","manage_threads","read_message_history",
		"send_tts_messages","use_application_commands","manage_events","administrator"
	]
	requiredperms = {
		"view_channel": "Needed to send messages for commands",
		"manage_webhooks": "Needed to send messages as users for things like /clone and nitron't*",
		"send_messages": "Needed to send messages for commands",
		"send_messages_in_threads": "Needed to send messages for commands in threads",
		"embed_links": "Needed to embed links in /echo and /issue*",
		"external_emojis": "Needed to send private emojis for several commands including /opinion and /games, as well as nitron't",
		"external_stickers": "Needed to send private stickers for nitron't",
		"manage_messages": "Needed to delete messages with invites if remove_invites is enabled",
		"read_message_history": "Needed to see past messages for /info"
	}
	optionalperms = {
		"manage_roles":"If disabled /role and birthday_role will no longer be avalable",
		"manage_guild":"If disabled guild invites wont be ignored if remove_invites is enabled",
		"mention_everyone":"If disabled qotd_role will not work",
		"attach_files":"If disabled /echo, /clone and nitron't will not have attachment support"
	}
	unnecessaryperms = [
		"manage_channels","manage_emojis_and_stickers","view_audit_log","view_guild_insights","create_instant_invite",
		"change_nickname","manage_nicknames","kick_members","ban_members","moderate_members","create_public_threads","create_private_threads",
		"add_reactions","manage_threads","send_tts_messages","use_application_commands","manage_events","administrator"
	]
	clientmember = get(ctx.guild.members, id=client.user.id)

	rtxt = ""
	for perm in requiredperms:
		if not permission_check(clientmember, ctx.channel, perm):
			rtxt += "`" + perm + " - " + requiredperms[perm] + "`\n"
	if rtxt == "":
		rtxt = f"Hoo ray! You have given {client.name} all the neccacary permissions!"
		
	otxt = ""
	for perm in optionalperms:
		if not permission_check(clientmember, ctx.channel, perm):
			otxt += "`" + perm + " - " + optionalperms[perm] + "`\n"
	if otxt == "":
		otxt = f"What a CHAD! You have given {client.name} all the optional permissions!"

	utxt = ""
	for perm in unnecessaryperms:
		if permission_check(clientmember, ctx.channel, perm):
			utxt += "`" + perm + " - Not needed in this current version`\n"
	if utxt == "":
		utxt = f"Smart Admin! You have not given {client.name} any unnecessary permissions!"

	return [["Required",rtxt],["Optional",otxt],["Unnecessary",utxt]]

# man, what a throwback
class CoreCog(discord.Cog):
	def __init__(self, client:commands.Bot):
		self.client = client

	@slash_command(name="info", description="Get info about the bot.")
	async def info(self, ctx:AC):
		infopages = [
			getComEmbed(ctx, self.client, "Info > General", f'''
				{self.client.info}

				[Aidan's Youtube](https://www.youtube.com/c/AidanMapper)
				[Aidan's Discord Server](https://discord.gg/KXrDUZfBpq)
				[{self.client.name}'s Privacy Policy](https://github.com/Aid0nModder/AidanBot#privacy-policy)
				[{self.client.name}'s Terms of Service](https://github.com/Aid0nModder/AidanBot#terms-of-service)

				**Guild Status:** `{self.client.CON.get_value(ctx.guild, "guild_status")}`
			'''),
			getComEmbed(ctx, self.client, "Info > Permissions", "```(options marked with a * may become optional in the future)\n\n- Required: must be enabled as it can cause serious issues to both user and bot.\n- Optional: can be enabled or disabled without major disturbance, though some functionality can be lost.\n- Unnecessary: aren't required yet and should be disabled to keep safe.\n\n(Permissions not mentioned are fine as is, enabled or not.)```", fields=permissionStates(ctx, self.client)),
		]
		infopagesbuttons = [
			pages.PaginatorButton("prev", label="<-", style=discord.ButtonStyle.blurple),
			pages.PaginatorButton("page_indicator", style=discord.ButtonStyle.gray, disabled=True),
			pages.PaginatorButton("next", label="->", style=discord.ButtonStyle.blurple),
		]
		paginator = pages.Paginator(pages=infopages, loop_pages=True, disable_on_timeout=True, timeout=60, use_default_buttons=False, custom_buttons=infopagesbuttons)
		await paginator.respond(ctx.interaction)

	@slash_command(name="ping", description="Check the Bot and API latency.")
	async def ping(self, ctx:AC):
		start_time = time.time()
		await ctx.respond("Testing Ping...", ephemeral=True)
		apitime = time.time() - start_time
		await ctx.edit(content="Ping Pong motherfliper!```\nBOT: {:.2f} seconds\nAPI: {:.2f} seconds\n```".format(self.client.latency, apitime))
		
	@slash_command(name="echo", description="Say something as me.")
	async def echo(self, ctx:AC,
		message:Option(str, "What I will say.", required=True),
		attachment:Option(discord.Attachment, "What attachment will he attach.", required=False)
	):
		if attachment and (not await command_checks_silent(ctx, self.client, is_guild=True, bot_has_permission="attach_files")):
			files = await self.client.attachmentsToFiles([attachment])
		else:
			files = []
		await ctx.send(message, files=files)
		await ctx.respond("Sent!", ephemeral=True)
	
	@slash_command(name="issue", description="Create an issue on GitHub.")
	async def issue(self, ctx:AC,
		title:Option(str, "Title of the post.", required=True),
		body:Option(str, "Body of the post.", required=True),
		label1:Option(str, "1st Tag for the post.", choices=GithubTags, required=False),
		label2:Option(str, "2nd Tag for the post.", choices=GithubTags, required=False),
		label3:Option(str, "3rd Tag for the post.", choices=GithubTags, required=False)
	):
		body += f"\n\n[ Submitted by {str(ctx.author)} via /issue ]"
		labels = [i for i in [label1, label2, label3] if i]
		if len(labels) > 0:
			issue = self.client.botrepo.create_issue(title=title, body=body, labels=labels)
		else:
			issue = self.client.botrepo.create_issue(title=title, body=body)
		await ctx.respond(f"Submitted!\n\n{issue.html_url}")

	@slash_command(name="clone", description="Say something as another user.")
	async def clone(self, ctx:AC,
		user:Option(discord.Member, "Member you want to clone.", required=True),
		message:Option(str, "Message you want to make them send.", required=True),
		attachment:Option(discord.Attachment, "What you want to attach.", required=False),
	):
		if attachment and (not await command_checks_silent(ctx, self.client, is_guild=True, bot_has_permission="attach_files")):
			files = await self.client.attachmentsToFiles([attachment])
		else:
			files = []

		if self.client.UCON.get_value(user, "clone_disabled", guild=ctx.guild):
			await ctx.respond("This user has disabled cloning, try a different user!", ephemeral=True)
		else:
			await ctx.defer(ephemeral=True)
			await self.client.sendWebhook(ctx.channel, user, message, files, " (fake)")
			await ctx.respond("Sent!", ephemeral=True)

	# ROLES #

	rolegroup = SlashCommandGroup("role", "Role commands.")

	@rolegroup.command(name="add", description="Add a role to you or someone. Can only add [r] roles to yourself without manage_roles.")
	async def roleadd(self, ctx:AC, 
		role:Option(discord.Role, "Role to add to yourself.", required=True),
		user:Option(discord.Member, "User to add the role to.", required=False)
	):
		if await command_checks(ctx, self.client, is_guild=True, bot_has_permission="manage_roles"): return
		
		if ((user and user != ctx.author) or (not role.name.startswith("[r]"))) and (not ctx.channel.permissions_for(ctx.author).manage_roles):
			return await ctx.respond("HAHA, Maybe one day kiddo...")
		clientmember = get(ctx.guild.members, id=self.client.user.id)
		if role.position >= clientmember.top_role.position:
			return await ctx.respond("Sorry, can't give roles above my top role.")
		if role.position >= ctx.author.top_role.position:
			return await ctx.respond("Sorry, can't give roles above your top role.")
		user = user or ctx.author
		await user.add_roles(role)
		await ctx.respond(f"Added {role.mention} to {user.mention}!")

	@rolegroup.command(name="remove", description="Remove a role from you or someone. Can only remove [r] roles from yourself without manage_roles.")
	async def roleremove(self, ctx:AC, 
		role:Option(discord.Role, "Role to remove from yourself.", required=True),
		user:Option(discord.Member, "User to remove the role from.", required=False)
	):
		if await command_checks(ctx, self.client, is_guild=True, bot_has_permission="manage_roles"): return

		if ((user and user != ctx.author) or (not role.name.startswith("[r]"))) and (not ctx.channel.permissions_for(ctx.author).manage_roles):
			return await ctx.respond("HAHA, Maybe one day kiddo...")
		clientmember = get(ctx.guild.members, id=self.client.user.id)
		if role.position >= clientmember.top_role.position:
			return await ctx.respond("Sorry, can't remove roles above my top role.")
		if role.position >= ctx.author.top_role.position:
			return await ctx.respond("Sorry, can't remove roles above your top role.")
		user = user or ctx.author
		await user.remove_roles(role)
		await ctx.respond(f"Removed {role.mention} from {user.mention}!")

	# CONFIG #

	configgroup = SlashCommandGroup("config", "Config commands.")
	
	@configgroup.command(name="guild", description="Guild configerations.")
	async def guildconfig(self, ctx:AC,
		action:Option(str, "Config action.", choices=["List","Set","Reset","Info","Getraw"], required=True),
		name:Option(str, "Variable you're performing action on.", choices=CONvaluenames, required=False),
		value:Option(str, "New value for this Variable.", required=False),
	):
		if await command_checks(ctx, self.client, is_guild=True, has_mod_role=True): return
		await self.newconfig_command(ctx, self.client.CON, ctx.guild, action, name, value)

	@configgroup.command(name="user", description="User configerations.")
	async def userconfig(self, ctx:AC,
		action:Option(str, "Config action.", choices=["List","Set","Reset","Info","Getraw"], required=True),
		name:Option(str, "Variable you're performing action on. Required for all but 'List'.", choices=UCONvaluenames, required=False),
		value:Option(str, "New value for this Variable. Required for 'Set'.", required=False)
	):
		await self.newconfig_command(ctx, self.client.UCON, ctx.author, action, name, value)
	
	async def newconfig_command(self, ctx, CON, obj, action="List", name=None, value=None):
		values = CON.get_group(obj)
		embed = False
		if action == "List":
			txt = ""
			for name in values:
				if CON.is_restricted(name) != True:
					txt += f"\n**- {name}:** {CON.display_value(name, CON.get_value(obj, name, ctx.guild))}"
			embed = getComEmbed(ctx, self.client, f"All values for {obj.name}:", txt)
		elif action == "Info" and name:
			txt = f"**Value:** {CON.display_value(name, values[name])}\n**Default Value:** `{CON.default_values[name]}`\n**Description:** '{CON.desc_values[name]}'\n**Type:** `{CON.type_values[name]}`\n**Stackable:** `{CON.stackable_values[name]}`"
			embed = getComEmbed(ctx, self.client, f"Info for {name}:", txt)
		elif action == "Getraw" and name:
			txt = f"```{CON.raw_value(name, values[name])}```"
			embed = getComEmbed(ctx, self.client, f"Raw of {name}:", txt)
		elif action == "Reset" and name:
			await CON.reset_value(obj, name)
			embed = getComEmbed(ctx, self.client, content=f"Reset {name} to `{CON.default_values[name]}`!")
		elif action == "Set" and name and value:
			fulval, error = await CON.set_value(obj, name, value, ctx.guild)
			if error:
				embed = getComEmbed(ctx, self.client, content=error)
			else:
				embed = getComEmbed(ctx, self.client, content=f"Set {name} to {CON.display_value(name, CON.get_value(obj, name, ctx.guild))}!")
		else:
			return await ctx.respond("Seems like you're missing some arguments. Try again.")
		await ctx.respond(embed=embed)

def setup(client):
	client.add_cog(CoreCog(client))
