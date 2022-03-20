import discord
from discord.ext import commands

import datetime, asyncio
from random import randint

from functions import getComEmbed

class QOTDCog(commands.Cog):
    def __init__(self, client):
        self.client = client

    async def ready(self):
        self.client.loop.create_task(self.background_task())

    @commands.command()
    @commands.is_owner()
    async def forceqotd(self, ctx):
        await self.changeDay()

    async def changeDay(self):
        await self.client.wait_until_ready()
        
        for guild in await self.client.CON.loopdata():
            channel = self.client.CON.get_channel(guild, "qotd_channel", guild)
            if channel:
                questions = self.client.CON.get_value(guild, "questions")
                if len(questions) == 0:
                    emb = getComEmbed(None, self.client, "Question Of The Day", f"Looks like we're out of questions, use {self.client.getprefixguild(guild)}qotdadd to add more!", "", discord.Color.from_rgb(145, 29, 37))
                    await channel.send(embed=emb)
                else:
                    questioni = randint(0, len(questions)-1)
                    question = questions[questioni]
                    questions.pop(questioni)
                    if not question.endswith("?"):
                        question += "?"
                    emb = getComEmbed(None, self.client, "Question Of The Day", question)
                    await channel.send(embed=emb)

                    self.client.CON.set_value_force(guild, "questions", questions)
                    await self.client.CON.values_msgupdate("save")

    # ????????
    async def background_task(self):
        when = datetime.time(15,0,0)
        now = datetime.datetime.utcnow()
        if now.time() > when:
            tomorrow = datetime.datetime.combine(now.date() + datetime.timedelta(days=1), datetime.time(0))
            seconds = (tomorrow - now).total_seconds()
            await asyncio.sleep(seconds)
        while True:
            target_time = datetime.datetime.combine(now.date(), when)
            seconds_until_target = (target_time - now).total_seconds()
            await asyncio.sleep(seconds_until_target)
            await self.changeDay()
            tomorrow = datetime.datetime.combine(now.date() + datetime.timedelta(days=1), datetime.time(0))
            seconds = (tomorrow - now).total_seconds()
            await asyncio.sleep(seconds)

    @commands.command()
    @commands.cooldown(1, 5)
    async def qotdadd(self, ctx, *, question):
        channel = self.client.CON.get_channel(ctx.guild, "qotd_channel", ctx.guild)
        if channel:
            questions = self.client.CON.get_value(ctx.guild, "questions")
            questions.append(question)
            self.client.CON.set_value_force(ctx.guild, "questions", questions)
            await self.client.CON.values_msgupdate("save")
            await ctx.send("Question added to qotd!")
        else:
            await ctx.send("This server doesn't have QOTD set up, consider asking an Admin as there may be another bot in charge of qotd!")

    @commands.command()
    @commands.cooldown(1, 3)
    async def qotdlist(self, ctx):
        channel = self.client.CON.get_channel(ctx.guild, "qotd_channel", ctx.guild)
        if channel:
            questions = self.client.CON.get_value(ctx.guild, "questions")
            if len(questions) > 0:
                txt = "\n- " + "\n- ".join(questions) + "\n"
                await ctx.send(f"**All questions:**```{txt}```")
            else:
                await ctx.send(f"Looks like we're out of questions, use {self.client.getprefixguild(ctx.guild)}qotdadd to add more!")
        else:
            await ctx.send("This server doesn't have QOTD set up, consider asking an Admin as there may be another bot in charge of qotd!")

def setup(client):
    client.add_cog(QOTDCog(client))