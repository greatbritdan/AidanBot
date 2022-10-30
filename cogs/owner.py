import discord
import discord.ext.commands as CM
import discord.app_commands as AC
from discord import Interaction as Itr

import io, contextlib, textwrap
from traceback import format_exception

from aidanbot import AidanBot
from functions import getComEmbed
from checks import ab_check, ab_check_slient

class OwnerCog(CM.Cog):
	def __init__(self, client:AidanBot):
		self.client = client

		self.eval = AC.ContextMenu(name="Eval", callback=self._eval)
		self.client.tree.add_command(self.eval, guilds=self.client.debug_guilds)

		self.evalrerun = AC.ContextMenu(name="Eval-rerun", callback=self._evalr)
		self.client.tree.add_command(self.evalrerun, guilds=self.client.debug_guilds)

	async def cog_unload(self):
		self.client.tree.remove_command(self.eval.name, type=self.eval.type)
		self.client.tree.remove_command(self.evalrerun.name, type=self.evalrerun.type)

	class EvalView(discord.ui.View):
		def __init__(self, client:AidanBot, cog:CM.Cog, code:str, messageid:int):
			self.client = client
			self.cog = cog
			self.code = code
			self.messageid = messageid
			super().__init__()

		@discord.ui.button(label="Re-run", emoji="🔁", style=discord.ButtonStyle.gray)
		async def rerun(self, itr:Itr, _):
			message = await itr.channel.fetch_message(self.messageid)
			self.code = clean_code(message.clean_content)
			embed = await self.cog.true_eval(itr, self.code)
			await itr.response.edit_message(embed=embed)

		@discord.ui.button(label="Disable", emoji="🇽", style=discord.ButtonStyle.gray)
		async def disable(self, itr:Itr, _):
			if not await ab_check_slient(itr, self.client, user=itr.user, is_owner=True):
				embed = await self.cog.true_eval(itr, self.code, "Only Aidan can end this Eval!")
				await itr.response.edit_message(embed=embed)
				return
			await itr.response.edit_message(view=None)

	async def true_eval(self, itr:Itr, code, title=None):
		local_variables = { "self": self.client, "client": self.client, "interaction": itr, "user": itr.user, "author": itr.user, "channel": itr.channel, "guild": itr.guild }
		stdout = io.StringIO()
		try:
			with contextlib.redirect_stdout(stdout):
				exec(f"import discord\n\nasync def func():\n{textwrap.indent(code, '    ')}", local_variables)
				await local_variables["func"]()
				result = f"{stdout.getvalue()}"
		except Exception as e:
			result = "".join(format_exception(e, e, e.__traceback__))

		if result == "":
			return getComEmbed(str(itr.user), self.client, title=title, content=f"Code: ```py\n{code}\n```")
		else:
			return getComEmbed(str(itr.user), self.client, title=title, content=f"Code: ```py\n{code}\n```\nResults: ```\n{str(result)}\n```")

	async def _evalr(self, itr:Itr, message:discord.Message):
		if not await ab_check(itr, self.client, is_owner=True):
			return
		embed = await self.true_eval(itr, clean_code(message.clean_content))
		view = self.EvalView(self.client, self, clean_code(message.clean_content), message.id)
		await itr.response.send_message(embed=embed, view=view)

	async def _eval(self, itr:Itr, message:discord.Message):
		if not await ab_check(itr, self.client, is_owner=True):
			return
		embed = await self.true_eval(itr, clean_code(message.clean_content))
		await itr.response.send_message(embed=embed, ephemeral=True)

def clean_code(content):
	if content.startswith("```") and content.endswith("```"):
		return "\n".join(content.split("\n")[1:])[:-3]
	else:
		return content

async def setup(client:AidanBot):
	await client.add_cog(OwnerCog(client), guilds=client.debug_guilds)