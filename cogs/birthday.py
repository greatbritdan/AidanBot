from discord.ext import commands

import datetime, asyncio

from functions import dateToStr, getComEmbed

class BirthdayCog(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.borths = []

    async def ready(self):
        self.borths = await self.getBirthdays()
        self.client.loop.create_task(self.background_task())

    async def changeDay(self):
        await self.client.wait_until_ready()

        # no longer birthday :(
        for user in self.borths:
            for guild in self.client.guilds:
                if user in guild.members:
                    member = guild.get_member(user.id)

                    role = self.client.CON.get_role(guild, "birthday_role", guild)
                    if role and role in member.roles:
                        await member.remove_roles(role)

        self.borths = await self.getBirthdays()
        # is birthday :)
        for user in self.borths:
            for guild in self.client.guilds:
                if user in guild.members:
                    member = guild.get_member(user.id)

                    channel = self.client.CON.get_channel(guild, "birthday_announcement_channel", guild)
                    msg = self.client.CON.get_value(guild, "birthday_announcement_message")
                    if channel and msg:
                        await channel.send(msg.format(name=user.name, mention=user.mention, user=user, member=user))
                    
                    role = self.client.CON.get_role(guild, "birthday_role", guild)
                    if role:
                        await member.add_roles(role)

    async def getBirthdays(self):
        borths = []
        now = "{dt.day}-{dt.month}".format(dt=datetime.datetime.now())
        for user in await self.client.UCON.loopdata():
            when = self.client.UCON.get_value(user, "birthday")
            if now == when:
                borths.append(user)
        return borths

    # ????????
    async def background_task(self):
        when = datetime.time(0,0,0)
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
            await self.changeDay()
            tomorrow = datetime.datetime.combine(now.date() + datetime.timedelta(days=1), datetime.time(0))
            seconds = (tomorrow - now).total_seconds()
            await asyncio.sleep(seconds)

    @commands.command(aliases=["setbd"])
    @commands.cooldown(1, 3)
    async def setbirthday(self, ctx, day:int=None, month:int=None):
        if day and month:
            if day >= 1 and (((month == 1 or month == 3 or month == 5 or month == 7 or month == 9 or month == 11) and day <= 31) or ((month == 4 or month == 6 or month == 8 or month == 10 or month == 12) and day <= 30) or (month == 2 and day <= 29)):
                suc = self.client.UCON.set_value_force(ctx.author, "birthday", f"{day}-{month}")
                txt = dateToStr(day, month)
                if suc:
                    await ctx.send(f"Birthday set to the {txt}")
                    await self.client.UCON.values_msgupdate("save")
                else:
                    await ctx.send("Seems the value failed to set. Try again later or report the issue if issues persist.")
            else:
                await ctx.send("Enter a valid date pls.")
        elif not day:
            suc = self.client.UCON.set_value_force(ctx.author, "birthday", False)
            if suc:
                await ctx.send("Remeoved your birthday from the database.")
                await self.client.UCON.values_msgupdate("save")
            else:
                await ctx.send("Seems the value failed to set. Try again later or report the issue if issues persist.")
        else:
            await ctx.send("Add a month to add birthday, or pass no day to remove yours (if set).")

    @commands.command(aliases=["upcomingbds","birthdays"])
    @commands.guild_only()
    @commands.cooldown(1, 3)
    async def upcomingbirthdays(self, ctx):
        birthlist = []
        for user in await self.client.UCON.loopdata():
            if user in ctx.guild.members:
                when = self.client.UCON.get_value(user, "birthday")
                if when:
                    day, month = when.split("-")
                    birthlist.append([user,int(day),int(month)])

        def sortfunc(e):
            return e[1]+(e[2]*31)
        birthlist.sort(key=sortfunc)

        notdone = True
        today = str(datetime.date.today()).split("-")
        today = [int(e) for e in today]
        while notdone:
            # if birth month is higher than todays month or month is same and birth day is higher than todays day
            if birthlist[0][2] > today[1] or (birthlist[0][2] == today[1] and birthlist[0][1] > today[2]):
                notdone = False
            else:
                birthlist.append(birthlist.pop(0))
                
        f = []
        for birth in birthlist[0:5]:
            txt = dateToStr(birth[1], birth[2])
            f.append([birth[0].display_name, txt])
        
        emb = getComEmbed(ctx, self.client, "Birthdays", "Upcoming Birthdays 🎊🎊🎊", fields=f)
        await ctx.reply(embed=emb, mention_author=False)

def setup(client):
	client.add_cog(BirthdayCog(client))
