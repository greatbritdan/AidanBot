import discord
from discord.ext import commands
from discord.utils import find, get
from github import Repository

import json, os, traceback, sys, re

from replybot import replyBot
from config import ConfigManager
from functions import sendError, sendComError, SendDM, getComEmbed, getComErrorEmbed
from checks import command_checks_silent

# My Son.
class AidanBot(commands.Bot):
	def __setitem__(self, key, value):
		setattr(self, key, value)
	def __getitem__(self, key):
		return getattr(self, key)

	def mentioncommand(self, name):
		return self.get_application_command(name).mention

	def __init__(self, repo:Repository, debug_guilds=None, offline=False):
		self.settingup = True
		self.offline = offline
		self.version = "V2 (Slash)"

		intents = discord.Intents.all()
		mentions = discord.AllowedMentions(everyone=False, roles=False)
		super().__init__(debug_guilds=debug_guilds, prefix="kdkldewkldlkw", intents=intents, allowed_mentions=mentions)

		if not self.offline:
			self.botrepo = repo
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

		with open('./data/profiles.json') as file:
			profiles = json.load(file)
		for name in profiles[profile]:
			self[name] = profiles[profile][name]

		self.settingup = False
		await self.change_presence(activity=discord.Activity(name=f"/info for info",type=discord.ActivityType.playing))
		print(f"< Logged in: {self.name} >")

		await self.CON.ready()
		await self.UCON.ready()
		await dict(self.cogs)["BirthdayCog"].ready()
		await dict(self.cogs)["QOTDCog"].ready()
		await dict(self.cogs)["UserCog"].ready()

	async def on_error(self, event, *args, **kwargs):
		if self.isbeta:
			await sendError(self, event, sys.exc_info())

	async def on_application_command_error(self, ctx:discord.ApplicationContext, error):
		if isinstance(error, commands.CommandOnCooldown):
			await ctx.respond(f"This command is currently on cooldown. Try again in {error.retry_after:.2f} seconds.")
		else:
			await ctx.respond(embed=getComErrorEmbed(ctx, self, str(error)))
			if self.isbeta:
				await sendComError(self, ctx, error)
			print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
			traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

	async def on_message(self, message:discord.Message):
		if self.settingup or message.author.bot or message.webhook_id:
			return
		if self.isbeta:
			if message.channel.id == 971157179446984794:
				return await self.replybot.on_message(message)
			return

		ctx:commands.Context = await self.get_context(message)
		if ctx.guild:
			if await self.handle_invites(ctx): # remove invites
				return
			if not ctx.command:
				channels = self.CON.get_value(ctx.guild, "replybot_channel", guild=ctx.guild) # reply bot uwu
				if channels and ctx.channel in channels:
					return await self.replybot.on_message(message)
				nqn = get(ctx.guild.members, id=559426966151757824)
				if (not nqn) and await self.handle_emojis(ctx):
					return

	async def on_member_join(self, member:discord.Member):
		if self.isbeta: return

		channel = self.CON.get_value(member.guild, "join_message_channel", guild=member.guild)
		msg = self.CON.get_value(member.guild, "join_message")
		if channel and msg:
			await channel.send(msg.format(name=member.name, mention=member.mention, user=member, member=member, server=member.guild, guild=member.guild))

		if not await command_checks_silent(None, self, guild=member.guild, user=member, is_guild=True, bot_has_permission="manage_roles"):
			role = self.CON.get_value(member.guild, "join_role", guild=member.guild)
			if role:
				await member.add_roles(role)

	async def on_guild_join(self, guild:discord.Guild):
		if self.isbeta: return
		await SendDM(self, "SOMEONE DID WHAT?!?!", f"Added to {guild.name}!")
		
		chan = find(lambda m: "general" in m.name, guild.text_channels)
		if not chan:
			chan = find(lambda m: "talk" in m.name, guild.text_channels)
		if not chan:
			for channel in guild.text_channels:
				if channel.can_send():
					chan = channel
		if chan:
			info = f'''
			I'm {self.name}, a dumb bot made by **Aidan#8883**. I'm a general bot that has many features and prides myself on not having premium or selling NFT's! From fun and useless commands like /opinion and /games, to more useful features using /config. I'll make a great addition to the server!!!

			Before we get started, you might want to read my:
			- [Terms of service](https://github.com/Aid0nModder/AidanBot/blob/main/README.md#terms-of-service)
			- [Privacy Policy](https://github.com/Aid0nModder/AidanBot/blob/main/README.md#privacy-policy)

			> **For aditional info on commands or permissions run {self.mentioncommand("info")}!**
			'''
			emb = getComEmbed(None, self, f"Hello world!.. oh uhh i meant {guild.name}!", info)
			await chan.send(embed=emb)

	async def on_guild_remove(self, guild:discord.Guild):
		if self.isbeta: return
		await self.CON.remove_group(guild)

	async def handle_invites(self, ctx:commands.Context):
		channels = self.CON.get_value(ctx.guild, "remove_invites_exempt_channels", guild=ctx.guild)
		roles = self.CON.get_value(ctx.guild, "remove_invites_exempt_roles", guild=ctx.guild)
		hasrole = False
		if roles:
			for role in roles:
				if role in ctx.author.roles:
					hasrole = True
					break

		if self.CON.get_value(ctx.guild, "remove_invites") and ((not channels) or (ctx.channel not in channels)) and ((not roles) or (not hasrole)):
			invites = re.findall(r'discord\.gg\/\S*|discord\.com\/invite\/\S*', ctx.message.clean_content)
			if invites and len(invites) > 0:
				guildinviteids = []
				if not await command_checks_silent(ctx, self, is_guild=True, bot_has_permission="manage_guild"):
					for invite in await ctx.guild.invites():
						guildinviteids.append(invite.id)
						#print(f"Guild ID: {invite.id}")
				for invite in invites:
					inviteid = invite.split("/")[-1]
					#print(f"Send ID: {inviteid}")
					if inviteid not in guildinviteids:
						await ctx.message.delete()
						if channels:
							return await ctx.send(f"No posting invites outside of {self.CON.display_value('remove_invites_exempt_channels', channels)}. >:(")
						return await ctx.send("No posting invites in this server. >:(")

	async def handle_emojis(self, ctx:commands.Context):
		emogis = re.findall(r':\w*:(?!\d*>)', ctx.message.content)
		emogis = [e.replace(":","") for e in emogis]
		emogilesstext = re.split(r':\w*:(?!\d*>)', ctx.message.content)
		if len(emogis) == 1 and emogilesstext[0] == "$" and emogilesstext[1] == "":
			realemogi = get(self.emojis, name=emogis[0])
			msgs = await ctx.channel.history(limit=2).flatten()
			await msgs[1].add_reaction(realemogi)
			await ctx.message.delete()
			return True
		elif len(emogis) > 0:
			txt = emogilesstext[0]
			for idx, emogi in enumerate(emogis):
				realemogi = get(self.emojis, name=emogi)
				if realemogi:
					txt = txt + str(realemogi) + emogilesstext[idx+1]
				else:
					txt = txt + ":" + emogi + ":" + emogilesstext[idx+1]
			if txt != ctx.message.content:
				if not await command_checks_silent(ctx, self, is_guild=True, bot_has_permission="attach_files"):
					files = await self.attachmentsToFiles(ctx.message.attachments)
				else:
					files = []
				await self.sendWebhook(ctx.channel, ctx.author, txt, files)
				await ctx.message.delete()
				return True
		return False

	async def attachmentsToFiles(self, attachments):
		for f in os.listdir("./nitrontfiles"): # clear old items
			os.remove(os.path.join("./nitrontfiles", f))

		paths, filenames = [], []
		if len(attachments) > 0: # save all attackments
			for idx, file in enumerate(attachments):
				filenames.append(file.filename)
				path = f"./nitrontfiles/emogifile{idx}_{file.filename}"
				paths.append(path)
				await file.save(path)

		files = None
		if len(attachments) > 0: # create discord file objects of attachments
			files = []
			for idx, _ in enumerate(paths):
				files.append(discord.File(paths[idx], filenames[idx]))
			
		return files

	async def sendWebhook(self, channel:discord.TextChannel, user:discord.Member, txt, files, nameadd=None):
		hook = False
		for w in await channel.webhooks():
			if w.name == "AidanBotCloneHook":
				hook = w
		if not hook:
			hook = await channel.create_webhook(name="AidanBotCloneHook")

		try:
			if nameadd:
				await hook.send(txt, username=user.display_name+nameadd, avatar_url=user.display_avatar, files=files)
			else:
				await hook.send(txt, username=user.display_name, avatar_url=user.display_avatar, files=files)
		except:
			await hook.delete()
			await self.sendWebhook(channel, user, txt, files, nameadd)
