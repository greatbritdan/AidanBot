import discord
from discord.ext import commands, tasks
from discord.utils import find, get

from replybot.replybot import replyBot
from utils.config import ConfigManager
from utils.checks import ab_check_slient
from utils.functions import sendError, sendCustomError, getComEmbed, sendComError, getErrorEmbed

import json, os, traceback, sys, re
from random import choice, randint

# My Son.
class AidanBot(commands.Bot):
	def __setitem__(self, key, value):
		setattr(self, key, value)
	def __getitem__(self, key):
		return getattr(self, key)
	
	def __init__(self, debug_guilds, revival_guild, offline=False):
		self.offline = offline

		self.isbeta = True
		self.settingup = True
		self.revival_guild = revival_guild
		if debug_guilds:
			self.debug_guilds = debug_guilds
		else:
			self.debug_guilds = []
		super().__init__(command_prefix="$",intents=discord.Intents.all())

		self.statuslooperrors = 0

	async def setup_hook(self):
		if not self.offline:
			self.CON = ConfigManager(self, "guild")
			self.UCON = ConfigManager(self, "user")
			self.replybot = replyBot(self)

			for filename in os.listdir('./cogs'):
				if filename.endswith('.py'):
					await self.load_extension(f'cogs.{filename[:-3]}')

		if len(self.debug_guilds) > 0:
			for guild in self.debug_guilds:
				await self.tree.sync(guild=guild)
		else:
			await self.tree.sync()

	async def on_ready(self):
		if self.offline:
			print(f"< Commands Cleared, logging out >")
			await self.close()
			return

		profile = "main"
		if self.user.id == 861571290132643850:
			profile = "beta"

		with open('./data/profiles.json') as file:
			profiles = json.load(file)
			self.name =            profiles[profile]["name"]
			self.pfp =             profiles[profile]["pfp"]
			self.isbeta =          profiles[profile]["isbeta"]
			self.info =            profiles[profile]["info"]
			self.embedcolor =      profiles[profile]["embedcolor"]
			self.embedcolorerror = profiles[profile]["embedcolorerror"]
			
		with open('./data/info.json') as file:
			info = json.load(file)
			self.version     = info["version"]
			self.lastupdate  = info["lastupdated"]
			self.ownername   = info["ownername"]
			self.ownerid     = info["ownerid"]
			self.youtube     = info["youtube"]
			self.youtubeplus = info["youtubeplus"]
			self.discord     = info["discord"]
			self.github      = info["github"]
			self.privacy     = info["privacy"]
			self.terms       = info["terms"]

		self.settingup = False
		if not self.statusloop.is_running():
			self.statusloop.start()
		print(f"< Logged in: {self.name} >")

		await self.CON.ready()
		await self.UCON.ready()
		await dict(self.cogs)["QOTDCog"].ready()

	async def on_error(self, event, *args, **kwargs):
		await sendError(self, event, sys.exc_info())

	async def on_command_error(self, ctx:commands.Context, error):
		await ctx.send(embed=getErrorEmbed(self, str(error)))
		if self.isbeta:
			print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
			traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)
		else:
			await sendComError(self, ctx, error)

	async def on_message(self, message:discord.Message):
		if self.settingup or message.author.bot or message.webhook_id:
			return
		if message.guild and message.guild.id == self.revival_guild:
			if "<:GentleGoomba:798327849412853760>" in message.content:
				# In memory of Gentle Goombot...
				return await message.channel.send("<:GentleGoomba:798327849412853760>")
			if self.isbeta:
				if message.channel.name == "aidanbetabot-talk":
					return await self.replybot.on_message(message)
			else:
				channels = self.CON.get_value(message.guild, "replybot_channel", guild=message.guild) # reply bot uwu
				if channels and message.channel in channels:
					return await self.replybot.on_message(message)
				if await ab_check_slient(None, self, user=message.author, guild=message.guild, channel=message.channel, is_guild=True, bot_has_permission="manage_messages"):
					if await self.handle_invites(message): # remove invites
						return
					nitront = self.CON.get_value(message.guild, "nitront", guild=message.guild) # not so nitro or some s#it
					if nitront and await self.handle_emojis(message):
						return

	async def on_member_join(self, member:discord.Member):
		if self.isbeta:
			return

		channel = self.CON.get_value(member.guild, "join_message_channel", guild=member.guild)
		msgs = self.CON.get_value(member.guild, "join_message")
		if channel and msgs:
			msg = choice(msgs)
			await channel.send(msg.format(name=member.name, mention=member.mention, user=member, member=member, server=member.guild, guild=member.guild))
		if await ab_check_slient(None, self, guild=member.guild, user=member, is_guild=True, bot_has_permission="manage_roles"):
			role = self.CON.get_value(member.guild, "join_role", guild=member.guild)
			if role:
				await member.add_roles(role)

	async def on_guild_join(self, guild:discord.Guild):
		if self.isbeta: return

		chan = find(lambda m: "general" in m.name, guild.text_channels)
		if not chan:
			chan = find(lambda m: "talk" in m.name, guild.text_channels)
		if not chan:
			clientmember = await guild.fetch_member(self.user.id)
			for channel in guild.text_channels:
				if channel.permissions_for(clientmember).send_messages:
					chan = channel
		if chan:
			info = f"I'm {self.name}, a dumb bot made by **{self.ownername}**. I'm a general bot that has many features and prides myself on not having premium or selling NFT's! From fun and useless commands like /opinion and /games, to more useful features using /config. I'll make a great addition to the server!!!\n\nBefore we get started, you might want to read my:\n- [Terms of service]({self.terms})\n- [Privacy Policy]({self.privacy})\n\n> **For aditional info on commands or permissions run /info!**"
			emb = getComEmbed(self, f"Hello world!.. oh uhh i meant {guild.name}!", info)
			await chan.send(embed=emb)

	async def on_guild_remove(self, guild:discord.Guild):
		if self.isbeta:
			return
		await self.CON.remove_group(guild)

	async def handle_invites(self, msg:discord.Message):
		channels = self.CON.get_value(msg.guild, "remove_invites_exempt_channels", guild=msg.guild)
		roles = self.CON.get_value(msg.guild, "remove_invites_exempt_roles", guild=msg.guild)
		hasrole = False
		if roles:
			for role in roles:
				if role in msg.author.roles:
					hasrole = True
					break

		if self.CON.get_value(msg.guild, "remove_invites") and ((not channels) or (msg.channel not in channels)) and ((not roles) or (not hasrole)):
			invites = re.findall(r'discord\.gg\/\S*|discord\.com\/invite\/\S*', msg.clean_content)
			if invites and len(invites) > 0:
				guildinviteids = []
				if await ab_check_slient(None, self, guild=msg.guild, user=msg.author, channel=msg.channel, is_guild=True, bot_has_permission="manage_guild"):
					for invite in await msg.guild.invites():
						guildinviteids.append(invite.id)
						#print(f"Guild ID: {invite.id}")
				for invite in invites:
					inviteid = invite.split("/")[-1]
					#print(f"Send ID: {inviteid}")
					if inviteid not in guildinviteids:
						await msg.delete()
						if channels:
							return await msg.channel.send(f"No posting invites outside of {self.CON.display_value('remove_invites_exempt_channels', channels)}. >:(")
						return await msg.channel.send("No posting invites in this server. >:(")

	async def handle_emojis(self, msg:discord.Message):
		emogis = re.findall(r':\w*:(?!\d*>)', msg.content)
		emogis = [e.replace(":","") for e in emogis]
		emogilesstext = re.split(r':\w*:(?!\d*>)', msg.content)
		if len(emogis) == 1 and emogilesstext[0] == "$" and emogilesstext[1] == "":
			realemogi = get(self.emojis, name=emogis[0])
			msgs = await msg.channel.history(limit=2).flatten()
			await msgs[1].add_reaction(realemogi)
			await msg.delete()
			return True
		elif len(emogis) > 0:
			txt = emogilesstext[0]
			for idx, emogi in enumerate(emogis):
				realemogi = get(self.emojis, name=emogi)
				if realemogi:
					txt = txt + str(realemogi) + emogilesstext[idx+1]
				else:
					txt = txt + ":" + emogi + ":" + emogilesstext[idx+1]
			if txt != msg.content:
				if await ab_check_slient(None, self, guild=msg.guild, user=msg.author, channel=msg.channel, is_guild=True, bot_has_permission="attach_files"):
					files = await self.attachmentsToFiles(msg.attachments)
				else:
					files = []
				await self.sendWebhook(msg.channel, msg.author.display_name, msg.author.display_avatar, txt, files)
				await msg.delete()
				return True
		return False

	async def attachmentsToFiles(self, attachments:list[discord.Attachment]):
		for f in os.listdir("./nitrontfiles"): # clear old items
			os.remove(os.path.join("./nitrontfiles", f))

		paths, filenames = [], []
		if len(attachments) > 0: # save all attackments
			for idx, file in enumerate(attachments):
				filenames.append(file.filename)
				path = f"./nitrontfiles/emogifile{idx}_{file.filename}"
				paths.append(path)
				await file.save(path)

		files = []
		if len(attachments) > 0: # create discord file objects of attachments
			for idx, _ in enumerate(paths):
				files.append(discord.File(paths[idx], filenames[idx]))
			
		return files
	
	async def sendWebhook(self, channel:discord.TextChannel, name, avatar, txt, files, repeat=None):
		hook = False
		for w in await channel.webhooks():
			if w.name == "AidanBotCloneHook":
				hook = w
		if not hook:
			hook = await channel.create_webhook(name="AidanBotCloneHook")

		try:
			msg = await hook.send(txt, username=name, avatar_url=avatar, files=files, allowed_mentions=discord.AllowedMentions(everyone=False, roles=False))
			if msg:
				return msg
			return False
		except Exception:
			await hook.delete()
			if (not repeat): # No more infinite loop
				return await self.sendWebhook(channel, name, avatar, txt, files, True)
			return False

	# No idea how this works, probbably stole it
	def make_ordinal(self, n):
		if 11 <= (n % 100) <= 13:
			suffix = 'th'
		else:
			suffix = ['th', 'st', 'nd', 'rd', 'th'][min(n % 10, 4)]
		return str(n) + suffix

	@tasks.loop(minutes=10)
	async def statusloop(self):
		status = {
			"playing": [ "/info for info", "$help for help", "Mari0: Alesan's Entities", "a very dangerous game...", "One Word Story", "Aidan's videos on repeat", "badbot", "Polish Grass Simulator" ],
			"watching": [ "the world fall apart...", "out for Waluigi!", "Aidan sleep", "the Bucket Wars", "Aidan rewrite me for the {nthtime} time", "people stop using me :(",
				"{servercount} Servers!", "{membercount} Members!", "One Word Story: The Movie", "other bots suck!", "Pip0n's Palace crumble lol" ],
			"streaming": [ "Polish Grass in 4K", "absolutely nothing", "the screams of my victims", "1's and 0's across the interwebs", "something... but you'll never know :)", "and screaming" ],
			"listening_to": [ "Aidan's nonexistant future lol", "my servers overheating", "Aidan complain about bots for the {nthtime} time", "everyone complain...", "Never Gonna Give You Up!" ],
			"competing_in": [ "an arm pit fart contest", "stuff with my brothers", "War Crimes Simulator!", "being better than Aidans Bots!", "a stupid bot contest (I'm winning)" ],
		}
		activity_type, group = choice(list(status.items()))

		if activity_type == "playing": activity_type = discord.ActivityType.playing
		if activity_type == "watching": activity_type = discord.ActivityType.watching
		if activity_type == "streaming": activity_type = discord.ActivityType.streaming
		if activity_type == "listening_to": activity_type = discord.ActivityType.listening
		if activity_type == "competing_in": activity_type = discord.ActivityType.competing
		content = choice(group).format(nthtime=self.make_ordinal(randint(1,24)), servercount=len(self.guilds), membercount=len(self.users))

		try:
			await self.change_presence(activity=discord.Activity(name=content,type=activity_type))
		except Exception:
			await sendCustomError(self, "Staus Change", f"Status failed to change to: {activity_type} {content}")
		self.statuslooperrors = 0

	@statusloop.error
	async def statuslooperror(self, error):
		self.statuslooperrors += 1
		if self.statuslooperrors >= 5:
			await sendCustomError(self, "Status Task Error", f"Status Task failed 5 times and has been shutdown, please fix and restart!\n\n{error}")
			if self.statusloop.is_running():
				self.statusloop.cancel()
		else:
			await sendCustomError(self, "Status Task Error", f"Status Task failed and will restart shortly!")
			if not self.statusloop.is_running():
				self.statusloop.start()

	def itrFail(self):
		if randint(1,6) == 1:
			comebacks = [
				"Did you try to poke my buttons? Sheeeeeesshh.", "Not your buttons! What a bruh moment.", "Sorry, you can't press this butt-on! :smirk:", "D-don't touch me user-san! >///<",
				"This button can't be hit.\nDespite the fact it's lit.\nYou try and fail,\nTo make it sail,\nBut I do not give a shit.", "It takes like, 10 seconds to just run your own command."
			]
			return choice(comebacks)
		else:

			return "Sorry, you can't press this button!"

