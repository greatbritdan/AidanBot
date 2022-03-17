import discord
from discord.ext import commands
from discord.utils import find, get

import os, traceback, sys

from functions import ClientError, ComError, CooldownError, ExistError, ParamError, SendDM, getComEmbed

import json
with open('./data/profiles.json') as file:
	PROFILES = json.load(file)
with open('./data/values.json') as file:
	VALUES = json.load(file)

# My Son.
class AidanBot(commands.Bot):
	def __setitem__(self, key, value):
		setattr(self, key, value)
	def __getitem__(self, key):
		return getattr(self, key)

	def getprefix(self, selfagain, message):
		return self.prefix

	def __init__(self):
		self.version = "V1.4.5 (Rewrite)"

		intents = discord.Intents( guilds=True, members=True, bans=True, emojis_and_stickers=False, integrations=False, webhooks=False, invites=False, voice_states=False, presences=False, messages=True, message_content=True, reactions=False, typing=False, scheduled_events=False )
		super().__init__(command_prefix=self.getprefix, case_insensitive=True, help_command=None, intents=intents, allowed_mentions=discord.AllowedMentions(everyone=False, roles=False))

		for filename in os.listdir('./cogs'):
			if filename.endswith('.py') and not filename.startswith('_'):
				self.load_extension(f'cogs.{filename[:-3]}')

	def getvaluechannel(self, guild, chan):
		channel = False
		if type(chan) == int:
			channel = get(guild.channels, id=chan)
		elif type(chan) == str:
			channel = get(guild.channels, name=chan)
		return channel

	async def on_ready(self):
		if self.user.id == 804319602292949013:
			for name in PROFILES["main"]:
				self[name] = PROFILES["main"][name]
		elif self.user.id == 861571290132643850:
			for name in PROFILES["beta"]:
				self[name] = PROFILES["beta"][name]
		else:
			print("< client not recognised >")
			return

		self.values = {}
		self.valid_values = []
		self.default_values = {}
		self.desc_values = {}
		for val in VALUES:
			self.valid_values.append(val)
			self.default_values[val] = VALUES[val]["default"]
			self.desc_values[val] = VALUES[val]["help"]
		
		await self.values_msgupdate("load")
		await self.change_presence(activity=discord.Activity(name=f"{self.prefix}help for help!",type=discord.ActivityType.playing))
		print(f"< Logged in: {self.user.name} >")

	# events #

	async def on_message(self, message):
		if not self.is_ready():
			return
		if (not self.isbeta) and await self.handle_invites(message):
			return

		ctx = await self.get_context(message)
		owner = await self.is_owner(ctx.author)
		if ctx.command and ctx.command.is_on_cooldown(ctx) and owner:
			ctx.command.reset_cooldown(ctx)

		await self.invoke(ctx)

	async def handle_invites(self, message):
		if "discord.gg" in message.content.lower() and self.get_value(message.guild, "remove_invites"):
			channel = self.getvaluechannel(message.guild, self.get_value(message.guild, "allow_invites_channel"))
			if ((not channel) or message.channel != channel) and (not message.channel.permissions_for(message.author).ban_members):
				await message.delete()
				if channel:
					return await message.channel.send(f"No posting invites outside of {channel.name}. >:(")
				return await message.channel.send("No posting invites in this server. >:(")

	async def on_member_join(self, member):
		if self.isbeta:
			return
		channel = self.getvaluechannel(member.guild, self.get_value(member.guild, "welcome_message_channel"))
		msg = self.get_value(member.guild, "welcome_message")
		if channel and msg:
			await channel.send(msg.format(name=member.name, mention=member.mention, user=member, member=member, server=member.guild, guild=member.guild))

	async def on_guild_join(self, guild):
		await SendDM(self, "SOMEONE DID WHAT?!?!", f"Added to {guild.name}!")

		chan = find(lambda m: "general" in m.name, guild.text_channels)
		if not chan:
			chan = find(lambda m: "talk" in m.name, guild.text_channels)
		if not chan:
			for c in guild.text_channels:
				if c.can_send():
					chan = c
					break
		if chan:
			emb = getComEmbed(None, self, "Welcome!", f"Hello world!.. oh uhh i meant {guild.name}!", f"I'm {self.name}, a dumb bot made by Aidan#8883 (that mari0 guy).\nI'm a general bot that has many features and prides myself on not having premium.\n\nFrom useless commands like $ask and $rate, to moderation features like a $timeout command. and everything imbetween. I'll make a great addition to the server.\n\nBefore we get started, you might want to read my [Terms of service](https://github.com/Aid0nModder/AidanBot/blob/main/README.md#terms-of-service) and [Privacy Policy](https://github.com/Aid0nModder/AidanBot/blob/main/README.md#privacy-policy). As well as chck out my User guide (Coming soon).", fields=[])
			await chan.send(embed=emb)

	async def on_guild_remove(self, guild):
		await SendDM(self, "SOMEONE DID WHAT?!?!", f"Removed from {guild.name}!")

		self.remove_all(guild)
		await self.values_msgupdate("save")

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

	# epic values #

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

	def remove_all(self, guild):
		if str(guild.id) in self.values:
			self.values[str(guild.id)] = None
			return True
		return False

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

	def set_value(self, guild, name, value):
		if str(guild.id) in self.values and name in self.valid_values:
			self.values[str(guild.id)][name] = value
			return True
		return False
