import os

import discord
from discord.ext import commands
from discord.utils import get

from functions import get_prefix

intents = discord.Intents.all()
client = commands.Bot(command_prefix=get_prefix(), case_insensitive=True, help_command=None, intents=intents)

@client.event
async def on_ready():
	print(f'Logged in as {client.user}')

	await client.change_presence(activity=discord.Activity(name=f'use {get_prefix()}help for help.',type=discord.ActivityType.playing))

## Archive Coolguy's Community hub messages, due to recent ghost pings ##
@client.event
async def on_message(message):
	if message.guild.id == 754952103381696656:
		guild = get(client.guilds, id=879063875469860874)
		channel = get(guild.text_channels, id=886191398259392512)

		await channel.send(f"From `{message.author.name}` in `#{message.channel.name}`:  {message.content}")

for filename in os.listdir('./cogs'):
	if filename.endswith('.py'):
		client.load_extension(f'cogs.{filename[:-3]}')
		print('{} Loaded!'.format(filename[:-3]))

client.run(os.getenv('DISCORD_TOKEN'))
