import discord
from discord.commands import SlashCommandGroup
from discord import Option, Color
from discord.utils import get, basic_autocomplete

import asyncio, datetime
from random import randint

from functions import getComEmbed
from checks import command_checks

def tobool(val):
	if val.lower() == "true":
		return True
	return False

async def auto_questions(ctx):
	questions = ctx.bot.CON.get_value(ctx.interaction.guild, "questions")
	return [q["question"] for q in questions if ctx.interaction.channel.permissions_for(ctx.interaction.user).manage_messages or q["author"] == ctx.interaction.user.id]

class QOTDCog(discord.Cog):
	def __init__(self, client):
		self.client = client

	async def ready(self):
		self.client.loop.create_task(self.background_task())
		
	async def askQuestion(self, testpost=False, postguild=False):
		if self.client.isbeta:
			return
		for guild in await self.client.CON.loopdata():
			if (not postguild) or postguild == guild:
				channel = self.client.CON.get_value(guild, "qotd_channel", guild=guild)
				if channel:
					questions = self.client.CON.get_value(guild, "questions")
					if len(questions) == 0:
						emb = getComEmbed(None, self.client, "Question Of The Day", f"Looks like we're out of questions, use /qotd config to add more!", Color.from_rgb(145, 29, 37))
						await channel.send(embed=emb)
					else:
						questioni = randint(0, len(questions)-1)
						question = questions[questioni]

						quest, author = question["question"], get(guild.members, id=question["author"])
						if not quest.endswith("?"): quest += "?"
						emb = getComEmbed(None, self.client, "Question Of The Day", quest)
						emb.set_footer(text=f"Question submitted by {str(author)}")

						txt, role = "", self.client.CON.get_value(guild, "qotd_role", guild=guild)
						if (not testpost) and role:
							txt = f"Wake up sussy's, New QOTD dropped. {role.mention}"
						await channel.send(txt, embed=emb, allowed_mentions=discord.AllowedMentions(roles=True))
						if not testpost:
							questions.pop(questioni)
							await self.client.CON.set_value(guild, "questions", questions)
							
	async def background_task(self):
		when = datetime.time(15,0,0)
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
			await self.askQuestion()
			tomorrow = datetime.datetime.combine(now.date() + datetime.timedelta(days=1), datetime.time(0))
			seconds = (tomorrow - now).total_seconds()
			await asyncio.sleep(seconds)

	qotdgroup = SlashCommandGroup("qotd", "Question Of The Day commands.")

	@qotdgroup.command(name="post", description="Forcefully post a question.")
	async def post(self, ctx,
		testpost:Option(str, "If the question isn't removed from the questions list, useful for tests.", choices=["True", "False"], default="True")
	):
		if await command_checks(ctx, self.client, is_owner=True, is_guild=True, has_value="qotd_channel"): return

		await self.askQuestion(tobool(testpost), ctx.guild)
		await ctx.respond("Question has been askified.")

	@qotdgroup.command(name="config", description="Ask, List and remove questions.")
	async def config(self, ctx,
		action:Option(str, "Config action.", choices=["List","Ask","Remove"], required=True),
		ask:Option(str, "Write a question you want to ask.", required=False),
		remove:Option(str, "Choose the question you want to remove.", autocomplete=basic_autocomplete(auto_questions), required=False)
	):
		if await command_checks(ctx, self.client, is_guild=True, has_value="qotd_channel"): return

		questions = self.client.CON.get_value(ctx.guild, "questions")
		embed = False
		if action == "List":
			if len(questions) == 0:
				embed = getComEmbed(ctx, self.client, f"All questions for {ctx.guild.name}:", "Looks like we're out of questions, use /qotd config to add more!")
			else:
				txt = ""
				for quest in questions:
					member = get(ctx.guild.members, id=quest["author"])
					txt += f"\n**'" + quest["question"] + "':** " + str(member)
				embed = getComEmbed(ctx, self.client, f"All questions for {ctx.guild.name}:", txt)
		elif action == "Ask" and ask:
			if len(ask) > 100:
				return await ctx.respond("Too many characters! Questions mustn't be more than 100 characters.")
			if len([q for q in questions if q["question"] == ask]) > 0:
				return await ctx.respond("You can't send the same question as someone else.")
			questions.append({ "question": ask, "author": ctx.author.id })
			await self.client.CON.set_value(ctx.guild, "questions", questions)
			embed = getComEmbed(ctx, self.client, f"Added question!")
		elif action == "Remove" and remove:
			questions = [q for q in questions if q["question"] != remove]
			await self.client.CON.set_value(ctx.guild, "questions", questions)
			embed = getComEmbed(ctx, self.client, f"Removed question!")
		else:
			return await ctx.respond("Seems like you're missing some arguments. Try again.")
		await ctx.respond(embed=embed)

def setup(client):
	client.add_cog(QOTDCog(client))