import discord
from discord.ext import commands
from discord.utils import find

import randfacts, asyncio
from random import randint

from functions import ComError

class GeneralCog(commands.Cog):
	def __init__(self, client):
		self.client = client

	@commands.command(aliases=["roles"])
	@commands.cooldown(1, 5)
	async def role(self, ctx):
		roles = []
		for role in ctx.guild.roles:
			if role.name.startswith("[r]"):
				roles.append(role)
		if len(roles) == 0:
			return await ctx.reply("No roles have been set up, consider asking an Admin as there may be another bot in charge of roles!", mention_author=False)
		
		options = []
		for role in roles:
			options.append(discord.SelectOption(label=role.name))

		def getButtons(disable=False):
			return discord.ui.View(discord.ui.Select(placeholder="Choose Roles", options=options, disabled=disable, custom_id="select", min_values=0, max_values=len(options)))

		MSG = await ctx.reply("Choose your roles: (Roles that aren't seleted will be removed if you have them)", mention_author=False, view=getButtons(False))

		def check(interaction):
			return (interaction.user.id == ctx.author.id and interaction.message.id == MSG.id)

		try:
			interaction = await self.client.wait_for("interaction", timeout=60, check=check)

			if interaction.data["custom_id"] == "select":
				changes = []
				for role in roles:
					if role.name in interaction.data["values"] and role not in ctx.author.roles:
						await ctx.author.add_roles(role)
						changes.append(f"Added {role.name}")
					elif role.name not in interaction.data["values"] and role in ctx.author.roles:
						await ctx.author.remove_roles(role)
						changes.append(f"Removed {role.name}")

				if len(changes) > 0:
					await MSG.edit(", ".join(changes), view=getButtons(True))
				else:
					await MSG.edit("No changes made.", view=getButtons(True))

		except asyncio.TimeoutError:
			await MSG.edit("[ Timeout ]", view=getButtons(True))		
		
	@commands.command()
	@commands.cooldown(1, 5)
	async def react(self, ctx, reaction:str="👋", message_id:int=None):
		if not ctx.channel.permissions_for(ctx.author).add_reactions:
			return await ctx.send(f"You don't have permission scrubb :sunglasses: (Missing add_reactions)")

		MSG = ""
		if message_id:
			MSG = await ctx.channel.fetch_message(message_id)
		else:
			yes = False
			async for message in ctx.channel.history(limit=2):
				if yes:
					MSG = message
				else:
					yes = True

		await ctx.message.delete()
		await MSG.add_reaction(reaction)

	@commands.command()
	@commands.cooldown(1, 5)
	@commands.bot_has_permissions(manage_webhooks=True)
	async def clone(self, ctx, name, *, message):
		if message.startswith(self.client.getprefix(None, ctx.message)):
			await ComError(ctx, self.client, "No running commands in clone.")
			return

		extra = {
			"Alesan99": "https://cdn.discordapp.com/attachments/885203191485050941/916394696350236712/Alesannew.png",
			"(fake)": "https://cdn.discordapp.com/attachments/896833918685306891/916400101533040700/fake.png",
			"Pip0n": "https://cdn.discordapp.com/attachments/885203191485050941/916738423467958312/Pip0n.png",
			"Box": "https://cdn.discordapp.com/attachments/885203191485050941/916738620730277888/Box.png",
			"GentleGoombot": "https://cdn.discordapp.com/attachments/836991509571567638/952190238686588988/gentleGoombotLivesInOurHearts.png"
		}

		temp = None
		for nam in extra:
			if name.lower() == nam.lower() or name.lower() in nam.lower():
				temp = {
					"name": nam,
					"pfp": extra[nam]
				}
				break
		if not temp:
			member = ctx.guild.get_member_named(name)
			if not member:
				member = find(lambda m: name.lower() in m.display_name.lower(), ctx.guild.members)
			if not member:
				member = find(lambda m: name.lower() in m.name.lower(), ctx.guild.members)
			if member:
				temp = {
					"name": member.display_name,
					"pfp": member.display_avatar.url
				}

		if temp:
			hook = ""
			for w in await ctx.channel.webhooks():
				if w.name == "AidanBotCloneHook":
					hook = w
			if not hook:
				hook = await ctx.channel.create_webhook(name="AidanBotCloneHook")

			await hook.send(message, username=temp["name"] + " (fake)", avatar_url=temp["pfp"])
		else:
			await ComError(ctx, self.client, f"Member '{name}' not found.")
			return

	@commands.command()
	@commands.cooldown(1, 5)
	async def punish(self, ctx):
		texts = ["AAAAAAAAAAAAHHHHHHH!!!!!","AAAHH PLEASE STO-P!!!!","I'M SORRY AAHHH!!!","PLEASE!... HAVE MERCY!...","STOP...   *CRIES*","AAAAAAHHHH!!!","I'M SO SORRY.AAA!!!"]
		text = texts[randint(0, len(texts)-1)]
		await ctx.send("**" + text + "**")

	@commands.command()
	@commands.cooldown(1, 5)
	async def fact(self, ctx):
		fact = randfacts.get_fact()
		await ctx.send(f"Did you know, {fact}")

def setup(client):
	client.add_cog(GeneralCog(client))
