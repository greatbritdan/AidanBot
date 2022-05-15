import discord
from discord.utils import get

import json
with open('./data/values.json') as file:
	VALUES = json.load(file)
with open('./data/uservalues.json') as file:
	UAVALUES = json.load(file)

# MANAGES CONFGERATION #

class ConfigManager():
	def __setitem__(self, key, value):
		setattr(self, key, value)
	def __getitem__(self, key):
		return getattr(self, key)

	def __init__(self, client, ctype):
		self.client = client
		self.type = ctype

		self.values = {}
		self.valid_values = []
		self.default_values = {}
		self.desc_values = {}
		self.type_values = {}
		self.restrict_values = {}

		list = None
		if self.type == "guild":
			self.logname = "logs"
			list = VALUES
		if self.type == "user":
			self.logname = "user-logs"
			list = UAVALUES

		for val in list:
			self.valid_values.append(val)
			self.default_values[val] = list[val]["default"]
			self.desc_values[val] = list[val]["help"]
			self.type_values[val] = list[val]["type"]
			if "restricted" in list[val]:
				self.restrict_values[val] = list[val]["restricted"]
			else:
				self.restrict_values[val] = False

	async def ready(self):
		await self.values_msgupdate("load")

	# load or save the json file
	async def values_msgupdate(self, typ):
		guild = get(self.client.guilds, id=879063875469860874)
		channel = get(guild.channels, name=self.logname)
		message = await channel.fetch_message(channel.last_message_id)
		if typ == "load":
			byte = await message.attachments[0].read()
			txt = byte.decode("utf-8")
			self.values = json.loads(txt)
		elif typ == "save":
			await message.delete()
			with open("temp.json", "w") as f:
				json.dump(self.values, f, indent=4)
			await channel.send(file=discord.File("temp.json", "values.json"))

	def tonumber(self, val):
		try:
			return int(val)
		except ValueError:
			return False

	# new lol!

	def fix_model(self, obj): # if values or group is missing it'll fill out the list
		id = str(obj.id)
		if id not in self.values or self.values[id] == None:
			self.values[id] = {}
		for name in self.default_values:
			if name not in self.values[id]:
				self.values[id][name] = self.default_values[name]

	def exists(self, name):
		return (name in self.valid_values)
	def get_help(self, name):
		return self.desc_values[name]
	def get_type(self, name):
		return self.type_values[name]
	def is_restricted(self, name):
		if self.restrict_values[name]:
			return True
		return False
		
	async def remove_group(self, obj):
		if str(obj.id) in self.values:
			self.values.pop(str(obj.id))
			await self.values_msgupdate("save")
			return True
		return False
	def get_group(self, obj):
		self.fix_model(obj)
		return self.values[str(obj.id)]

	def get_value(self, obj, name, guild=None):
		self.fix_model(obj)
		val = self.values[str(obj.id)][name]
		if self.get_type(name) == "channel":
			return get(guild.channels, id=val)
		elif self.get_type(name) == "role":
			return get(guild.roles, id=val)
		else:
			return val
	async def set_value(self, obj, name, val, guild=None, noupdate=False):
		result = self._set_value(obj, name, val, guild)
		if result and (not noupdate):
			await self.values_msgupdate("save")
		return result
	def _set_value(self, obj, name, val, guild):
		self.fix_model(obj)
		if type(val) == str:
			val = val.lower()

		if (self.get_type(name) == "channel" or self.get_type(name) == "role") and (val == "false" or val == "none"):
			self.values[str(obj.id)][name] = False
			return True

		if self.get_type(name) == "channel":
			newval = self.tonumber(val)
			channel = None
			if newval:
				channel = get(guild.channels, id=newval)
			else:
				channel = get(guild.channels, name=val)
			if channel:
				self.values[str(obj.id)][name] = channel.id
				return True
			return False

		elif self.get_type(name) == "role":
			newval = self.tonumber(val)
			role = None
			if newval:
				role = get(guild.roles, id=newval)
			else:
				role = get(guild.roles, name=val)
			if role:
				self.values[str(obj.id)][name] = role.id
				return True
			return False
		
		elif self.get_type(name) == "boolean":
			if val == "true":
				self.values[str(obj.id)][name] = True
			else:
				self.values[str(obj.id)][name] = False
			return True
			
		elif self.get_type(name) == "number":
			newval = self.tonumber(val)
			if newval:
				self.values[str(obj.id)][name] = newval
				return True
			return False

		else:
			self.values[str(obj.id)][name] = val
			return True
	async def reset_value(self, obj, name, noupdate=False):
		self.fix_model(obj)
		self.values[str(obj.id)][name] = self.default_values[name]
		if not noupdate:
			await self.values_msgupdate("save")

	def display_value(self, val):
		if isinstance(val, discord.TextChannel) or isinstance(val, discord.VoiceChannel) or isinstance(val, discord.Role):
			return val.mention
		else:
			return f"`{val}`"

	# loop through each user/guild and return their object, using the guild parameter limits it to a spesific guild.
	async def loopdata(self, guild=None):
		chomk = []
		for id in self.values:
			obj = None
			if self.type == "guild":
				obj = self.client.get_guild(int(id))
			elif self.type == "user":
				if guild:
					obj = get(guild.members, id=int(id))
				else:
					obj = await self.client.get_or_fetch_user(int(id))
			if obj:
				chomk.append(obj)
		return chomk