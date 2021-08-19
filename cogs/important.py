from discord.ext import commands

import asyncio

from functions import get_prefix, get_version, add_command, get_commands, getEmbed, Error, addField, userHasPermission, SEND_SYSTEM_MESSAGE

class ImportantCog(commands.Cog):
	def __init__(self, client):
		self.client = client

	# cogname, category name, command name, command description, locked role
	add_command(["important", "Important", "Help", "Returns a list of most commands.", False])
	@commands.command()
	async def help(self, ctx):
		prefix = get_prefix()
		commands = get_commands()
		commandsections = ["Important", "Values", "General", "Games"]

		ismod = userHasPermission(ctx.author, "kick_members") == True
		isadmin = userHasPermission(ctx.author, "administrator") == True

		emb = getEmbed(ctx, "Help", "All commands you can use:", "")

		for sect in commandsections:
			txt = ""
			for com in commands:
				if com[1] == sect:
					if com[4] == False or (com[4] == "mod" and ismod) or (com[4] == "admin" and isadmin):
						txt = txt + f"`{prefix}{com[2]}`: {com[3]}"
						if com[4] == "mod":
							txt = txt + " (Mods only)"
						if com[4] == "admin":
							txt = txt + " (Admins only)"
						txt = txt + "\n"
                
			if txt != "":
				emb = addField(emb, sect, txt)

		await ctx.send(embed=emb)

	add_command(["important", "Important", "info", "Returns info about the bot.", False])
	@commands.command()
	async def info(self, ctx):
		prefix = get_prefix()
		version = get_version()

		emb = getEmbed(ctx, "Info", "Hey, I am AidanBot, A small discord bot created by Aidan#8883 for his server that now anyone can use!", f"[Aidan's Youtube](https://www.youtube.com/c/AidanMapper)\n[Aidan's Twitter](https://twitter.com/Aid0nYT)\n[Aidan's Discord Server](https://discord.gg/KXrDUZfBpq)\n[Invite me to your server!](https://discord.com/api/oauth2/authorize?client_id=804319602292949013&permissions=8&scope=bot)\n\nIf you find a bug or he has made a typo <:AidanSmug:837001740947161168>, you can report it to Aidan on his server in one of the bot chats. You can also suggest features in the suggestion channel on his server.\n\nNote: If you are a server admin and want to setup a feature (e.g. if server invites are deleted automaticaly) use {prefix}config!")
		emb = addField(emb, "Version:", version)
		await ctx.send(embed=emb)

	add_command(["important", "Important", "invite", "Add the bot to your server.", False])
	@commands.command()
	async def invite(self, ctx):
		await ctx.send("Y- you want me on your server??? I'd love too!!! https://discord.com/api/oauth2/authorize?client_id=804319602292949013&permissions=8&scope=bot")

	add_command(["important", "Important", "lockdown", "Delete all invites.", "admin"])
	@commands.command()
	@commands.has_permissions(administrator=True)
	async def lockdown(self, ctx):
		for invite in await ctx.guild.invites():
			await invite.delete()

		emb = getEmbed(ctx, "Lockdown", ":lock: **!Lockdown!** :lock:", "The owner has decided to lockdown the server! All invites have been deleted, no one can join so be careful not to leave by accident.", False, True)
		await ctx.send(embed=emb)

	add_command(["important", "Important", "report", "Report any errors or issues to aidan's system channel.", False])
	@commands.command()
	async def report(self, ctx, *, message:str=None):
		if message == None:
			await Error(ctx, self.client, "Missing un-optional argument for command.")
			return

		prefix = get_prefix()
		await SEND_SYSTEM_MESSAGE(ctx, self.client, f"Someone use the {prefix}report command!", message)
		await ctx.send("sent!")

def setup(client):
  client.add_cog(ImportantCog(client))