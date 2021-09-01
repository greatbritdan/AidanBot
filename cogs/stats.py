import discord
from discord.ext import commands

from functions import getEmbed, addField

class StatsCog(commands.Cog):
	def __init__(self, client):
		self.client = client

	@commands.command(description="Get info about a user.")
	async def user(self, ctx, user:discord.Member=None):
		if user == None:
			user = ctx.author
		
		epochc = round(user.created_at.timestamp())
		epochj = round(user.joined_at.timestamp())
		epochb = False

		toptxt = f"{user.name}#{user.discriminator}"
		if ctx.guild.owner_id == user.id:
			toptxt += " (Guild Owner)"
		if user.premium_since:
			toptxt += " (Epic booster)"
			epochb = round(user.premium_since.timestamp())

		txt = ""
		txt += f"`Name`: {user.name}\n"
		txt += f"`ID`: {user.id}\n"
		if user.nick:
			txt += f"`Nickname`: {user.nick}\n"
		if user.bot:
			txt += f"`Bot`: True\n"
		txt += f"`Created at`: <t:{epochc}:D>\n"
		txt += f"`Joined Guild on`: <t:{epochj}:D>\n"
		if epochb:
			txt += f"`Booster since`: <t:{epochb}:D>"

		roltxt = ""
		for role in reversed(user.roles):
			roltxt += role.mention + " "

		permtxt = ""
		for perm in user.guild_permissions:
			if perm[1] == True:
				permtxt += perm[0] + ", "

		emb = getEmbed(ctx, "user", toptxt, "", user.color, user.avatar_url)
		emb = addField(emb, "General:", txt)
		emb = addField(emb, "Roles:", roltxt)
		emb = addField(emb, "Permissions:", permtxt[0:-2])
		await ctx.send(embed=emb)

	@commands.command(description="Get info about a guild.")
	async def guild(self, ctx):
		guild = ctx.guild

		epochc = round(guild.created_at.timestamp())

		txt = ""
		txt += f"`Members`: {guild.member_count}\n"
		txt += f"`Members (No bots)`: {len([m for m in guild.members if not m.bot])}\n"
		txt += f"`Members (Just bots)`: {len([m for m in guild.members if m.bot])}\n"
		txt += f"`ID`: {guild.id}\n"
		txt += f"`Owner`: {guild.owner.mention}\n"
		txt += f"`Roles`: {len(guild.roles)}\n"
		txt += f"`Boosts`: {guild.premium_subscription_count} (Level {guild.premium_tier})\n"
		txt += f"`Created at`: <t:{epochc}:D>\n"

		ac = 0
		for chan in guild.text_channels:
			if chan.is_news():
				ac += 1

		chantxt = ""
		chantxt += f"- **{len(guild.categories)}** Categories.\n"
		chantxt += f"- **{len(guild.text_channels)}** Text Channels.\n"
		if ac > 0:
			chantxt += f"- **{ac}** Announcement Channels.\n"
		chantxt += f"- **{len(guild.voice_channels)}** Voice Channels.\n"
		chantxt += f"- **{len(guild.stage_channels)}** Stage Channels.\n"
		if guild.rules_channel:
			chantxt += f"- Rule Channel: {guild.rules_channel.mention}\n"

		emb = getEmbed(ctx, "user", f"{guild.name}", "", None, guild.icon_url)
		emb = addField(emb, "General:", txt)
		emb = addField(emb, "Channels:", chantxt)
		await ctx.send(embed=emb)

def setup(client):
  client.add_cog(StatsCog(client))