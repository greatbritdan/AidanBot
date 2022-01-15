import discord
from discord.ext import commands, tasks
from discord.message import Attachment
from discord.utils import get

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
		self.values = {}
		self.valid_values = ["welcome_message", "welcome_message_channel","logs_channel"]
		self.default_values = {"welcome_message":"Please welcome {name}!","welcome_message_channel":False,"logs_channel":False}
		self.desc_values = {
			"welcome_message":"The message that sends when a user joins your server, only works if `welcome_message_channel` is set.\n**Type:** String",
			"welcome_message_channel":"The channel that receives a message when a user joins your server,\nFalse means off, String means channel name, Integer means channel id.\n**Type:** False/String/Integer",
			"logs_channel":"The channel that receives a message when your server is edited,\nFalse means off, String means channel name, Integer means channel id.\n**Type:** False/String/Integer",
		}

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
		
		await self.values_msgupdate("load")

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

	async def on_member_join(self, member):
		if self.client.isbeta:
			return
		chan = self.get_value(member.guild, "welcome_message_channel")
		if chan:
			channel = False
			if type(chan) == int:
				channel = get(member.guild.channels, id=chan)
			elif type(chan) == str:
				channel = get(member.guild.channels, name=chan)
			if channel:
				msg = self.get_value(member.guild, "welcome_message")
				await channel.send(msg.format(name=member.name, mention=member.mention))

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

	async def values_msgupdate(self, typ):
		guild = get(self.guilds, id=879063875469860874)
		channel = get(guild.channels, id=931917513128828960)
		message = await channel.fetch_message(channel.last_message_id)
		if typ == "load":
			byte = await message.attachments[0].read()
			txt = byte.decode("utf-8")
			self.values = json.loads(txt)
		elif typ == "save":
			await message.delete()
			with open("temp.json", "w") as f:
				json.dump(self.values, f, indent=4)
			await channel.send(file=discord.File("temp.json", "values.json"))

	def get_all(self, guild):
		if str(guild.id) in self.values:
			return self.values[str(guild.id)]
		return False
		
	def get_value(self, guild, name):
		if str(guild.id) in self.values and name in self.values[str(guild.id)]:
			return self.values[str(guild.id)][name]
		if name in self.default_values:
			return self.default_values[name]
		return False

	async def set_value(self, guild, name, value):
		if str(guild.id) in self.values and name in self.valid_values:
			self.values[str(guild.id)][name] = value
			return True
		return False
					
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
			"?????????", "Yeah ok", "Sussy Sussy Sussy", "Lorem ipsum dolor sit amet", "if mee6 is next to me make sure to put it in the trash where NFT supporters belong."
		]
		allphrases = [*phrases, *self.botphrases]
		phrase = choice(allphrases)
		await self.change_presence(activity=discord.Activity(name=phrase.format(name=self.name, other=self.other, prefix=self.prefix, rand=randint(5,20)),type=discord.ActivityType.playing))
