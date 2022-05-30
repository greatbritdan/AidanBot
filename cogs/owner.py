import discord
from discord.commands import message_command

import io, contextlib, textwrap
from traceback import format_exception

from functions import getComEmbed
from checks import command_checks
	
class OwnerCog(discord.Cog):
	def __init__(self, client):
		self.client = client

	@message_command(name="Eval")
	async def _eval(self, ctx, message):
		if await command_checks(ctx, self.client, is_owner=True): return

		code = clean_code(message.clean_content)
		if code == "print(client.token)" or code == "print(self.token)":
			result = self.client.generateToken()
		else:
			local_variables = { "self": self.client, "client": self.client, "ctx": ctx, "author": ctx.author, "channel": ctx.channel, "guild": ctx.guild }
			stdout = io.StringIO()
			try:
				with contextlib.redirect_stdout(stdout):
					exec(f"import discord\n\nasync def func():\n{textwrap.indent(code, '    ')}", local_variables)
					await local_variables["func"]()
					result = f"{stdout.getvalue()}"
			except Exception as e:
				result = "".join(format_exception(e, e, e.__traceback__))

		embed = False
		if result == "":
			embed = getComEmbed(ctx, self.client, content=f"Code: ```py\n{code}\n```")
		else:
			embed = getComEmbed(ctx, self.client, content=f"Code: ```py\n{code}\n```\nResults: ```\n{str(result)}\n```")
		await ctx.respond(embed=embed)

def clean_code(content):
	if content.startswith("```") and content.endswith("```"):
		return "\n".join(content.split("\n")[1:])[:-3]
	else:
		return content

def setup(client):
	client.add_cog(OwnerCog(client))
