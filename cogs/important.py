from discord.ext import commands

from functions import get_prefix, get_version, add_command, get_commands, getEmbed, Error, addField, userHasPermission, SEND_SYSTEM_MESSAGE

class ImportantCog(commands.Cog):
	def __init__(self, client):
		self.client = client

	add_command({
		"cog": "important", "category": "Important",
		"name": "help", "description": "Returns a list of most commands.",
		"arguments": [
			["command", "Get help on a spesific command", "string", False]
		],
		"level": False
	})
	@commands.command()
	async def help(self, ctx, command=None):
		prefix = get_prefix()
		commands = get_commands()
		ismod = userHasPermission(ctx.author, "kick_members") == True
		isadmin = userHasPermission(ctx.author, "administrator") == True

		if command != None:
			found = False
			for com in commands:
				if com["name"].lower() == command.lower():
					name = com["name"]
					description = com["description"]
					level = com["level"]
					args = com["arguments"]
					found = True
					break

			if found:
				if level == False or (level == "Mods" and ismod) or (level == "Admins" and isadmin):
					comtxt = prefix + command
					if args != False:
						for arg in args:
							comtxt = comtxt + f" <{arg[0]}>"
						
					txt = description
					if level:
						txt = txt + f" ({level} only)"

					if args != False:
						argtxt = ""
						for arg in args:
							argtxt = argtxt + f"`{arg[0]}`: {arg[1]} (type: {arg[2]}) (required: {str(arg[3])})\n"

					emb = getEmbed(ctx, "Help > " + prefix + command, comtxt, txt)
					if args != False:
						emb = addField(emb, "Arguments", argtxt)

					await ctx.send(embed=emb)
			else:
				await ctx.send(f"{prefix}{command} isn't a command that exists!")
		else:
			emb = getEmbed(ctx, "Help", "All commands you can use:", f"Run {prefix}help <command> to get more help on a command!")

			commandsections = ["Important", "Values", "General", "Games"]
			for sect in commandsections:
				txt = ""
				for com in commands:
					category = com["category"]
					name = com["name"]
					description = com["description"]
					level = com["level"]

					if category == sect:
						if level == False or (level == "mod" and ismod) or (level == "admin" and isadmin):
							txt = txt + f"`{prefix}{name}`: {description}"
							if level:
								txt = txt + f" ({level} only)"
							txt = txt + "\n"
					
				if txt != "":
					emb = addField(emb, sect, txt)

			await ctx.send(embed=emb)

	add_command({
		"cog": "important", "category": "Important",
		"name": "info", "description": "Returns info about the bot.",
		"arguments": False, "level": False
	})
	@commands.command()
	async def info(self, ctx):
		prefix = get_prefix()
		version = get_version()

		emb = getEmbed(ctx, "Info", "Hey, I am AidanBot, A small discord bot created by Aidan#8883 for his server that now anyone can use!", f"[Aidan's Youtube](https://www.youtube.com/c/AidanMapper)\n[Aidan's Twitter](https://twitter.com/Aid0nYT)\n[Aidan's Discord Server](https://discord.gg/KXrDUZfBpq)\n\n[Invite me to your server!](https://discord.com/api/oauth2/authorize?client_id=804319602292949013&permissions=8&scope=bot)\n[Privacy Policy](https://github.com/Aid0nModder/AidanBot/blob/main/README.md#privacy-policy)\n[Terms Of Service](https://github.com/Aid0nModder/AidanBot/blob/main/README.md#terms-of-service)\n\nIf you find a bug or he has made a typo <:AidanSmug:837001740947161168>, you can report it to Aidan on his server in one of the bot chats. You can also suggest features in the suggestion channel on his server.\n\nNote: If you are a server admin and want to setup a feature (e.g. if server invites are deleted automaticaly) use {prefix}config!")
		emb = addField(emb, "Version:", version)
		await ctx.send(embed=emb)

	add_command({
		"cog": "important", "category": "Important",
		"name": "invite", "description": "Add the bot to your server.",
		"arguments": False, "level": False
	})
	@commands.command()
	async def invite(self, ctx):
		await ctx.send("Y- you want me on your server??? I'd love too!!! https://discord.com/api/oauth2/authorize?client_id=804319602292949013&permissions=8&scope=bot")

	add_command({
		"cog": "important", "category": "Important",
		"name": "report", "description": "Report any errors or issues to aidan's system channel.",
		"arguments": [
			["message", "Message to send to Aidan.", "string", True]
		],
		"level": False
	})
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