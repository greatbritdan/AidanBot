from discord.ext import commands

import random

from functions import get_prefix, get_version, getEmbed, addField, Error, userHasPermission

class ImportantCog(commands.Cog):
	def __init__(self, client):
		self.client = client

	@commands.command(description="Get help on a command or spesific command")
	async def help(self, ctx, command=None):
		prefix = get_prefix()

		# Get help on a spesific command
		if command != None:
			for com in self.client.commands:
				if com.name.lower() == command.lower():
					await com.can_run(ctx)

					if (not com.hidden) and com.enabled:
						comtxt = f"{prefix}{com.name}"

						args = dict(com.clean_params)
						if len(args) > 0:
							for arg in args:
								comtxt = comtxt + f" <{arg}>"

						emb = getEmbed(ctx, f"Help > {prefix}{com.name}", comtxt, com.description.format(prefix=prefix))

						await ctx.reply(embed=emb, mention_author=False)
						break
		else:
			# Get all visible commands
			emb = getEmbed(ctx, "Help", "All commands you can use:", f"Run {prefix}help <command> to get more help on a command!")

			cognames = ["ImportantCog", "GeneralCog", "FightCog", "StatsCog", "PPCog", "OwnerCog"]
			neatcognames = ["Important", "General", "Fight", "Stats", "Pip0n's Palace Only", "Owner Only"]
			for cog in cognames:
				txt = ""
				for com in self.client.commands:
					try:
						await com.can_run(ctx)
					except:
						continue

					if (not com.hidden) and com.enabled and com.cog_name == cog:
						desc = com.description or "Nil"
						if "\n" in desc:
							lines = desc.splitlines()
							desc = lines[0]
								
						txt = txt + f"`{prefix}{com.name}`: {desc}\n"

				if txt != "":
					emb = addField(emb, neatcognames[cognames.index(cog)], txt, False)

			await ctx.reply(embed=emb, mention_author=False)

	@commands.command(description="Get info on the bot.")
	async def info(self, ctx):
		emb = getEmbed(ctx, "Info", "Hey, I am AidanBot, A small discord bot created by Aidan#8883 for his server that now anyone can use!", f"[Aidan's Youtube](https://www.youtube.com/c/AidanMapper)\n[Aidan's Twitter](https://twitter.com/Aid0nYT)\n[Aidan's Discord Server](https://discord.gg/KXrDUZfBpq)\n\n[Invite me to your server!](https://discord.com/api/oauth2/authorize?client_id=804319602292949013&permissions=8&scope=bot)\n[Privacy Policy](https://github.com/Aid0nModder/AidanBot/blob/main/README.md#privacy-policy)\n[Terms Of Service](https://github.com/Aid0nModder/AidanBot/blob/main/README.md#terms-of-service)\n\nIf you find a bug or he has made a typo <:AidanSmug:837001740947161168>, you can report it to Aidan on his server in one of the bot chats. You can also suggest features in the suggestion channel on his server.")
		emb = addField(emb, "Version:", get_version())
		await ctx.reply(embed=emb, mention_author=False)

	@commands.command(description="Invite me to your server")
	async def invite(self, ctx):
		await ctx.reply("Y- you want me on your server??? I'd love too!!! https://discord.com/api/oauth2/authorize?client_id=804319602292949013&permissions=8&scope=bot", mention_author=False)

	@commands.command(description="Get any role that starts with [r].\n\nIf you have `manage roles` you can add any role up to your highest.")
	async def role(self, ctx, *, name=None):
		if name == None:
			await Error(ctx, self.client, "Missing un-optional argument for command.")
			return

		r = None
		for role in ctx.guild.roles:
			if name.lower() in role.name.lower():
				r = role
				break

		if r == None:
			await ctx.reply("Try again, i couldn't find this role.", mention_author=False)
			return

		if userHasPermission(ctx.author, "manage_roles") or r.name.startswith("[r]"):
			if r == ctx.author.top_role:
				await ctx.reply(f"You can't remove your top role", mention_author=False)
				return
			
			if r in ctx.author.roles:
				await ctx.author.remove_roles(r)
				await ctx.reply(f"Removed {r.name}", mention_author=False)
			else:
				await ctx.author.add_roles(r)
				await ctx.reply(f"Added {r.name}", mention_author=False)
		else:
			await ctx.reply(f"{r.name} is not a role that can be added by anyone", mention_author=False)

	@commands.command(hidden=True)
	async def bucket(self, ctx):
		urls = ["https://cdn.discordapp.com/attachments/880033942420484157/882333690410197062/cd804_y_bucket-blue.webp", "https://cdn.discordapp.com/attachments/880033942420484157/882333693094547566/cd805_y_bucket-yellow.webp", "https://cdn.discordapp.com/attachments/880033942420484157/882333695162343424/cd807_y_bucket-red.webp"]

		emb = getEmbed(ctx, "Bucket", "Buket", "", False, False)
		emb.set_image(url=random.choice(urls))
		await ctx.send(embed=emb)

def setup(client):
  client.add_cog(ImportantCog(client))