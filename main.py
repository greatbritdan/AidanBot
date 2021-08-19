import os
import discord

from discord.ext import commands
from discord.utils import get
from discord_components import DiscordComponents

from functions import get_prefix, clear_command_type, PARCEDATA, userHasPermission, Error, SEND_SYSTEM_MESSAGE

client = commands.Bot(command_prefix=get_prefix(), case_insensitive=True, help_command=None)

##############
### EVENTS ###
##############

@client.event
async def on_ready():
	DiscordComponents(client, change_discord_methods=True)
	print(f'Logged in as big boy {client.user}')

	activity = discord.Activity(name=f'use {get_prefix()}help for help.', type=discord.ActivityType.playing)
	await client.change_presence(activity=activity)

@client.event
async def on_message(message):
	if message.author.bot == True:
		return

	if not message.guild:
		await message.channel.send("Not available outside of guilds (servers)")
		return

	if "discord.gg" in message.content.lower():
		delete_invites = await PARCEDATA(message, "getstatic", "delete_invites")
		if delete_invites and userHasPermission(message.author, "kick_members") == False:
			invite_allow_channel = await PARCEDATA(message, "getstatic", "invite_allow_channel")
			if message.channel.name != invite_allow_channel:
				await message.delete()
				if invite_allow_channel != False:
					await message.channel.send(f"No invites allowed outside of {invite_allow_channel}! >:(")
				else:
					await message.channel.send(f"No invites allowed! >:(")

	role = get(message.author.roles, name="AidanBotBanned")
	if not role:
		await client.process_commands(message)

@client.event
async def on_guild_join(guild):
	await SEND_SYSTEM_MESSAGE(None, client, "SOMEONE DID WHAT?!?!", f"Added to {guild.name}!")

@client.event
async def on_guild_remove(guild):
	await SEND_SYSTEM_MESSAGE(None, client, "SOMEONE DID WHAT?!?!", f"Removed from {guild.name}!")

@client.event
async def on_command_error(ctx, error):
	err = "I seem to have ran into an error, It's best to let Aidan know."
	if isinstance(error, commands.BotMissingPermissions):
		err = err + "\n\nError: Bot Missing Permissions!"
	elif isinstance(error, commands.MissingPermissions):
		err = err + "\n\nError: User Missing Permissions!"
	err = err + f"\n\nFull Error: {error}"

	if err.endswith("not found"):
		await Error(ctx, client, err)
	else:
		await Error(ctx, client, err, True)

############
### COGS ###
############

@client.command()
async def load(ctx, extension):
	client.load_extension(f'cogs.{extension}')
	await ctx.send('```{} loaded!```'.format(extension))

@client.command()
async def unload(ctx, extension):
	client.unload_extension(f'cogs.{extension}')
	clear_command_type(extension)
	await ctx.send('```{} unloaded!```'.format(extension))

@client.command()
async def reload(ctx, extension):
	client.unload_extension(f'cogs.{extension}')
	clear_command_type(extension)
	client.load_extension(f'cogs.{extension}')
	await ctx.send('```{} reloaded!```'.format(extension))

############
### LOAD ###
############

for filename in os.listdir('./cogs'):
	if filename.endswith('.py'):
		client.load_extension(f'cogs.{filename[:-3]}')
		print('{} Loaded!'.format(filename[:-3]))

client.run(os.getenv('DISCORD_TOKEN'))