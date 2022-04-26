import discord
from discord.ext import commands
from discord.utils import find

import os, traceback, sys

from functions import ClientError, ComError, CooldownError, ExistError, ParamError, SendDM, getComEmbed

from replybot import replyBot
from config import ConfigManager

import json
with open('./data/profiles.json') as file:
	PROFILES = json.load(file)

# My Son.
class AidanBot(commands.Bot):
	def __setitem__(self, key, value):
		setattr(self, key, value)
	def __getitem__(self, key):
		return getattr(self, key)

	def getprefix(self, selfagain, message):
		if not self.isbeta:
			prefix = self.CON.get_value(message.guild, "prefix")
			if prefix:
				return prefix
		return self.prefix

	# same as above but just guild. useful when message or ctx is unavalable
	def getprefixguild(self, guild):
		if not self.isbeta:
			prefix = self.CON.get_value(guild, "prefix")
			if prefix:
				return prefix
		return self.prefix

	def __init__(self):
		self.version = "V2 Full"
		self.replybot = replyBot(self)
		self.CON = ConfigManager(self, ctype="guild") # guild config
		self.UCON = ConfigManager(self, ctype="user") # user config

		intents = discord.Intents( 
			guilds=True, members=True, bans=False, emojis_and_stickers=False, integrations=False, webhooks=False, invites=False,
			voice_states=False, presences=False, messages=True, message_content=True, reactions=False, typing=False, scheduled_events=False
		)
		super().__init__(command_prefix=self.getprefix, case_insensitive=True, help_command=None, intents=intents, allowed_mentions=discord.AllowedMentions(everyone=False, roles=False))

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
			await self.close()
			return
		
		await self.CON.ready()
		await self.UCON.ready()
		await self.change_presence(activity=discord.Activity(name=f"{self.prefix}help for help!",type=discord.ActivityType.playing))
		print(f"< Logged in: {self.user.name} >")

		await dict(self.cogs)["BirthdayCog"].ready()
		await dict(self.cogs)["QOTDCog"].ready()

	# events #

	async def on_message(self, message):
		ctx = await self.get_context(message) # Not out of context

		# don't post if not ready or a webhook
		if (not self.is_ready()) or message.webhook_id:
			return
		# remove invites
		if (not self.isbeta) and await self.handle_invites(message):
			return
		# replybot stufvs
		if (not isinstance(ctx.channel, discord.channel.DMChannel)) and (not message.clean_content.startswith(self.getprefix(self, message))) and message.channel.name == "aidanbot-talk" and not message.author.bot:
			return await self.replybot.on_message(message)
		# ping pong
		if (not ctx.command) and self.user.mentioned_in(message):
			emb = getComEmbed(None, self, "That is me!", f"Hey, ya pingd me! I assume you want to know my current prefix huh, it's **{self.getprefix(self, message)}**.")
			return await message.reply(embed=emb, mention_author=False)
		# i'm too cool for cooldowns
		owner = await self.is_owner(ctx.author)
		if ctx.command and ctx.command.is_on_cooldown(ctx) and owner:
			ctx.command.reset_cooldown(ctx)

		await self.invoke(ctx)

	async def on_member_join(self, member):
		if self.isbeta:
			return
		channel = self.CON.get_channel(member.guild, "welcome_message_channel", member.guild)
		msg = self.CON.get_value(member.guild, "welcome_message")
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

		self.CON.remove_all(guild)
		await self.CON.values_msgupdate("save")

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
			if await self.is_owner(ctx.author):
				print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
				traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

	async def handle_invites(self, message):
		if "discord.gg" in message.content.lower() and self.CON.get_value(message.guild, "remove_invites"):
			channel = self.CON.get_channel(message.guild, "allow_invites_channel", message.guild)
			if ((not channel) or message.channel != channel) and (not message.channel.permissions_for(message.author).ban_members):
				await message.delete()
				if channel:
					return await message.channel.send(f"No posting invites outside of {channel.name}. >:(")
				return await message.channel.send("No posting invites in this server. >:(")
