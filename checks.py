import discord
from discord.ext import commands
from discord.utils import get
from functions import getCheckErrorEmbed

def permission_check(member:discord.Member, channel:discord.TextChannel, permission):
	try:
		perms = channel.permissions_for(member)
	except:
		perms = member.guild_permissions
	for perm in perms:
		if str(perm[0]) == permission and perm[1] == True:
			return True
	return False

#chenk
async def command_checks(
	ctx:discord.ApplicationContext, client:commands.Bot, user:discord.Member=None, guild:discord.Guild=None, channel:discord.TextChannel=None,
	is_guild=None, is_owner=None, has_value=None, has_permission=None, bot_has_permission=None, has_mod_role=None, ephemeral=False
):
	user = user or ctx.author
	guild = guild or ctx.guild
	if channel or ctx:
		channel = channel or ctx.channel

	if is_guild and (not guild):
		await ctx.respond(embed=getCheckErrorEmbed(ctx, client, "This command is limited to servers only!"), ephemeral=ephemeral)
		return True
	if is_owner and (not await client.is_owner(user)):
		await ctx.respond(embed=getCheckErrorEmbed(ctx, client, "This command is limited to Aidan only!"), ephemeral=ephemeral)
		return True
	if is_guild: # these work only in guilds
		if has_value and (not client.CON.get_value(guild, has_value, guild)):
			await ctx.respond(embed=getCheckErrorEmbed(ctx, client, f"The value '{has_value}' is not set up on this server!"), ephemeral=ephemeral)
			return True
		if has_permission:
			if not permission_check(user, channel, has_permission):
				await ctx.respond(embed=getCheckErrorEmbed(ctx, client, f"You are missing '{has_permission}' permissions!"), ephemeral=ephemeral)
				return True
		if bot_has_permission:
			clientmember = get(guild.members, id=client.user.id)
			if not permission_check(clientmember, channel, bot_has_permission):
				await ctx.respond(embed=getCheckErrorEmbed(ctx, client, f"I am missing '{bot_has_permission}' permissions!"), ephemeral=ephemeral)
				return True
		if has_mod_role:
			roles = client.CON.get_value(guild, "mod_role", guild)
			if roles:
				gud = False
				for role in roles:
					if role in user.roles:
						gud = True
				if not gud:
					await ctx.respond(embed=getCheckErrorEmbed(ctx, client, f"This command is limited to moderators only!"), ephemeral=ephemeral)
					return True
			else:
				if not permission_check(user, channel, "kick_members"):
					await ctx.respond(embed=getCheckErrorEmbed(ctx, client, f"This command is limited to moderators only!"), ephemeral=ephemeral)
					return True
	return False

async def command_checks_silent(
	ctx:discord.ApplicationContext, client:commands.Bot, user:discord.Member=None, guild:discord.Guild=None, channel:discord.TextChannel=None,
	is_guild=None, is_owner=None, has_value=None, has_permission=None, bot_has_permission=None, has_mod_role=None, ephemeral=False
):
	user = user or ctx.author
	guild = guild or ctx.guild
	if channel or ctx:
		channel = channel or ctx.channel

	if is_guild and (not guild):
		return True
	if is_owner and (not await client.is_owner(user)):
		return True
	if is_guild: # these work only in guilds
		if has_value and (not client.CON.get_value(guild, has_value, guild)):
			return True
		if has_permission:
			if not permission_check(user, channel, has_permission):
				return True
		if bot_has_permission:
			clientmember = get(guild.members, id=client.user.id)
			if not permission_check(clientmember, channel, bot_has_permission):
				return True
		if has_mod_role:
			roles = client.CON.get_value(guild, "mod_role", guild)
			if roles:
				gud = False
				for role in roles:
					if role in user.roles:
						gud = True
				if not gud:
					return True
			else:
				if not permission_check(user, channel, "kick_members"):
					return True
	return False