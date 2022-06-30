import discord
from discord.commands import slash_command, SlashCommandGroup
from discord import Option
from discord.utils import get, basic_autocomplete

import time
from random import choice

from functions import getComEmbed
from checks import command_checks

async def auto_CONvaluenames(ctx):
	return [val for val in ctx.bot.CON.valid_values if not ctx.bot.CON.is_restricted(val)]
async def auto_UCONvaluenames(ctx):
	return [val for val in ctx.bot.UCON.valid_values if not ctx.bot.UCON.is_restricted(val)]
async def auto_githubtags(ctx):
	return [tag.name for tag in ctx.bot.botrepo.get_labels()]

# man, what a throwback
class CoreCog(discord.Cog):
	def __init__(self, client):
		self.client = client

	@slash_command(name="info", description="Get info about the bot.")
	async def info(self, ctx):
		info = f'''

		**VERSION:** {self.client.version}
		**GUILD STATUS:** {self.client.CON.get_value(ctx.guild, "guild_status")}
		
		[Aidan's Youtube](https://www.youtube.com/c/AidanMapper)
		[Aidan's Discord Server](https://discord.gg/KXrDUZfBpq)
		[AidanBot's Privacy Policy](https://github.com/Aid0nModder/AidanBot#privacy-policy)
		[AidanBot's Terms of Service](https://github.com/Aid0nModder/AidanBot#terms-of-service)
		
		If you find a bug or he has made a typo <:AidanSmug:837001740947161168>,
		you can report it to Aidan on his server in one of the bot chats.
		You can also suggest features in the suggestion channel on his server!
		'''
		perms = '''
		The Permissions I come with are only the ones I need, But I understand if you don't like the sound of some. Don't worry tho, Some can be disabled safely, just remeber some functionality will be lost.
		
			- Manage Roles: You won't be able to use /role and `join_role`/`birthday_role` will not work.
			- Manage Server: Your own server invites will be removed from your server.
			- Ping Everyone/Here/Role: `qotd_role` will not ping unless it is set to "everyone can ping this role"
		'''
		embed = getComEmbed(ctx, self.client, f"Info for {self.client.name}", self.client.info + info, fields=[["Permissions", perms]])
		await ctx.respond(embed=embed)

	@slash_command(name="ping", description="Check the Bot and API latency.")
	async def ping(self, ctx):
		start_time = time.time()
		await ctx.respond("Testing Ping...", ephemeral=True)
		apitime = time.time() - start_time
		await ctx.edit(content="Ping Pong motherfliper!```\nBOT: {:.2f} seconds\nAPI: {:.2f} seconds\n```".format(self.client.latency, apitime))

	@slash_command(name="echo", description="Say something as AidanBot.")
	async def echo(self, ctx, content:Option(str, "What AidanBot will say.", required=True)):
		await ctx.send(content)
		await ctx.delete()
	
	@slash_command(name="issue", description="Create an issue on GitHub.")
	async def issue(self, ctx,
		title:Option(str, "Title of the post.", required=True),
		body:Option(str, "Body of the post.", required=True),
		label1:Option(str, "Tag for the post.", autocomplete=basic_autocomplete(auto_githubtags), required=False),
		label2:Option(str, "Another Tag for the post.", autocomplete=basic_autocomplete(auto_githubtags), required=False)
	):
		body += f"\n\n[ Submitted by {str(ctx.author)} via /issue ]"
		labels = [i for i in [label1, label2] if i]
		if len(labels) > 0:
			issue = self.client.botrepo.create_issue(title=title, body=body, labels=labels)
		else:
			issue = self.client.botrepo.create_issue(title=title, body=body)
		await ctx.respond(f"Submitted!\n\nhttps://github.com/{self.client.botreponame}/issues/{issue.number}")

	# ROLES #

	rolegroup = SlashCommandGroup("role", "Role commands.")

	@rolegroup.command(name="add", description="Add a role to you or someone. Can only add [r] roles to yourself without manage_roles.")
	async def roleadd(self, ctx, 
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
	async def roleremove(self, ctx, 
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
	async def guildconfig(self, ctx,
		action:Option(str, "Config action.", choices=["List","Set","Reset","Info"], required=True),
		name:Option(str, "Variable you're performing action on.", autocomplete=basic_autocomplete(auto_CONvaluenames), required=False),
		value:Option(str, "New value for this Variable.", required=False),
	):
		if await command_checks(ctx, self.client, is_guild=True, has_permission="kick_members"): return
		await self.newconfig_command(ctx, self.client.CON, ctx.guild, action, name, value)

	@configgroup.command(name="user", description="User configerations.")
	async def userconfig(self, ctx,
		action:Option(str, "Config action.", choices=["List","Set","Reset","Info"], required=True),
		name:Option(str, "Variable you're performing action on. Required for all but 'List'.", autocomplete=basic_autocomplete(auto_UCONvaluenames), required=False),
		value:Option(str, "New value for this Variable. Required for 'Set'.", required=False)
	):
		await self.newconfig_command(ctx, self.client.UCON, ctx.author, action, name, value)
	
	async def newconfig_command(self, ctx, CON, obj, action="List", name=None, value=None):
		values = CON.get_group(obj)
		embed = False
		if action == "List":
			txt = ""
			for name in values:
				if not CON.is_restricted(name):
					txt += f"\n**- {name}:** {CON.display_value(name, CON.get_value(obj, name, ctx.guild))}"
			embed = getComEmbed(ctx, self.client, f"All values for {obj.name}:", txt)
		elif action == "Info" and name:
			txt = f"**Value:** {CON.display_value(name, values[name])}\n**Default Value:** `{CON.default_values[name]}`\n**Description:** '{CON.desc_values[name]}'\n**Type:** `{CON.type_values[name]}`\n**Stackable:** `{CON.stackable_values[name]}`"
			embed = getComEmbed(ctx, self.client, f"Info for {name}:", txt)
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
