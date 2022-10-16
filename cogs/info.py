import discord
from discord.ext import commands
from discord.commands import slash_command, user_command
from discord.utils import format_dt
from discord import Option

from functions import dateToStr, getComEmbed

AC = discord.ApplicationContext
class UserCog(discord.Cog):
	def __init__(self, client:commands.Bot):
		self.client = client
		self.specalstatus = {
			"384439774972215296": "Bot Owner 💻",
			"788492102568902656": "Our Lord And Saviour",
			"804319602292949013": "An Authentic AidanBot",
			"861571290132643850": "An Authentic AidanBot",
			"939228285106286702": "An Authentic AidanBot"
		}

	@user_command(name="Info")
	async def uinfo(self, ctx:AC, user:discord.Member|discord.User):
		await self.info(ctx, user)

	@slash_command(name="userinfo")
	async def sinfo(self, ctx:AC, user:Option(discord.Member, "User to get info on, you can use an id for users not in server.")):
		await self.info(ctx, user)

	async def info(self, ctx:AC, user:discord.Member|discord.User):	
		user = user or ctx.author
		inguild = True
		if isinstance(user, discord.User):
			inguild = False

		title = f"Info on {str(user)}"
		if inguild and user.nick: title += f" ({user.nick})"

		desc = ""
		if not inguild:
			desc += "**[ This User isn't in the server so details are minimal ]**\n"
		if str(user.id) in self.specalstatus:
			desc += f"**[ {self.specalstatus[str(user.id)]} ]**\n"
		if ctx.guild.owner_id == user.id:
			desc += f"**[ Server Owner 👑 ]**\n"
		if inguild and user.premium_since:
			desc += f"**[ Server Booster 💎 ]**\n"
		if user.bot:
			desc += f"**[ Bot Gang 🤖 ]**\n"
		if len(user.mutual_guilds) == 1:
			watch = f"**[ Being watched by 1 {self.client.name} ]**\n\n"
		else:
			watch = f"**[ Being watched by {len(user.mutual_guilds)} {self.client.name}'s ]**\n\n"
		desc += watch
		
		desc += f"**Id:** {user.id}\n"
		if inguild:
			borth = self.client.UCON.get_value(user, 'birthday')
			if borth:
				day, month = borth.split("-")
				desc += f"**Birthday:** {dateToStr(int(day), int(month))}\n"
		desc += f"**Created:** {format_dt(user.created_at, 'F')}\n"
		if inguild:
			desc += f"**Joined:** {format_dt(user.joined_at, 'F')}\n"
		if inguild and user.premium_since:
			desc += f"**Boosted:** {format_dt(user.premium_since, 'F')}\n"
		if inguild and user.communication_disabled_until and ctx.channel.permissions_for(ctx.author).moderate_members:
			desc += f"**Timed-out until:** {format_dt(user.communication_disabled_until, 'F')}\n"
			
		desc += f"**Url's:**"
		if user.avatar:
			desc += f" [Avatar]({user.avatar.url})"
		if user.default_avatar:	
			desc += f" [Default Avatar]({user.default_avatar})"
		ruser = await self.client.fetch_user(user.id)
		if ruser.banner:
			desc += f" [Banner]({ruser.banner.url})"
			
		color = discord.Color.from_rgb(20, 29, 37)
		if user.colour.value:
			color = user.colour

		await ctx.interaction.response.defer()

		fields = False
		if inguild:
			roletxt = "No roles"
			if len(user.roles) > 1:
				roletxt = ""
				for role in reversed(user.roles):
					if not role.is_default():
						roletxt += role.mention + " "

			lastmsgtxt = await ctx.channel.history(limit=500).find(lambda m: m.author.id == user.id)
			if lastmsgtxt is None:
				lastmsgtxt = "This user hasn't talked in a while..."
			else:
				lastmsgtxt = "'" + lastmsgtxt.clean_content + f"' [Jump to message]({lastmsgtxt.jump_url})"

			fields = [["Roles:", roletxt], ["Latest Message:", lastmsgtxt]]

		embed = getComEmbed(ctx, self.client, title, desc, color, fields=fields)
		if user.avatar:
			embed.set_thumbnail(url=user.avatar)
		elif user.default_avatar:
			embed.set_thumbnail(url=user.default_avatar)
		await ctx.respond(embed=embed)

def setup(client):
	client.add_cog(UserCog(client))
