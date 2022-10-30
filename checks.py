import discord
import discord.ext.commands as CM

#from aidanbot import AidanBot
from functions import getCheckEmbed

def permission_check(user:discord.Member, channel:discord.TextChannel, permission):
	try:
		perms = channel.permissions_for(user)
	except Exception:
		perms = user.guild_permissions
	for perm in perms:
		if str(perm[0]) == permission and perm[1] == True:
			return True
	return False

async def _command_checks(client:CM.Bot, user, guild, channel, is_guild, is_owner, has_value, has_permission, bot_has_permission, has_mod_role):
	if is_guild and (not guild):
		return "This command is limited to servers only!"
	if is_owner and (not await client.is_owner(user)):
		return "This command is limited to Aidan only!"
	if is_guild: # these work only in guilds
		if has_value and (not client.CON.get_value(guild, has_value, guild)):
			return f"The value '{has_value}' is not set up on this server!"
		if has_permission:
			if not permission_check(user, channel, has_permission):
				return f"You are missing '{has_permission}' permissions!"
		if bot_has_permission:
			clientmember = await guild.fetch_member(client.user.id)
			if not permission_check(clientmember, channel, bot_has_permission):
				return f"I am missing '{bot_has_permission}' permissions!"
		if has_mod_role:
			roles = client.CON.get_value(guild, "mod_role", guild)
			if roles:
				gud = False
				for role in roles:
					if role in user.roles:
						gud = True
				if not gud:
					return f"This command is limited to moderators only!"
			else:
				if not permission_check(user, channel, "kick_members"):
					return f"This command is limited to moderators only!"
	return False

async def ab_check_slient(itr:discord.Interaction, client:CM.Bot=None, user=None, guild=None, channel=None, is_guild=None, is_owner=None, has_value=None, has_permission=None, bot_has_permission=None, has_mod_role=None):
	user = user or itr.user
	guild = guild or itr.guild
	if channel or itr:
		channel = channel or itr.channel
	result = await _command_checks(client, user, guild, channel, is_guild, is_owner, has_value, has_permission, bot_has_permission, has_mod_role)
	if result:
		return False
	return True

async def ab_check(itr:discord.Interaction, client:CM.Bot=None, user=None, guild=None, channel=None, is_guild=None, is_owner=None, has_value=None, has_permission=None, bot_has_permission=None, has_mod_role=None):
	user = user or itr.user
	guild = guild or itr.guild
	if channel or itr:
		channel = channel or itr.channel
	result = await _command_checks(client, user, guild, channel, is_guild, is_owner, has_value, has_permission, bot_has_permission, has_mod_role)
	if result:
		await itr.response.send_message(embed=getCheckEmbed(str(user), client, result), ephemeral=True)
		return False
	return True