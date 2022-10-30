import discord
import discord.ext.commands as CM
import discord.app_commands as AC
from discord import Interaction as Itr
from discord.utils import format_dt

from aidanbot import AidanBot
from functions import dateToStr, getComEmbed
from cooldowns import cooldown_etc

class InfoCog(CM.Cog):
	def __init__(self, client:AidanBot):
		self.client = client
		self.specalstatus = {
			"384439774972215296": "Bot Owner 💻",
			"788492102568902656": "Our Lord And Saviour",
			"804319602292949013": "An Authentic AidanBot",
			"861571290132643850": "An Authentic AidanBot",
			"939228285106286702": "An Authentic AidanBot"
		}

		self.uinfo = AC.ContextMenu(name="Info", callback=self.userinfo)
		self.client.tree.add_command(self.uinfo, guilds=self.client.debug_guilds)

	async def cog_unload(self):
		self.client.tree.remove_command(self.uinfo.name, type=self.uinfo.type)
		
	@CM.dynamic_cooldown(cooldown_etc, CM.BucketType.user)
	async def userinfo(self, itr:Itr, user:discord.Member|discord.User):
		await self.info(itr, user)

	@AC.command(name="userinfo", description="Get info on a user in the server.")
	@AC.describe(user="User to get info on, you can use an id for users not in server.")
	@CM.dynamic_cooldown(cooldown_etc, CM.BucketType.user)
	async def slashinfo(self, itr:Itr, user:discord.Member):
		await self.info(itr, user)

	async def info(self, itr:Itr, user:discord.Member|discord.User):	
		user = user or itr.user
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
		if itr.guild.owner_id == user.id:
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

async def setup(client:AidanBot):
	await client.add_cog(InfoCog(client), guilds=client.debug_guilds)