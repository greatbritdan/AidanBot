import discord
from discord.ext import commands
from discord.utils import find, get

import json, os, traceback, sys, datetime, re
from functions import SendDM, getComEmbed, getErrorEmbed

from replybot import replyBot
from config import ConfigManager

with open('./data/profiles.json') as file:
	PROFILES = json.load(file)

# My Son.
class AidanBot(commands.Bot):
	def __setitem__(self, key, value):
		setattr(self, key, value)
	def __getitem__(self, key):
		return getattr(self, key)

	def __init__(self, github, debug_guilds=None, offline=False):
		self.settingup = True
		self.offline = offline
		self.version = "V1.2 (Slash)"

		intents = discord.Intents.all()
		mentions = discord.AllowedMentions(everyone=False, roles=False)
		super().__init__(debug_guilds=debug_guilds, prefix="kdkldewkldlkw", intents=intents, allowed_mentions=mentions)

		if not self.offline:
			self.GIT = github
			self.botreponame = "Aid0nModder/AidanBot"
			self.botrepo = self.GIT.get_repo(self.botreponame)
			self.CON = ConfigManager(self, ctype="guild") # guild config
			self.UCON = ConfigManager(self, ctype="user") # user config
			self.replybot = replyBot(self)

			for filename in os.listdir('./cogs'):
				if filename.endswith('.py') and filename != "offline.py":
					self.load_extension(f'cogs.{filename[:-3]}')

	async def on_ready(self):
		if self.offline:
			print(f"< Commands Cleared, logging out >")
			await self.close()

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

		# automod
		if ctx.guild and ctx.guild.id == 836936601824788520:
			msg = message.content.lower()
			# saying them feels wrong
			if "ni##er".replace("#","g") in msg or "fa##ot".replace("#","g") in msg or "#eta#d".replace("#","r") in msg:
				await ctx.author.timeout_for(datetime.timedelta(days=7), reason="Slur, check for validity and ban if nessasary.")
				role = get(ctx.guild.roles, id=836937774598848512)
				await ctx.send(f"{role.mention} Someone was trying to be funny.")
				await ctx.message.delete()
			# no ping pong >:(
			mentions = [user for user in ctx.message.mentions if (not user.bot)]
			if len(mentions) > 4:
				await ctx.author.timeout_for(datetime.timedelta(days=2), reason="Mass-Ping, check for validity and ban if nessasary.")
				role = get(ctx.guild.roles, id=836937774598848512)
				await ctx.send(f"**SPAM PING!**\n\nAidanBot would like to apologise to {', '.join([user.name for user in mentions])} on behalf of {str(ctx.author)}.\n\n{role.mention} Someone was trying to be funny.")
				await ctx.message.delete()

		if ctx.guild:
			if (not self.isbeta) and await self.handle_invites(message): # remove invites
				return
			if not ctx.command:
				channels = self.CON.get_value(ctx.guild, "replybot_channel", guild=ctx.guild) # reply bot uwu
				if (not self.isbeta) and channels and ctx.channel in channels:
					return await self.replybot.on_message(message)
				elif self.isbeta and message.channel.name == "aidanbetabot-talk":
					return await self.replybot.on_message(message)

				'''nqn = get(ctx.guild.members, id=559426966151757824)
				if not nqn:
					emogis = re.findall(r':\w*:(?!\d*>)', ctx.message.content)
					emogis = [e.replace(":","") for e in emogis]
					emogilesstext = re.split(r':\w*:(?!\d*>)', ctx.message.content)
					if len(emogis) > 0:
						txt = emogilesstext[0]
						for idx, emogi in enumerate(emogis):
							realemogi = get(self.emojis, name=emogi)
							if realemogi:
								txt = txt + str(realemogi) + emogilesstext[idx+1]
							else:
								txt = txt + ":" + emogi + ":" + emogilesstext[idx+1]
						if txt != ctx.message.content:
							await cloneUser(ctx.channel, ctx.author, txt)'''

	async def on_member_join(self, member):
		if self.isbeta:
			return
		channel = self.CON.get_value(member.guild, "welcome_message_channel", guild=member.guild)
		msg = self.CON.get_value(member.guild, "welcome_message")
		if channel and msg:
			await channel.send(msg.format(name=member.name, mention=member.mention, user=member, member=member, server=member.guild, guild=member.guild))

	async def on_guild_join(self, guild):
		if self.isbeta:
			return
		await SendDM(self, "SOMEONE DID WHAT?!?!", f"Added to {guild.name}!")
		
		chan = find(lambda m: "general" in m.name, guild.text_channels)
		if not chan:
			chan = find(lambda m: "talk" in m.name, guild.text_channels)
		if chan:
			emb = getComEmbed(None, self, f"Hello world!.. oh uhh i meant {guild.name}!", f"I'm {self.name}, a dumb bot made by Aidan#8883 (that mari0 guy).\nI'm a general bot that has many features and prides myself on not having premium or selling NFT's.\n\nFrom fun and useless commands like /opinion and /games, to more useful features like /role, And many configeration optuions using /config. I'll make a great addition to the server.\n\nBefore we get started, you might want to read my [Terms of service](https://github.com/Aid0nModder/AidanBot/blob/main/README.md#terms-of-service) and [Privacy Policy](https://github.com/Aid0nModder/AidanBot/blob/main/README.md#privacy-policy). As well as chck out my User guide (Coming soon).")
			await chan.send(embed=emb)

	async def on_guild_remove(self, guild):
		if self.isbeta:
			return
		await self.CON.remove_group(guild)

	async def handle_invites(self, message):
		if "discord.gg" in message.content.lower() and self.CON.get_value(message.guild, "remove_invites"):
			channels = self.CON.get_value(message.guild, "allow_invites_channel", guild=message.guild)
			if ((not channels) or message.channel not in channels) and (not message.channel.permissions_for(message.author).ban_members):
				await message.delete()
				if channels:
					return await message.channel.send(f"No posting invites outside of {self.CON.display_value('allow_invites_channel', channels)}. >:(")
				return await message.channel.send("No posting invites in this server. >:(")
