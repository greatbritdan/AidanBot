import discord
from discord.ext import commands, tasks

import os, traceback, sys
from random import choice, randint

from functions import ClientError, ComError, CooldownError, ExistError, ParamError, SendDM

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

	def __init__(self):
		self.version = "V1.3 (Rewrite)"

		intents = discord.Intents.all()
		super().__init__(command_prefix=self.getprefix, case_insensitive=True, help_command=None, intents=intents, allowed_mentions=discord.AllowedMentions(everyone=False))

		for filename in os.listdir('./cogs'):
			if filename.endswith('.py') and not filename.startswith('_'):
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

		print(f'Logged in: {self.user.name}')
		self.status_loop.start()

	async def on_message(self, message):
		if not self.is_ready():
			return

		ctx = await self.get_context(message)
		owner = await self.is_owner(ctx.author)
		if ctx.command and ctx.command.is_on_cooldown(ctx) and owner:
			ctx.command.reset_cooldown(ctx)

		await self.invoke(ctx)

	async def on_guild_join(self, guild):
		await SendDM(self.client, "SOMEONE DID WHAT?!?!", f"Added to {guild.name}!")

	async def on_guild_remove(self, guild):
		await SendDM(self.client, "SOMEONE DID WHAT?!?!", f"Removed from {guild.name}!")

	async def on_command_error(self, ctx, error):
		if isinstance(error, discord.ClientException):
			await ClientError(ctx, self, error)
		elif isinstance(error, commands.CommandOnCooldown):
			await CooldownError(ctx, self, error)
		elif isinstance(error, commands.MissingRequiredArgument):
			await ParamError(ctx, self, error)
		elif isinstance(error, commands.CommandNotFound):
			await ExistError(ctx, self)
		else:
			await ComError(ctx, self, error)
			if self.is_owner(ctx.author):
				print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
				traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

	@tasks.loop(minutes=10)
	async def status_loop(self):
		phrases = [
			"MOM GET THE CAMERA!", "Imagine using {other}.", "Almost 1 year old.",
			"HOW?!?!", "Go f{prefix}{prefix}k yourself..", "{prefix} for help... please?",
			"king of hearts, all in. it's not a sin to wanna win.", "offline", "only true OG's remeber {prefix}wake",
			"trans rights!", "{name} > {other}", "reject reactions, embrace buttons!","who am i??? no please tell me.",
			"Wanted for bot warcrimes - WilliamFrog", "Only occasionally pissing off god.", ":mmaker:",
			"{prefix}rate that phat ass :smirk:", "Familiy friendly :)))", "Minecraft with da bois!",
			"On the, like, {rand}th rewrite.", "chimken numgent", "Who needs a database lol!",
			"Wasting Aidan's time :)", ":/", "{name} Encountered an error and this status was cancelled.",
			"In memory of {prefix}uwu.. please rise", "", "Objectvly better than every other bot",
			"That was legitness.", "Add to Server or else.", "Physicly dead inside.",
			"Only idiots complain about the logo change.", "Knock Konck", "https://discord.gg/KXrDUZfBpq",
			"I can post animated emotes for free!", "NFT more like en ef pee *dabs*", "Why can't bots be in group DM's?",
			"?????????", "Yeah ok", "Sussy Sussy Sussy", "Lorem ipsum dolor sit amet",
			"if mee6 is next to me make sure to put them in the trash where NFT supporters belong."
		]
		allphrases = [*phrases, *self.botphrases]
		phrase = choice(allphrases)
		await self.change_presence(activity=discord.Activity(name=phrase.format(name=self.name, other=self.other, prefix=self.prefix, rand=randint(5,20)),type=discord.ActivityType.playing))
