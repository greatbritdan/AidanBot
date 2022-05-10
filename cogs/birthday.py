from discord import Option
from discord.ext import commands
from discord.commands import SlashCommandGroup

import asyncio, datetime
from functions import getComEmbed, dateToStr

class BirthdayCog(commands.Cog):
	def __init__(self, client):
		self.client = client

	async def ready(self):
		self.borths = await self.getBirthdays()
		self.client.loop.create_task(self.background_task())
	
	async def getBirthdays(self):
		borths = []
		now = "{dt.day}-{dt.month}".format(dt=datetime.datetime.now())
		for user in await self.client.UCON.loopdata():
			when = self.client.UCON.get_value(user, "birthday")
			if now == when:
				borths.append(user)
		return borths

	async def nextDay(self):
		if self.client.isbeta:
			return

		for user in self.borths: # no longer birthday :(
			for guild in self.client.guilds:
				if user in guild.members:
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
					
					role = self.client.CON.get_value(guild, "birthday_role", guild=guild)
					if role:
						await member.add_roles(role)

	async def background_task(self):
		when = datetime.time(1,0,0)
		now = datetime.datetime.utcnow()
		if now.time() > when:
			tomorrow = datetime.datetime.combine(now.date() + datetime.timedelta(days=1), datetime.time(0))
			seconds = (tomorrow - now).total_seconds()
			await asyncio.sleep(seconds)
		while True:
			now = datetime.datetime.utcnow()
			target_time = datetime.datetime.combine(now.date(), when)
			seconds_until_target = (target_time - now).total_seconds()
			await asyncio.sleep(seconds_until_target)
			await self.nextDay()
			tomorrow = datetime.datetime.combine(now.date() + datetime.timedelta(days=1), datetime.time(0))
			seconds = (tomorrow - now).total_seconds()
			await asyncio.sleep(seconds)

	borthgroup = SlashCommandGroup("birthday", "Birthday commands.")

	@borthgroup.command(name="set", description="Set your birthday.")
	async def set(self, ctx,
		day:Option(int, "Day of your birthday", min_value=1, max_value=31, required=True),
		month:Option(int, "Month of your birthday", min_value=1, max_value=12, required=True)
	):
		if day >= 1 and (((month == 1 or month == 3 or month == 5 or month == 7 or month == 9 or month == 11) and day <= 31) or ((month == 4 or month == 6 or month == 8 or month == 10 or month == 12) and day <= 30) or (month == 2 and day <= 29)):
			await self.client.UCON.set_value(ctx.author, "birthday", f"{day}-{month}")
			await ctx.respond(f"Birthday set to the {dateToStr(day, month)}")
		else:
			await ctx.respond(f"Nice try but the {dateToStr(day, month)} isn't real, Enter a valid date please.")

	@borthgroup.command(name="remove", description="Remove your birthday.")
	async def remove(self, ctx):
		await self.client.UCON.set_value(ctx.author, "birthday", False)
		await ctx.respond("Remeoved your birthday from the database.")

	@borthgroup.command(name="upcoming", description="Upcoming birthdays.")
	async def upcoming(self, ctx):
		birthlist = []
		for user in await self.client.UCON.loopdata():
			if user in ctx.guild.members:
				when = self.client.UCON.get_value(user, "birthday")
				if when:
					day, month = when.split("-")
					birthlist.append([user,int(day),int(month)])
		if len(birthlist) == 0:
			return await ctx.respond(f"No one in this server has set a birthday. You can change that by running /birthday set!")

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
				
		f = []
		for birth in birthlist[0:5]:
			txt = dateToStr(birth[1], birth[2])
			f.append([birth[0].display_name, txt])
		
		embed = getComEmbed(ctx, self.client, "Birthdays", "Upcoming Birthdays 🎊🎊🎊", fields=f)
		await ctx.respond(embed=embed)

def setup(client):
	client.add_cog(BirthdayCog(client))