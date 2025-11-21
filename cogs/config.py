import discord
import discord.ext.commands as CM
import discord.app_commands as AC
from discord import Interaction as Itr

from typing import Literal

from aidanbot import AidanBot
from utils.config import ConfigManager
from utils.functions import getComEmbed
from utils.checks import ab_check

class ConfigCore(CM.Cog):
	def __init__(self, client:AidanBot):
		self.client = client

	configgroup = AC.Group(name="config", description="Commands to do with configeration.")
	
	@configgroup.command(name="guild", description="Guild configerations.")
	@AC.describe(action="Config action.", name="Variable you're performing action on.", value="New value for this variable.")
	async def guildconfig(self, itr:Itr, action:Literal["List","Set","Reset","Info","Raw"], name:str=None, value:str=None):
		if itr.guild.id != self.client.revival_guild:
			await itr.response.send_message(ephemeral=True,content="I have only come back online for the celebration of Pip0n's Palace before it's shutdown, I am very much still deprecated and have not returned. Thank you for keeping me around!")
			return
		
		if not await ab_check(itr, self.client, is_guild=True, has_mod_role=True):
			return
		if name and name not in self.client.CON.valid_values:
			name = False
		await self.config_command(itr, self.client.CON, itr.guild, action, name, value)

	@guildconfig.autocomplete("name")
	async def guildconfig_name(self, itr:Itr, current:str):
		return [AC.Choice(name=val, value=val) for val in self.client.CON.valid_values if current.lower() in val.lower() and not self.client.CON.is_restricted(val.lower())][:25]

	@configgroup.command(name="user", description="User configerations.")
	@AC.describe(action="Config action.", name="Variable you're performing action on.", value="New value for this variable.")
	async def userconfig(self, itr:Itr, action:Literal["List","Set","Reset","Info","Raw"], name:str=None, value:str=None):
		if itr.guild.id != self.client.revival_guild:
			await itr.response.send_message(ephemeral=True,content="I have only come back online for the celebration of Pip0n's Palace before it's shutdown, I am very much still deprecated and have not returned. Thank you for keeping me around!")
			return
		
		if name and name not in self.client.UCON.valid_values:
			name = False
		await self.config_command(itr, self.client.UCON, itr.user, action, name, value)

	@userconfig.autocomplete("name")
	async def userconfig_name(self, itr:Itr, current:str):
		return [AC.Choice(name=val, value=val) for val in self.client.UCON.valid_values if current.lower() in val.lower() and not self.client.UCON.is_restricted(val.lower())][:25]
	
	async def config_command(self, itr:Itr, CON:ConfigManager, obj, action="List", name:str=None, value=None):
		command = "Config (Guild)"
		if CON.type == "user":
			command = "Config (User)"
		values = CON.get_group(obj)
		embed = False

		if action == "List":
			txt = ""
			for name in values:
				if CON.is_restricted(name) != True:
					txt += f"\n**\\- {name}:** {CON.display_value(name, CON.get_value(obj, name, itr.guild))}"
			embed = getComEmbed(self.client, f"All values for {obj.name}:", txt, command=command, footer=f"{len(values)} Options")
		elif action == "Info" and name:
			truename = name.split("_")
			truename = " ".join([n.capitalize() for n in truename])
			truetype = CON.type_values[name] # font
			if CON.stackable_values[name]:
				truetype = f"{truetype} (Stackable)"
			truetype = f"**{truetype}**"
			example = f"`/config guild action:Set name:{name} value:{CON.get_example(name)}`"

			fields = [
				["Current Value:", CON.display_value(name, CON.get_value(obj, name, itr.guild))],
				["Type:",          truetype],
				["Default Value:", CON.display_value(name, CON.default_values[name])],
				["Example:",       example],
			]
			if CON.option_values[name]:
				fields.append(["Options:", f"`{', '.join(CON.option_values[name])}`"])
				
			embed = getComEmbed(self.client, f"Info on {truename} ({name})", CON.desc_values[name], command=command, fields=fields)
		elif action == "Raw" and name:
			txt = f"```{CON.raw_value(name, values[name])}```"
			embed = getComEmbed(self.client, f"Raw of {name}:", txt, command=command)
		elif action == "Reset" and name:
			await CON.reset_value(obj, name)
			embed = getComEmbed(self.client, content=f"Reset {name} to `{CON.default_values[name]}`!", command=command)
		elif action == "Set" and name and value:
			_, error = await CON.set_value(obj, name, value, itr.guild)
			if error:
				embed = getComEmbed(self.client, content=error, command=command)
			else:
				val = CON.get_value(obj, name, itr.guild)
				embed = getComEmbed(self.client, content=f"Set {name} to {CON.display_value(name, val)}!", command=command)
		else:
			return await itr.response.send_message("Seems like you're missing some arguments, or inputed an incorrect one. Try again.")
		await itr.response.send_message(embed=embed)

async def setup(client:AidanBot):
	await client.add_cog(ConfigCore(client), guilds=client.debug_guilds)