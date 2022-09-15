import discord
from discord.ext import commands
from discord.commands import message_command, SlashCommandGroup
from discord.utils import get
from discord import Option

import io, contextlib, textwrap
from traceback import format_exception

from functions import getComEmbed
from checks import command_checks

AC = discord.ApplicationContext
class OwnerCog(discord.Cog):
	def __init__(self, client:commands.Bot):
		self.client = client

	class EvalView(discord.ui.View):
		def __init__(self, client:commands.Bot, cog:discord.Cog, ctx:AC, code):
			self.client = client
			self.cog = cog
			self.ctx = ctx
			self.code = code
			super().__init__()

		@discord.ui.button(label="Re-run", emoji="🔁", style=discord.ButtonStyle.green)
		async def rerun(self, button:discord.ui.Button, interaction:discord.Interaction):
			embed = await self.cog.true_eval(self.ctx, self.code)
			await interaction.response.edit_message(embed=embed)

		@discord.ui.button(label="Disable", emoji="✖️", style=discord.ButtonStyle.red)
		async def disable(self, button:discord.ui.Button, interaction:discord.Interaction):
			if await command_checks(self.ctx, self.client, user=interaction.user, is_owner=True, ephemeral=True): return
			await interaction.response.edit_message(view=None)

	@message_command(name="Eval-Rerun")
	async def _evalr(self, ctx:AC, message:discord.Message):
		if await command_checks(ctx, self.client, is_owner=True): return
		embed = await self.true_eval(ctx, clean_code(message.clean_content))
		view = self.EvalView(self.client, self, ctx, clean_code(message.clean_content))
		await ctx.respond(embed=embed, view=view)

	@message_command(name="Eval")
	async def _eval(self, ctx:AC, message:discord.Message):
		if await command_checks(ctx, self.client, is_owner=True): return
		embed = await self.true_eval(ctx, clean_code(message.clean_content))
		await ctx.respond(embed=embed)

	async def true_eval(self, ctx:AC, code):
		local_variables = { "self": self.client, "client": self.client, "ctx": ctx, "author": ctx.author, "channel": ctx.channel, "guild": ctx.guild }
		stdout = io.StringIO()
		try:
			with contextlib.redirect_stdout(stdout):
				exec(f"import discord\n\nasync def func():\n{textwrap.indent(code, '    ')}", local_variables)
				await local_variables["func"]()
				result = f"{stdout.getvalue()}"
		except Exception as e:
			result = "".join(format_exception(e, e, e.__traceback__))

		if result == "":
			return getComEmbed(ctx, self.client, content=f"Code: ```py\n{code}\n```")
		else:
			return getComEmbed(ctx, self.client, content=f"Code: ```py\n{code}\n```\nResults: ```\n{str(result)}\n```")

	ownergroup = SlashCommandGroup("owner", "Owner commands.")

	@ownergroup.command(name="guild_status", description="Change a guilds status.")
	async def guildstatus(self, ctx:AC, 
		guildid:Option(str, "ID of the guild", required=True),
		status:Option(str, "The status to set it to.", choices=["Basic","Plus"], default="Basic")
	):
		if await command_checks(ctx, self.client, is_guild=True, is_owner=True): return
		try:
			guildid = int(guildid)
		except:
			return await ctx.respond(f"`{guildid}` Is not a valid guild id")
		guild = get(self.client.guilds, id=guildid)
		if guild:
			await self.client.CON.set_value(guild, "guild_status", status, guild)
			await ctx.respond(f"Granted '{status}' status to {guild.name}!!!")
		else:
			await ctx.respond(f"Couldn't find guild with id `{guildid}` :/")

	@ownergroup.command(name="test", description="Testing")
	async def test(self, ctx:AC,
		test:Option(str, "test")
	):
		await ctx.respond(f"test: {test}")

def clean_code(content):
	if content.startswith("```") and content.endswith("```"):
		return "\n".join(content.split("\n")[1:])[:-3]
	else:
		return content

def setup(client):
	client.add_cog(OwnerCog(client))