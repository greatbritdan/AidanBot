import discord
from discord.ext import commands
from discord.utils import get

import datetime, asyncio
from random import randint

from functions import getComEmbed

class QOTDCog(commands.Cog):
    def __init__(self, client):
        self.client = client

    async def ready(self):
        self.client.loop.create_task(self.background_task())

    async def changeDay(self):
        await self.client.wait_until_ready()
        
        for guild in await self.client.CON.loopdata():
            channel = self.client.CON.get_value(guild, "qotd_channel", guild=guild)
            if channel:
                questions = self.client.CON.get_value(guild, "questions")
                if len(questions) == 0:
                    emb = getComEmbed(None, self.client, "Question Of The Day", f"Looks like we're out of questions, use {self.client.getprefixguild(guild)}qotdadd to add more!", "", discord.Color.from_rgb(145, 29, 37))
                    await channel.send(embed=emb)
                else:
                    questioni = randint(0, len(questions)-1)
                    question = questions[questioni]
                    questions.pop(questioni)

                    quest, author = question["question"], get(guild.members, id=question["author"])
                    if not quest.endswith("?"):
                        quest += "?"
                    emb = getComEmbed(None, self.client, "Question Of The Day", quest)
                    emb.set_footer(text=f"Question submitted by {str(author)}")
                    await channel.send(embed=emb)
                    await self.client.CON.set_value(guild, "questions", questions)

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
    
    @commands.command(aliases=["qotdask"])
    @commands.cooldown(1, 5)
    async def qotdadd(self, ctx, *, question):
        channel = self.client.CON.get_value(ctx.guild, "qotd_channel", guild=ctx.guild)
        if channel:
            questions = self.client.CON.get_value(ctx.guild, "questions")
            questions.append({
                "question": question,
                "author": ctx.author.id
            })
            await self.client.CON.set_value(ctx.guild, "questions", questions)
            await ctx.send("Question added to qotd!")
            await ctx.message.delete()
        else:
            await ctx.send("This server doesn't have QOTD set up, consider asking an Admin as there may be another bot in charge of qotd!")

    @commands.command()
    @commands.cooldown(1, 3)
    async def qotdlist(self, ctx):
        channel = self.client.CON.get_value(ctx.guild, "qotd_channel", guild=ctx.guild)
        if channel:
            questions = self.client.CON.get_value(ctx.guild, "questions")
            if len(questions) > 0:
                txt = "\n- "
                for entry in questions:
                    user = get(ctx.guild.members, id=entry['author'])
                    txt += f"\'{entry['question']}\' - {user.name}\n- "
                txt = txt[:-2]
                await ctx.send(f"**All questions:**```{txt}```")
            else:
                await ctx.send(f"Looks like we're out of questions, use {self.client.getprefixguild(ctx.guild)}qotdadd to add more!")
        else:
            await ctx.send("This server doesn't have QOTD set up, consider asking an Admin as there may be another bot in charge of qotd!")

    @commands.command()
    @commands.cooldown(1, 3)
    async def qotdremove(self, ctx, val=None):
        channel = self.client.CON.get_value(ctx.guild, "qotd_channel", guild=ctx.guild)
        if channel:
            questions = self.client.CON.get_value(ctx.guild, "questions")
            if not val:
                txt = "\n- "
                ide = 1
                for entry in questions:
                    if ctx.channel.permissions_for(ctx.author).manage_messages or entry["author"] == ctx.author.id:
                        user = get(ctx.guild.members, id=entry['author'])
                        txt += f"{ide}: \'{entry['question']}\' - {user.name}\n- "
                        ide += 1
                txt = txt[:-2]
                if ide == 1:
                    return await ctx.send(f"You have 0 questions you can edit.")
                else:
                    return await ctx.send(f"**All questions you can remove (and their id):**```{txt}```")

            total = 0
            indexs = []
            for i, entry in enumerate(questions):
                if ctx.channel.permissions_for(ctx.author).manage_messages or entry["author"] == ctx.author.id:
                    indexs.append(i)
            if len(indexs) == 0:
                return await ctx.send("You have 0 questions you've asked, maybe ask one first idfk...")

            if val == "all": # all of em
                total = len(indexs)
                indexs.reverse()
                for i in indexs:
                    questions.pop(i)
            else:
                try:
                    val = int(val)
                except ValueError:
                    val = val # not an int pog!!!

                if type(val) == int and val > 0 and val <= len(indexs): # index
                    total = 1
                    questions.pop(indexs[val-1])
                elif type(val) == str: # spesific question
                    indexs.reverse()
                    for i in indexs:
                        if val in questions[i]["question"]:
                            questions.pop(i)
                            total += 1
  
            if total > 0:
                await self.client.CON.set_value(ctx.guild, "questions", questions)
                await ctx.send(f"Removed {total} question(s)!")
            else:
                await ctx.send(f"No questions removed, this may be because there are no matches or you entered an invalid value.")
        else:
            await ctx.send("This server doesn't have QOTD set up, consider asking an Admin as there may be another bot in charge of qotd!")

def setup(client):
    client.add_cog(QOTDCog(client))