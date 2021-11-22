import os
import discord
from discord.ext import commands, tasks
from discord.utils import get

from random import choice, randint

from functions import ComError, CooldownError, ParamError, SendDM

import json
with open('./profiles.json') as file:
	PROFILES = json.load(file)

# My Son.
class AidanBot(commands.Bot):
	def __setitem__(self, key, value):
		setattr(self, key, value)
	def __getitem__(self, key):
		return getattr(self, key)

	def getprefix(self, selfagain, message):
		return self.prefix
	def is_pipon_palace(ctx):
		if ctx.guild:
			return (ctx.guild.id == 836936601824788520)
		return False

	def __init__(self):
		self.version = "V1.1.1 (Rewrite)"
		self.botbanned = {}

		intents = discord.Intents.all()
		super().__init__(command_prefix=self.getprefix, case_insensitive=True, help_command=None, intents=intents, allowed_mentions=discord.AllowedMentions(everyone=False))

		for filename in os.listdir('./cogs'):
			if filename.endswith('.py'):
				self.load_extension(f'cogs.{filename[:-3]}')

	async def on_ready(self):
		if self.user.id == 804319602292949013:
			for name in PROFILES["main"]:
				self[name] = PROFILES["main"][name]
		elif self.user.id == 861571290132643850:
			for name in PROFILES["beta"]:
				self[name] = PROFILES["beta"][name]
		else:
			print("< client not recognised >")

		self.qotd_store_channel = get(get(self.guilds, id=879063875469860874).text_channels, id=895727615573360650)
		self.qotd_channel =       get(get(self.guilds, id=836936601824788520).text_channels, id=856977059132866571)
		#self.qotd_channel =       get(get(self.guilds, id=879063875469860874).text_channels, id=879064126561878036)

		print(f'Logged in: {self.user.name}')
		self.status_loop.start()

	async def on_message(self, message):
		ctx = await self.get_context(message)
		owner = await self.is_owner(ctx.author)
		if ctx.author.id in self.botbanned:
			return 
		if ctx.command and ctx.command.is_on_cooldown(ctx) and owner:
			ctx.command.reset_cooldown(ctx)
		await self.invoke(ctx)

	async def on_guild_join(self, guild):
		await SendDM(self.client, "SOMEONE DID WHAT?!?!", f"Added to {guild.name}!")

	async def on_guild_remove(self, guild):
		await SendDM(self.client, "SOMEONE DID WHAT?!?!", f"Removed from {guild.name}!")

	async def on_command_error(self, ctx, error):
		# cooldown
		if isinstance(error, commands.CommandOnCooldown):
			await CooldownError(ctx, self, "Command on cooldown!! Try again in {:.2f} seconds".format(error.retry_after))
			return False
		# missoing params
		if isinstance(error, commands.MissingRequiredArgument):
			await ParamError(ctx, self, error)
			return False
		# ones that should have uniqe message
		err = ""
		if isinstance(error, commands.CommandNotFound):
			err = "This command doesn't exist :/\nMaybe you typed it wrong? double check!"
		elif isinstance(error, commands.MissingPermissions) or isinstance(error, commands.CheckFailure):
			err = "You don't have permission to run this command :/"
		elif isinstance(error, commands.BotMissingPermissions):
			err = "I don't have permission to run this command :/"
		else:
			err = f"I seem to have ran into an error, It's best to let Aidan know.\n```{error}```"
		await ComError(ctx, self, err)

	@tasks.loop(minutes=5)
	async def status_loop(self):
		phrases = [
			"MOM GET THE CAMERA!", "Imagine using {other}.", "Almost 1 year old.",
			"HOW?!?!", "Go f{prefix}{prefix}k yourself..", "{prefix} for help... please?",
			"king of hearts, all in. it's not a sin to wanna win.", "offline", "only true OG's remeber {prefix}wake",
			"trans rights!", "{name} > {other}", "reject reactions, embrace buttons!","who am i??? no please tell me.",
			"Wanted for bot warcrimes - WilliamFrog", "Only occasionally pissing off god.", ":mmaker:",
			"{prefix}rate that phat ass :smirk:", "Familiy friendly :)))", "Minecraft with da bois!",
			"On the, like, {rand} rewrite.", "{prefix}killme, now please", "Who needs a database lol!",
			"Wasting Aidan's time :)", ":/", "{name} Encountered an error and this status was cancelled."
		]
		allphrases = [*phrases, *self.botphrases]
		phrase = choice(allphrases)
		await self.change_presence(activity=discord.Activity(name=phrase.format(name=self.name, other=self.other, prefix=self.prefix, rand=randint(5,25)),type=discord.ActivityType.playing))