import discord
import discord.ext.commands as CM
import discord.app_commands as AC
from discord import Interaction as Itr
from discord.ext import tasks

import datetime, asyncio

from aidanbot import AidanBot
from functions import getComEmbed, dateToStr
from checks import ab_check_slient
from cooldowns import cooldown_etc

class BirthdayCog(CM.Cog):
	def __init__(self, client:AidanBot):
		self.client = client

	async def ready(self):
		self.borths = await self.getBirthdays()
		self.daily_task.start()

	def cog_unload(self):
		self.daily_task.cancel()
	
	async def getBirthdays(self):
		borths = []
		now = "{dt.day}-{dt.month}".format(dt=datetime.datetime.now())
		for user in await self.client.UCON.loopdata():
			when = self.client.UCON.get_value(user, "birthday")
			if now == when:
				borths.append(user)
		return borths

	async def getUpcomingBirthdays(self, itr:Itr):
		birthlist = []
		for user in await self.client.UCON.loopdata():
			if user in itr.guild.members:
				when = self.client.UCON.get_value(user, "birthday")
				if when:
					day, month = when.split("-")
					birthlist.append([user,int(day),int(month)])
		if len(birthlist) == 0:
			return await itr.response.send_message(f"No one in this server has set a birthday. You can change that by running /birthday set!")

		def sortfunc(e):
			return e[1]+(e[2]*31)
		birthlist.sort(key=sortfunc)

		today = str(datetime.date.today()).split("-")
		today = [int(e) for e in today]
		for i in range(1,len(birthlist)): # thanks for wasting my sweet time.
			# if birth month is higher than todays month or month is same and birth day is higher than todays day
			if birthlist[0][2] > today[1] or (birthlist[0][2] == today[1] and birthlist[0][1] > today[2]):
				break
			else:
				birthlist.append(birthlist.pop(0))

		return birthlist

	async def nextDay(self):
		if self.client.isbeta:
			return
			
		for user in self.borths: # no longer birthday :(
			for guild in self.client.guilds:
				if user in guild.members:
					if await ab_check_slient(None, self.client, guild=guild, user=user, is_guild=True, bot_has_permission="manage_roles"):
						member = guild.get_member(user.id)

						role = self.client.CON.get_value(guild, "birthday_role", guild=guild)
						if role and role in member.roles:
							await member.remove_roles(role)

		self.borths = await self.getBirthdays()
		for user in self.borths: # is birthday :)
			for guild in self.client.guilds:
				if user in guild.members:
					member = guild.get_member(user.id)

					channel = self.client.CON.get_value(guild, "birthday_announcement_channel", guild=guild)
					msg = self.client.CON.get_value(guild, "birthday_announcement_message")
					if channel and msg:
						await channel.send(msg.format(name=user.name, mention=user.mention, user=user, member=user))
					
					if await ab_check_slient(None, self.client, guild=guild, user=user, is_guild=True, bot_has_permission="manage_roles"):
						role = self.client.CON.get_value(guild, "birthday_role", guild=guild)
						if role:
							await member.add_roles(role)

	@tasks.loop(time=datetime.time(0, 0, 0, 0, datetime.datetime.now().astimezone().tzinfo))
	async def daily_task(self):
		await self.nextDay()

	###

	borthgroup = AC.Group(name="birthday", description="Birthday Of The Day commands.")

	@borthgroup.command(name="change", description="Set or remove your birthday. To remove leave day and month arguments blank")
	@AC.describe(day="Day of your birthday.", month="Month of your birthday.")
	@CM.dynamic_cooldown(cooldown_etc, CM.BucketType.user)
	async def change(self, itr:Itr, day:AC.Range[int,1,31], month:AC.Range[int,1,12]):
		if (not day) and (not month):
			await self.client.UCON.set_value(itr.user, "birthday", False)
			await itr.response.send_message("Remeoved your birthday from the database.")
		if (not (day and month)):
			await itr.response.send_message("Command requires both or neither argument.")
		else:
			if day >= 1 and (((month == 1 or month == 3 or month == 5 or month == 7 or month == 9 or month == 11) and day <= 31) or ((month == 4 or month == 6 or month == 8 or month == 10 or month == 12) and day <= 30) or (month == 2 and day <= 29)):
				await self.client.UCON.set_value(itr.user, "birthday", f"{day}-{month}")
				await itr.response.send_message(f"Birthday set to the {dateToStr(day, month)}")
			else:
				await itr.response.send_message(f"Nice try but the {dateToStr(day, month)} isn't real, Enter a valid date please.")

	@borthgroup.command(name="upcoming", description="Upcoming birthdays.")
	@CM.dynamic_cooldown(cooldown_etc, CM.BucketType.user)
	async def upcoming(self, itr:Itr):	
		await itr.response.defer()
		birthlist = await self.getUpcomingBirthdays(itr)

		def getbirthdaylistembed(birthdays, first):
			fields = []
			for birth in birthdays:
				txt = dateToStr(birth[1], birth[2])
				fields.append([f"{birth[0]}:", txt])
			content = "Other Birthdays:"
			if first:
				content = "🎊🎊🎊 Upcoming Birthdays:"
			return getComEmbed(str(itr.user), self.client, content, "Is your birthday coming soon? Use /birthday set to add yours!", fields=fields)

		page = 0
		pages = []
		first = True
		questionchunks = divide_chunks(birthlist, 5)
		for qc in questionchunks:
			pages.append(getbirthdaylistembed(qc, first))
			if first: first = False

		def getView(timeout=False):
			view = discord.ui.View(timeout=None)
			view.add_item(discord.ui.Button(label="<-", style=discord.ButtonStyle.blurple, custom_id="left", disabled=timeout))
			view.add_item(discord.ui.Button(label=f"{page+1}/{len(pages)}", style=discord.ButtonStyle.gray, custom_id="display", disabled=True))
			view.add_item(discord.ui.Button(label="->", style=discord.ButtonStyle.blurple, custom_id="right", disabled=timeout))
			return view
		
		await itr.edit_original_response(embed=pages[page], view=getView())
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

def divide_chunks(l, n):
	for i in range(0, len(l), n):
		yield l[i:i + n]

async def setup(client:AidanBot):
	await client.add_cog(BirthdayCog(client), guilds=client.debug_guilds)