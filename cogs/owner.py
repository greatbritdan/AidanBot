import discord
from discord.commands import SlashCommandGroup
from discord import Option

import io, contextlib, textwrap
from traceback import format_exception

from functions import getComEmbed
from checks import command_checks

def tobool(val):
	if val.lower() == "true":
		return True
	return False
	
class OwnerCog(discord.Cog):
	def __init__(self, client):
		self.client = client

	class EvalModal(discord.ui.Modal):
		def __init__(self, client, template):
			self.client = client
			super().__init__(title="Eval", custom_id="eval")

			txt = ""
			if template == "utils.get":
				txt = 'from discord.utils import get\nguild = get(client.guilds, name="name_here")'
			if template == "embed":
				txt = 'from functions import getComEmbed\nemb = getComEmbed(ctx, client, "Amgous", "Sussy")\nawait ctx.send(embed=emb)'
			self.add_item(discord.ui.InputText(style=discord.InputTextStyle.long, label="Code:", placeholder="print('Hello World!')", value=txt, required=True))
		async def callback(self, interaction):
			await interaction.response.send_message("Working...")

	ownergroup = SlashCommandGroup("owner", "Owner commands.")
	@ownergroup.command(name="eval", description="For running python code in discord.")
	async def eval(self, ctx,
		message_id:Option(str, description="Message id of the code you want to run.", required=False),
		template:Option(str, "Template code", choices=["None","utils.get","embed"], default="None"),
		respond:Option(str, "If it responds after the code has finished running.", choices=["True","False"], default="True"),
		ephemeral:Option(str, "If the code can be seen by just you or not.", choices=["True","False"], default="False")
	):
		if await command_checks(ctx, self.client, is_owner=True): return
		
		respond, ephemeral = tobool(respond), tobool(ephemeral)
		code = False
		if message_id:
			try:
				message_id = int(message_id)
				message = await ctx.channel.fetch_message(message_id)
				if message:
					code = clean_code(message.clean_content)
			except:
				return
		else:
			await ctx.send_modal(self.EvalModal(self.client, template))
			interaction = await self.client.wait_for("interaction")
			try:
				code = interaction.data["components"][0]["components"][0]["value"]
				await interaction.delete_original_message()
			except:
				return

		local_variables = { "client": self.client, "ctx": ctx, "author": ctx.author, "channel": ctx.channel, "guild": ctx.guild }
		stdout, iserror = io.StringIO(), False
		try:
			with contextlib.redirect_stdout(stdout):
				exec(f"import discord\n\nasync def func():\n{textwrap.indent(code, '    ')}", local_variables)
				await local_variables["func"]()
				result = f"{stdout.getvalue()}"
		except Exception as e:
			result = "".join(format_exception(e, e, e.__traceback__))
			iserror = True
		if iserror or respond:
			embed = False
			if result == "":
				embed = getComEmbed(ctx, self.client, content=f"Code: ```py\n{code}\n```")
			else:
				embed = getComEmbed(ctx, self.client, content=f"Code: ```py\n{code}\n```\nResults: ```\n{str(result)}\n```")
			await ctx.respond(embed=embed, ephemeral=ephemeral)

def clean_code(content):
	if content.startswith("```") and content.endswith("```"):
		return "\n".join(content.split("\n")[1:])[:-3]
	else:
		return content

def setup(client):
	client.add_cog(OwnerCog(client))