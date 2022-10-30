import discord, copy
from discord.utils import get
import discord.ext.commands as CM

#from aidanbot import AidanBot

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

	def __init__(self, client:CM.Bot, ctype):
		self.client = client
		self.type = ctype

		self.values = {}
		self.valid_values = []
		self.default_values = {}
		self.desc_values = {}
		self.type_values = {}
		self.restrict_values = {}
		self.stackable_values = {}

		list = None
		if self.type == "guild":
			self.logname = "guild-logs"
			list = VALUES
		if self.type == "user":
			self.logname = "user-logs"
			list = UAVALUES

		for val in list:
			self.valid_values.append(val)
			self.default_values[val] = list[val]["default"]
			self.desc_values[val] = list[val]["help"]
			if list[val]["type"].startswith("[]"):
				self.stackable_values[val] = True
				self.type_values[val] = list[val]["type"][2:]
			else:
				self.stackable_values[val] = False
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
			values = self.savevalues(self.values)
			await message.delete()
			with open("temp.json", "w") as f:
				json.dump(values, f, indent=4)
			await channel.send(file=discord.File("temp.json", "values.json"))

	def tonumber(self, val):
		try:
			return int(val)
		except ValueError:
			return False
			
	def savevalues(self, values):
		valuescopy = copy.deepcopy(values)
		for id in valuescopy:
			valuesidcopy = copy.deepcopy(values[id])
			for name in valuesidcopy:
				if values[id][name] == self.default_values[name]:
					values[id].pop(name)
			if len(values[id]) == 0:
				values.pop(id)
		return values

	def fix_model(self, obj:discord.Object=None, id=None): # if values or group is missing it'll fill out the list
		if obj: id = str(obj.id)
		if id not in self.values or self.values[id] == None:
			self.values[id] = {}
		for name in self.default_values:
			if name not in self.values[id]:
				self.values[id][name] = self.default_values[name]

		# fix yucky order
		vals = copy.deepcopy(self.values[id])
		self.values[id] = {}
		for name in self.default_values:
			self.values[id][name] = vals[name]

	def exists(self, name):
		return (name in self.valid_values)
	def get_help(self, name):
		return self.desc_values[name]
	def get_type(self, name):
		return self.type_values[name]
	def get_stackable(self, name):
		return self.stackable_values[name]
	def is_restricted(self, name):
		return self.restrict_values[name]
		
	async def remove_group(self, obj:discord.Object):
		if str(obj.id) in self.values:
			self.values.pop(str(obj.id))
			await self.values_msgupdate("save")
			return True
		return False
	def get_group(self, obj:discord.Object):
		self.fix_model(obj)
		return self.values[str(obj.id)]

	def get_value(self, obj:discord.Object, name, guild:discord.Guild=None):
		self.fix_model(obj)
		val = self.values[str(obj.id)][name]
		if self.get_stackable(name) and type(val) == list:
			result = []
			for nval in val:
				result.append( self._get_value(name, nval, guild) )
		else:
			result = self._get_value(name, val, guild)
		return result
	def _get_value(self, name, val, guild:discord.Guild=None):
		typ = self.get_type(name)
		if typ == "channel/thread":
			channel = get(guild.channels, id=val)
			if channel:
				return channel
			else:
				thread = get(guild.threads, id=val)
				if thread:
					return thread
		elif typ == "channel":
			return get(guild.channels, id=val)
		elif typ == "thread":
			return get(guild.threads, id=val)
		elif typ == "role":
			return get(guild.roles, id=val)
		else:
			return val
	def can_set_value(self, obj:discord.Object, name, val):
		stackable_limit = 5
		string_limit = 250
		if self.type == "guild" and self.get_value(obj, "guild_status"):
			stackable_limit = 15
			string_limit = 500
		if self.get_stackable(name) and len(val.replace(" ","").split(",")) > stackable_limit:
			return "Stackable values like `{name}` can't have more than {limit} {type}s.".format(limit=stackable_limit, name=name, type=self.get_type(name))
		if self.get_type(name) == "string":
			if val != True and val != False and len(val) > string_limit:
				return "String values like `{name}` can't have more than {limit} letters.".format(limit=string_limit, name=name)
		return False
	async def set_value(self, obj:discord.Object, name, val, guild:discord.Guild=None, noupdate=False):
		self.fix_model(obj)
		err = self.can_set_value(obj, name, val)
		if err:
			return False, err
		if self.get_stackable(name):
			vals = val.replace(" ","").split(",")
			result = []
			for nval in vals:
				result.append( self._set_value(obj, name, nval, guild) )
		else:
			result = self._set_value(obj, name, val, guild)
		self.values[str(obj.id)][name] = result
		if not noupdate:
			await self.values_msgupdate("save")
		return result, False
	def _set_value(self, obj:discord.Object, name, val, guild:discord.Guild):
		typ = self.get_type(name)
		if (typ != "string") and type(val) == str:
			val = val.lower()
			if (val == "false" or val == "none"):
				return False

		if typ == "channel/thread":
			newval = self.tonumber(val)
			channel = get(guild.channels, id=newval) if newval else get(guild.channels, name=val)
			if channel:
				return channel.id
			else:
				thread = get(guild.threads, id=newval) if newval else get(guild.threads, name=val)
				if thread:
					return thread.id	
		if typ == "channel":
			newval = self.tonumber(val)
			channel = get(guild.channels, id=newval) if newval else get(guild.channels, name=val)
			if channel:
				return channel.id
		elif typ == "thread":
			newval = self.tonumber(val)
			thread = get(guild.threads, id=newval) if newval else get(guild.threads, name=val)
			if thread:
				return thread.id
		elif typ == "role":
			newval = self.tonumber(val)
			role = get(guild.roles, id=newval) if newval else get(guild.roles, name=val)
			if role:
				return role.id
		elif typ == "boolean":
			if val == "true":
				return True
			else:
				return False
		elif typ == "number":
			newval = self.tonumber(val)
			if newval:
				return newval
		else:
			return val
	async def reset_value(self, obj:discord.Object, name, noupdate=False):
		self.fix_model(obj)
		self.values[str(obj.id)][name] = self.default_values[name]
		if not noupdate:
			await self.values_msgupdate("save")

	def raw_value(self, name, val):
		if self.get_stackable(name) and type(val) == list:
			result = []
			for nval in val:
				result.append(self._raw_value(nval))
			return ",".join(result)
		else:
			return self._raw_value(val)
	def _raw_value(self, val):
		if isinstance(val, discord.TextChannel) or isinstance(val, discord.Thread) or isinstance(val, discord.Role):
			return str(val.id)
		return str(val)
	def display_value(self, name, val):
		if self.get_stackable(name) and type(val) == list:
			result = []
			for nval in val:
				result.append(self._display_value(nval))
			return ", ".join(result)
		else:
			return self._display_value(val)
	def _display_value(self, val):
		if isinstance(val, discord.TextChannel) or isinstance(val, discord.Thread) or isinstance(val, discord.Role):
			return val.mention
		return f"`{val}`"

	# loop through each user/guild and return their object, using the guild parameter limits it to a spesific guild.
	async def loopdata(self, guild:discord.Guild=None):
		chomk = []
		for id in self.values:
			obj = None
			if self.type == "guild":
				obj = self.client.get_guild(int(id))
			elif self.type == "user":
				if guild:
					obj = get(guild.members, id=int(id))
				else:
					obj = await self.client.fetch_user(int(id))
			if obj:
				chomk.append(obj)
		return chomk