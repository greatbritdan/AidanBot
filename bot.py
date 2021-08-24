import discord
from discord.ext import commands
from discord_components import DiscordComponents

import os
from functions import get_prefix

intents = discord.Intents.all()
client = commands.Bot(command_prefix=get_prefix(), case_insensitive=True, help_command=None, intents=intents)
DiscordComponents(client)

@client.event
async def on_ready():
	print(f'Hello there {client.user}')

	activity = discord.Activity(name=f'use {get_prefix()}help for help.', type=discord.ActivityType.playing)
	await client.change_presence(activity=activity)

for filename in os.listdir('./cogs'):
	if filename.endswith('.py'):
		client.load_extension(f'cogs.{filename[:-3]}')
		print('{} Loaded!'.format(filename[:-3]))

client.run(os.getenv('DISCORD_TOKEN'))