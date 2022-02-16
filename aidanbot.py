import discord
from discord.ext import commands, tasks
from discord.message import Attachment
from discord.utils import find, get

import os, traceback, sys
from random import choice, randint

from functions import ClientError, ComError, CooldownError, ExistError, ParamError, SendDM, getComEmbed

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
		self.version = "V1.3.5 (Rewrite)"
		self.values = {}
		self.valid_values = ["welcome_message", "welcome_message_channel","logs_channel","remove_invites","allow_invites_channel"]
		self.default_values = {"welcome_message":"Please welcome {name}!","welcome_message_channel":False,"logs_channel":False,"remove_invites":False,"allow_invites_channel":False}
		self.desc_values = {
			"welcome_message":"The message that sends when a user joins your server, only works if `welcome_message_channel` is set.\n**Type:** String",
			"welcome_message_channel":"The channel that receives a message when a user joins your server,\nFalse means off, String means channel name, Integer means channel id.\n**Type:** False/String/Integer",
			"logs_channel":"The channel that receives a message when your server is edited,\nFalse means off, String means channel name, Integer means channel id.\n**Type:** False/String/Integer",
			"remove_invites":"If invites are removed.\n**Type:** Boolean",
			"allow_invites_channel":"The channel that invites are allowed in,\nFalse means off, String means channel name, Integer means channel id.\n**Type:** False/String/Integer",
		}

		intents = discord.Intents(
			guilds=True, members=True, bans=True, emojis_and_stickers=False, integrations=False, webhooks=False,
			invites=False, voice_states=False, presences=False, messages=True, reactions=False, typing=False, scheduled_events=False
		)
		super().__init__(command_prefix=self.getprefix, case_insensitive=True, help_command=None, intents=intents, allowed_mentions=discord.AllowedMentions(everyone=False))

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
		
		await self.values_msgupdate("load")
		await self.change_presence(activity=discord.Activity(name=f"{self.prefix}help for help!",type=discord.ActivityType.playing))
		print(f'Logged in: {self.user.name}')

	async def on_message(self, message):
		if not self.is_ready():
			return

		if (not self.isbeta) and "discord.gg" in message.content.lower() and self.get_value(message.guild, "remove_invites"):
			channel = self.getvaluechannel(message.guild, self.get_value(message.guild, "allow_invites_channel"))
			if (not channel) or message.channel != channel:
				await message.delete()
				if channel:
					await message.channel.send(f"No posting invites outside of {channel.name}. >:(")
				else:
					await message.channel.send("No posting invites in this server. >:(")

		ctx = await self.get_context(message)
		owner = await self.is_owner(ctx.author)
		if ctx.command and ctx.command.is_on_cooldown(ctx) and owner:
			ctx.command.reset_cooldown(ctx)

		await self.invoke(ctx)

	async def on_member_join(self, member):
		if self.isbeta:
			return
		chan = self.get_value(member.guild, "welcome_message_channel")
		if chan:
			channel = self.getvaluechannel(member.guild, chan)
			if channel:
				msg = self.get_value(member.guild, "welcome_message")
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
			emb = getComEmbed(None, self, "Welcome!", f"Hello world!.. oh uhh i meant {guild.name}!", "I'm AidanBot, a dumb bot made by Aidan#8883 (that mari0 guy).\nI'm a general bot that has many features and prides myself on not having premium.\n\nFrom useless commands like $ask and $rate, to moderation features like a $timeout command. and everything imbetween. I'll make a great addition to the server.\n\nBefore we get started, you might want to read my [Terms of service](https://github.com/Aid0nModder/AidanBot/blob/main/README.md#terms-of-service) and [Privacy Policy](https://github.com/Aid0nModder/AidanBot/blob/main/README.md#privacy-policy). As well as chck out my User guide (Coming soon).", fields=[])
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

	async def set_value(self, guild, name, value):
		if str(guild.id) in self.values and name in self.valid_values:
			self.values[str(guild.id)][name] = value
			return True
		return False
