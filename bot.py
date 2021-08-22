import os
from discord.ext import commands

from discord_components import DiscordComponents

from functions import get_prefix, clear_command_type

client = commands.Bot(command_prefix=get_prefix(), case_insensitive=True, help_command=None)
DiscordComponents(client)

### COGS ###

@client.command()
async def load(ctx, extension):
	client.load_extension(f'cogs.{extension}')
	await ctx.send('```{} loaded!```'.format(extension))

@client.command()
async def unload(ctx, extension):
	client.unload_extension(f'cogs.{extension}')
	if extension != "events":
		clear_command_type(extension)
	await ctx.send('```{} unloaded!```'.format(extension))

@client.command()
async def reload(ctx, extension):
	client.unload_extension(f'cogs.{extension}')
	if extension != "events":
		clear_command_type(extension)
	client.load_extension(f'cogs.{extension}')
	await ctx.send('```{} reloaded!```'.format(extension))

### LOAD ###

for filename in os.listdir('./cogs'):
	if filename.endswith('.py'):
		client.load_extension(f'cogs.{filename[:-3]}')
		print('{} Loaded!'.format(filename[:-3]))

client.run(os.getenv('DISCORD_TOKEN'))
