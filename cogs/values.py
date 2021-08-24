from discord.ext import commands

from functions import add_command, get_prefix, PARCEDATA, CREATEDATA, DELETEDATA, getEmbed

class ValuesCog(commands.Cog):
	def __init__(self, client):
		self.client = client

	add_command({
		"cog": "values", "category": "Values",
		"name": "setup", "description": "Sets up server data that holds server values.",
		"arguments": False, "level": "Admins"
	})
	@commands.command()
	@commands.has_permissions(administrator=True)
	async def setup(self, ctx):
		succ = await CREATEDATA(ctx, self.client)
		if succ:
			prefix = get_prefix()
			await ctx.send(f"Created! run {prefix}unsetup to delete your data at any time.")

	add_command({
		"cog": "values", "category": "Values",
		"name": "unsetup", "description": "Removes server data that holds server values.",
		"arguments": False, "level": "Admins"
	})
	@commands.command()
	@commands.has_permissions(administrator=True)
	async def unsetup(self, ctx):
		succ = await DELETEDATA(ctx.guild.id, ctx, self.client)
		if succ:
			prefix = get_prefix()
			await ctx.send(f"Deleted! run {prefix}setup to set it up again at any time.")

	add_command({
		"cog": "values", "category": "Values",
		"name": "config", "description": "Configure server values.\n\n`config list`: view all values.\n`config get <name>`: view a value.\n`config set <name> <val>`: set a value.",
		"arguments": [
			["action", "What action you are performing.", "set/get/list", True],
			["name", "Name of the value you are getting of setting.", "string", "only if get/set"],
			["val", "What you aresetting it to.", "string/bool", "only if set"]
		],
		"level": "Admins"
	})
	@commands.command()
	@commands.has_permissions(administrator=True)
	async def config(self, ctx, action=None, name=None, val=None):
		if action == "list":
			data = await PARCEDATA(ctx, self.client, "list")
			if data:
				txt = ""
				for d in data:
					txt = txt + f"`{d}`: {data[d]}\n"

				emb = getEmbed(ctx, "Config", "", txt)
				await ctx.send(embed=emb)
				return

		elif action == "get" and name:
			val = await PARCEDATA(ctx, self.client, "get", name)
			if val:
				emb = getEmbed(ctx, "Config", "", f"`{name}` is currently set to {val}!")
				await ctx.send(embed=emb)
				return

		elif action == "set" and name and val:
			suc = await PARCEDATA(ctx, self.client, "set", name, val)
			if suc:
				emb = getEmbed(ctx, "Config", "", f"`{name}` was set to {val}!")
				await ctx.send(embed=emb)
				return

		await ctx.send(f"{name} was not found!")

def setup(client):
  client.add_cog(ValuesCog(client))