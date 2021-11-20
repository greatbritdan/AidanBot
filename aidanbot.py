import os
import discord
from discord.ext import commands
from discord.utils import get

import json
import time

from functions import CooldownError, Error, sendToWorkshop, strtolist, listtostr

def is_pipon_palace(ctx):
	if ctx.guild:
		return (ctx.guild.id == 836936601824788520)

aidanbot_desc = '''I am a small discord bot created by [Aidan#8883](https://discordapp.com/users/384439774972215296/) for his server that now anyone can use!

[Aidan's Youtube](https://www.youtube.com/c/AidanMapper)  |  [Aidan's Discord Server](https://discord.gg/KXrDUZfBpq)  |  [Invite me to your server!](https://discord.com/api/oauth2/authorize?client_id=804319602292949013&permissions=8&scope=bot)

If you find a bug or he has made a typo <:AidanSmug:837001740947161168>,
you can report it to Aidan on his server in one of the bot chats.
You can also suggest features in the suggestion channel on his server.'''

aidanbetabot_desc = '''I am test discord bot created by [Aidan#8883](https://discordapp.com/users/384439774972215296/) to test features before being launched to the main!

[Aidan's Youtube](https://www.youtube.com/c/AidanMapper)  |  [Aidan's Discord Server](https://discord.gg/KXrDUZfBpq)

If you find a bug or he has made a typo <:AidanSmug:837001740947161168>,
you can report it to Aidan on his server in one of the bot chats.
You can also suggest features in the suggestion channel on his server.'''

# My Son.
class AidanBot(commands.Bot):
	def getprefix(self):
		return self.PREFIX

	def __init__(self, prefix):
		# vars #
		self.NAME = "AidanBot"
		self.DESC = aidanbot_desc
		self.PREFIX = prefix
		self.VERSION = "Full Release V1.1"
		self.ISBETA = False
		self.ASLEAP = False
		self.custom_commands = {}
		self.BOTBANNED = {}

		intents = discord.Intents.all()
		super().__init__(command_prefix=self.getprefix(), case_insensitive=True, help_command=None, intents=intents, allowed_mentions=discord.AllowedMentions(everyone=False))

		for filename in os.listdir('./cogs'):
			if filename.endswith('.py') and filename != "qotd.py": #QOTD is on break
				self.load_extension(f'cogs.{filename[:-3]}')

	async def on_ready(self):
		print(f'Logged in: {self.user}')

		if self.user.id == 861571290132643850:
			self.NAME = "AidanBetaBot"
			self.DESC = aidanbetabot_desc
			self.ISBETA = True
		await self.change_presence(activity=discord.Activity(name=f'{self.PREFIX}help for help.',type=discord.ActivityType.competing))

		if os.path.isfile("restart.json"):
			with open("restart.json", "r") as fp:
				restart = json.load(fp)

				guild = get(self.guilds, id=restart["guild_id"])
				channel = get(guild.text_channels, id=restart["channel_id"])
				diftime = round(time.time()-restart["time"], 3)
				if diftime > 6:
					await channel.send(f"Good job dumbass <:AidanSmug:837001740947161168>.\n\nRestarted!\nTime: {diftime} seconds")
				else:
					await channel.send(f"Restarted!\nTime: {diftime} seconds")

			os.remove("restart.json")

		await self.load_custom_commands()

	async def on_message(self, message):
		ctx = await self.get_context(message)
		owner = await self.is_owner(ctx.author)

		if owner or (not self.ASLEAP):
			if ctx.author.id in self.BOTBANNED:
				return 

			if ctx.command and ctx.command.is_on_cooldown(ctx) and owner:
				ctx.command.reset_cooldown(ctx)

			if is_pipon_palace(ctx):
				suc = await self.send_custom_command(ctx)
				if suc:
					return
			await self.invoke(ctx)
		elif ctx.command:
			await ctx.send("I'm currently paused, no commands for now ^^;")

	async def on_guild_join(self, guild):
		await sendToWorkshop(None, self.client, "SOMEONE DID WHAT?!?!", f"Added to {guild.name}!")

	async def on_guild_remove(self, guild):
		await sendToWorkshop(None, self.client, "SOMEONE DID WHAT?!?!", f"Removed from {guild.name}!")

	async def on_command_error(self, ctx, error):
		# cooldown
		if isinstance(error, commands.CommandOnCooldown):
			await CooldownError(ctx, self, "Command on cooldown!! Try again in {:.2f} seconds".format(error.retry_after))
			return False
		# ones that should have uniqe message
		err = ""
		if isinstance(error, commands.CommandNotFound):
			err = "This command doesn't exist :/\n\nMaybe you typed it wrong? double check!"
		elif isinstance(error, commands.CheckFailure):
			err = "You don't have permission to run this command :/"
		elif isinstance(error, commands.BotMissingPermissions):
			err = "I am missing permissions to do this :/"
		elif isinstance(error, commands.MissingPermissions):
			err = "You are missing permissions to do this :/"
		else:
			err = f"I seem to have ran into an error, It's best to let Aidan know.\n\nError: {error}"
		await Error(ctx, self, err)

	# custom command shit #

	async def add_custom_command(self, name=None, text=None):
		self.custom_commands[name] = text
		await self.update_custom_commands("set")
	
	async def remove_custom_command(self, name=None):
		self.custom_commands.pop(name)
		await self.update_custom_commands("set")

	async def load_custom_commands(self):
		await self.update_custom_commands("get")

	async def update_custom_commands(self, typ):
		guild = get(self.guilds, id=879063875469860874)
		channel = get(guild.text_channels, id=909561005875548250)
		msg = await channel.fetch_message(channel.last_message_id)
		if typ == "set":
			await msg.delete()
			await channel.send(listtostr([self.custom_commands]))
		elif typ == "get":
			self.custom_commands = strtolist(msg.clean_content)[0]

	async def send_custom_command(self, ctx):
		for name in self.custom_commands:
			if ctx.message.content == f"{self.PREFIX}{name}":
				await ctx.send(self.custom_commands[name])
				return True
		return False
