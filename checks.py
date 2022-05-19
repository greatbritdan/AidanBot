import discord
from discord.utils import get
from functions import getErrorEmbed

def permission_check(ctx, member, permission):
	for perm in ctx.channel.permissions_for(member):
		if str(perm[0]) == permission and perm[1] == True:
			return True
	return False

#chenk
async def command_checks(ctx, client, is_guild=None, is_owner=None, has_value=None, has_permission=None, bot_has_permission=None):
	if is_guild and isinstance(ctx.channel, discord.channel.DMChannel):
		await ctx.respond(embed=getErrorEmbed(ctx, client, "This command is limited to servers only!"))
		return True
	if is_owner and (not await client.is_owner(ctx.author)):
		await ctx.respond(embed=getErrorEmbed(ctx, client, "This command is limited to Aidan only!"))
		return True
	if has_value and (not client.CON.get_value(ctx.guild, has_value, ctx.guild)):
		await ctx.respond(embed=getErrorEmbed(ctx, client, f"The value '{has_value}' is not set up on this server!"))
		return True
	if has_permission and (not permission_check(ctx, ctx.author, has_permission)):
		await ctx.respond(embed=getErrorEmbed(ctx, client, f"You are missing '{has_permission}' permissions!"))
		return True
	clientmember = get(ctx.guild.members, id=client.user.id)
	if bot_has_permission and (not permission_check(ctx, clientmember, bot_has_permission)):
		await ctx.respond(embed=getErrorEmbed(ctx, client, f"I am missing '{bot_has_permission}' permissions!"))
		return True
	return False