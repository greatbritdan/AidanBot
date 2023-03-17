import discord
import discord.ext.commands as CM
import discord.app_commands as AC
from discord import Interaction as Itr
from discord.utils import format_dt

import datetime

from aidanbot import AidanBot
from utils.functions import dateToStr, getComEmbed
from utils.checks import ab_check

class InfoCog(CM.Cog):
	def __init__(self, client:AidanBot):
		self.client = client
		self.specalstatus = {
			"384439774972215296": "Bot Owner 💻",
			"788492102568902656": "Our Lord And Saviour 🙏",
			"804319602292949013": "An Authentic AidanBot <:AidanBotBruh:861643332241457162>",
			"861571290132643850": "An Authentic AidanBot <:AidanBotBruh:861643332241457162>",
			"939228285106286702": "An Authentic AidanBot <:AidanBotBruh:861643332241457162>",
			"836936601824788520": "Offical Support Server 🎫"
		}

		self.uinfo = AC.ContextMenu(name="Info", callback=self.userinfo)
		self.client.tree.add_command(self.uinfo, guilds=self.client.debug_guilds)

	async def cog_unload(self):
		self.client.tree.remove_command(self.uinfo.name, type=self.uinfo.type)
		
	async def appuserinfo(self, itr:Itr, user:discord.Member|discord.User):
		await self.userinfo(itr, user)

	@AC.command(name="userinfo", description="Get info on a user in the server.")
	@AC.describe(user="User to get info on, you can use an id for users not in server.")
	async def slashuserinfo(self, itr:Itr, user:discord.Member|discord.User):
		await self.userinfo(itr, user)

	async def userinfo(self, itr:Itr, user:discord.Member|discord.User):	
		user = user or itr.user
		inguild = True
		if isinstance(user, discord.User):
			inguild = False

		today = datetime.datetime.now()

		title = f"Info on {str(user)}"
		if inguild and user.nick: title += f" ({user.nick})"

		desc = ""
		if not inguild:
			desc += "**[ This User isn't in the server so details are minimal ]**\n"
		if str(user.id) in self.specalstatus:
			desc += f"**[ {self.specalstatus[str(user.id)]} ]**\n"
		if itr.guild.owner_id == user.id:
			desc += f"**[ Server Owner 👑 ]**\n"
		if inguild and user.premium_since:
			desc += f"**[ Server Booster 💎 ]**\n"
		if user.bot:
			desc += f"**[ Bot Gang 🤖 ]**\n\n"
		else:
			if len(user.mutual_guilds) == 1:
				desc += f"**[ Being watched by 1 {self.client.name} ]**\n\n"
			else:
				desc += f"**[ Being watched by {len(user.mutual_guilds)} {self.client.name}'s ]**\n\n"
		
		desc += f"**Id:** {user.id}\n"
		if inguild:
			borth = self.client.UCON.get_value(user, 'birthday')
			if borth:
				day, month = borth.split("-")
				desc += f"**Birthday:** {dateToStr(int(day), int(month))}\n"
		createddays = today - user.created_at.replace(tzinfo=None)
		desc += f"**Created:** {format_dt(user.created_at, 'F')} ({createddays.days} Days)\n"
		if inguild:
			joindays = today - user.joined_at.replace(tzinfo=None)
			desc += f"**Joined:** {format_dt(user.joined_at, 'F')} ({joindays.days} Days)\n"
		if inguild and user.premium_since:
			boostdays = today - user.premium_since.replace(tzinfo=None)
			desc += f"**Boosted:** {format_dt(user.premium_since, 'F')} ({boostdays.days} Days)\n"
		if inguild and user.timed_out_until and itr.channel.permissions_for(itr.user).moderate_members:
			desc += f"**Timed-out until:** {format_dt(user.timed_out_until, 'F')}\n"
			
		desc += f"**Url's:**"
		first = True
		if user.avatar:
			if not first: desc += " |"
			first = False
			desc += f" [Avatar]({user.avatar.url})"
		if user.default_avatar:
			if not first: desc += " |"
			first = False
			desc += f" [Default Avatar]({user.default_avatar})"
		if inguild and user.guild_avatar:
			if not first: desc += " |"
			first = False
			desc += f" [Guild Avatar]({user.guild_avatar})"
		ruser = await self.client.fetch_user(user.id)
		if ruser.banner:
			if not first: desc += " |"
			first = False
			desc += f" [Banner]({ruser.banner.url})"
			
		color = discord.Color.from_rgb(20, 29, 37)
		if user.colour.value:
			color = user.colour

		await itr.response.defer()
		fields = False
		if inguild:
			roletxt = "No roles"
			if len(user.roles) > 1:
				roletxt = ""
				for role in reversed(user.roles):
					if not role.is_default():
						roletxt += role.mention + " "

			lastmsgtxt = None
			async for message in itr.channel.history(limit=2000):
				if message.author == user:
					lastmsgtxt = message
					break
			if lastmsgtxt is None:
				lastmsgtxt = "This user hasn't talked in a while..."
			elif lastmsgtxt.clean_content == "":
				lastmsgtxt = f"[Jump to message]({lastmsgtxt.jump_url})"
			else:
				lastmsgtxt = "'" + lastmsgtxt.clean_content + f"' [Jump to message]({lastmsgtxt.jump_url})"

			fields = [["Roles:", roletxt], ["Latest Message:", lastmsgtxt]]

		embed = getComEmbed(str(itr.user), self.client, title, desc, color, fields=fields)
		if user.avatar:
			embed.set_thumbnail(url=user.avatar)
		elif user.default_avatar:
			embed.set_thumbnail(url=user.default_avatar)
		if ruser.banner:
			embed.set_image(url=ruser.banner.url)
		await itr.edit_original_response(embed=embed)

	@AC.command(name="guildinfo", description="Get info on the server/guild.")
	async def slashguildinfo(self, itr:Itr):
		if not await ab_check(itr, self.client, is_guild=True):
			return
		await self.guildinfo(itr)

	async def guildinfo(self, itr:Itr):	
		guild = itr.guild
		today = datetime.datetime.now()

		title = f"Info on {guild.name}"

		desc = ""
		if guild.owner.id == 384439774972215296:
			desc += f"**[ Owned by Aidan <:AidanPog:839509169743593494> ]**\n"
		if str(guild.id) in self.specalstatus:
			desc += f"**[ {self.specalstatus[str(guild.id)]} ]**\n"

		desc += f"\n**Id:** {guild.id}\n"
		createddays = today - guild.created_at.replace(tzinfo=None)
		desc += f"**Created:** {format_dt(guild.created_at, 'F')} ({createddays.days} Days)\n"

		desc += f"**Url's:**"
		first = True
		if guild.icon:
			if not first: desc += " |"
			first = False
			desc += f" [Icon]({guild.icon.url})"
		if guild.splash:
			if not first: desc += " |"
			first = False
			desc += f" [Invite Image]({guild.splash.url})"

		usertxt = f"**Full Member count:** {guild.member_count}\n"
		bots = len([member for member in guild.members if member.bot])
		if bots > 0:
			usertxt += f"**Non-bot count:** {guild.member_count-bots}\n"
			usertxt += f"**Bot count:** {bots}\n"

		boosttxt = ""
		if guild.premium_tier > 0:
			boosttxt += f"**Boost level:** {guild.premium_tier}\n"
			boosttxt += f"**Number of boosts:** {guild.premium_subscription_count}\n"
			boosttxt += f"**Number of boosters:** {len(guild.premium_subscribers)}\n"
			mentions = [user.mention for user in guild.premium_subscribers]
			boosttxt += f"**Boosters:** {', '.join(mentions)}\n"

		channeltxt = ""
		if len(guild.channels) > 0:
			channeltxt = f"**Total channels:** {len(guild.channels)}\n"
			if len(guild.text_channels) > 0:
				channeltxt += f"**Text channels:** {len(guild.text_channels)}\n"
			if len(guild.forums) > 0:
				channeltxt += f"**Forum channels:** {len(guild.forums)}\n"	
			if len(guild.voice_channels) > 0:
				channeltxt += f"**Voice channels:** {len(guild.voice_channels)}\n"	
			if len(guild.stage_channels) > 0:
				channeltxt += f"**Stage channels:** {len(guild.stage_channels)}\n"

		roletxt = f"**Role count:** {len(guild.roles)}\n"
		if len(guild.roles) > 1:
			for role in reversed(guild.roles):
				if not role.is_default():
					roletxt += role.mention + " "
		
		fields = []
		fields.append(["Users",usertxt])
		if boosttxt != "":
			fields.append(["Boosting",boosttxt])
		if channeltxt != "":
			fields.append(["Channels",channeltxt])
		fields.append(["Roles",roletxt])

		embed = getComEmbed(str(itr.user), self.client, title, desc, fields=fields)
		if guild.icon:
			embed.set_thumbnail(url=guild.icon)
		if guild.splash:
			embed.set_image(url=guild.splash.url)
		await itr.response.send_message(embed=embed)

async def setup(client:AidanBot):
	await client.add_cog(InfoCog(client), guilds=client.debug_guilds)