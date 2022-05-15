import discord
from discord.ext import commands
from discord.utils import find

import json, os, traceback, sys
from functions import SendDM, getComEmbed, getErrorEmbed

from replybot import replyBot
from config import ConfigManager
from github import Github

with open('./data/profiles.json') as file:
	PROFILES = json.load(file)

# My Son.
class AidanBot(commands.Bot):
	def __setitem__(self, key, value):
		setattr(self, key, value)
	def __getitem__(self, key):
		return getattr(self, key)

	def __init__(self, debug_guilds=None):
		self.settingup = True
		self.offline = True
		self.version = "V1 (Slash)"
		
		self.GIT = Github(os.getenv("GITHUB_TOKEN"))
		self.botreponame = "Aid0nModder/AidanBot"
		self.botrepo = self.GIT.get_repo(self.botreponame)
		self.CON = ConfigManager(self, ctype="guild") # guild config
		self.UCON = ConfigManager(self, ctype="user") # user config
		self.replybot = replyBot(self)

		intents = discord.Intents.all()
		mentions = discord.AllowedMentions(everyone=False, roles=False)
		super().__init__(debug_guilds=debug_guilds, command_prefix="!-/^", intents=intents, allowed_mentions=mentions)

		if self.offline:
			self.load_extension(f'cogs.offline')
		else:
			for filename in os.listdir('./cogs'):
				if filename.endswith('.py') and filename != "offline.py":
					self.load_extension(f'cogs.{filename[:-3]}')

	async def on_ready(self):
		profile = "main"
		if self.user.id == 861571290132643850:
			profile = "beta"
		for name in PROFILES[profile]:
			self[name] = PROFILES[profile][name]

		self.settingup = False
		await self.change_presence(activity=discord.Activity(name=f"/info for info",type=discord.ActivityType.playing))
		print(f"< Logged in: {self.name} >")

		await self.CON.ready()
		await self.UCON.ready()
		if not self.offline:
			await dict(self.cogs)["BirthdayCog"].ready()
			await dict(self.cogs)["QOTDCog"].ready()

	async def on_application_command_error(self, ctx, error):
		await ctx.respond(embed=getErrorEmbed(ctx, self, str(error)))
		if await self.is_owner(ctx.author):
			print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
			traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

	async def on_message(self, message):
		if self.settingup or message.author.bot or message.webhook_id:
			return
		ctx = await self.get_context(message)
		if (not isinstance(message.channel, discord.channel.DMChannel)):
			if (not self.isbeta) and await self.handle_invites(message): # remove invites
				return
			channel = self.CON.get_value(ctx.guild, "replybot_channel", guild=ctx.guild) # reply bot uwu
			if (not self.isbeta) and (not ctx.command) and channel and ctx.channel == channel:
				return await self.replybot.on_message(message)
			elif self.isbeta and message.channel.name == "aidanbetabot-talk":
				return await self.replybot.on_message(message)
			
	async def on_member_join(self, member):
		if not self.isbeta:
			return
		channel = self.CON.get_value(member.guild, "welcome_message_channel", guild=member.guild)
		msg = self.CON.get_value(member.guild, "welcome_message")
		if channel and msg:
			await channel.send(msg.format(name=member.name, mention=member.mention, user=member, member=member, server=member.guild, guild=member.guild))

	async def on_guild_join(self, guild):
		if not self.isbeta:
			return
		await SendDM(self, "SOMEONE DID WHAT?!?!", f"Added to {guild.name}!")
		
		chan = find(lambda m: "general" in m.name, guild.text_channels)
		if not chan:
			chan = find(lambda m: "talk" in m.name, guild.text_channels)
		if chan:
			emb = getComEmbed(None, self, f"Hello world!.. oh uhh i meant {guild.name}!", f"I'm {self.name}, a dumb bot made by Aidan#8883 (that mari0 guy).\nI'm a general bot that has many features and prides myself on not having premium or selling NFT's.\n\nFrom fun and useless commands like /opinion and /games, to more useful features like /role, And many configeration optuions using /config. I'll make a great addition to the server.\n\nBefore we get started, you might want to read my [Terms of service](https://github.com/Aid0nModder/AidanBot/blob/main/README.md#terms-of-service) and [Privacy Policy](https://github.com/Aid0nModder/AidanBot/blob/main/README.md#privacy-policy). As well as chck out my User guide (Coming soon).")
			await chan.send(embed=emb)

	async def on_guild_remove(self, guild):
		if not self.isbeta:
			return
		await self.CON.remove_group(guild)

	async def handle_invites(self, message):
		if "discord.gg" in message.content.lower() and self.CON.get_value(message.guild, "remove_invites"):
			channel = self.CON.get_value(message.guild, "allow_invites_channel", guild=message.guild)
			if ((not channel) or message.channel != channel) and (not message.channel.permissions_for(message.author).ban_members):
				await message.delete()
				if channel:
					return await message.channel.send(f"No posting invites outside of {channel.mention}. >:(")
				return await message.channel.send("No posting invites in this server. >:(")
