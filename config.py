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

    # get if a value is restricted (can't be changed)
    def is_restricted(self, name):
        if self.restrict_values[name]:
            return True
        return False

    # remove a user/guild from the config file
    def remove_all(self, obj):
        if str(obj.id) in self.values:
            self.values[str(obj.id)] = None
            return True
        return False

    # get all values from a user/guild
    def get_all(self, obj):
        if str(obj.id) in self.values:
            return self.values[str(obj.id)]
        return False

    # get a spesific value from a user/guild
    def get_value(self, obj, name):
        if str(obj.id) in self.values and name in self.values[str(obj.id)]:
            return self.values[str(obj.id)][name]
        if name in self.default_values:
            return self.default_values[name]
        return False

    # get a channel value from a user/guild
    def get_channel(self, obj, name, guild):
        chan = self.get_value(obj, name)
        channel = None
        if type(chan) == int:
            channel = get(guild.channels, id=chan)
        elif type(chan) == str:
            channel = get(guild.channels, name=chan)
        return channel

    # get a role value from a user/guild
    def get_role(self, obj, name, guild):
        rol = self.get_value(obj, name)
        role = None
        if type(rol) == int:
            role = get(guild.roles, id=rol)
        elif type(rol) == str:
            role = get(guild.roles, name=rol)
        return role

    # set a value from a user/guild
    def set_value(self, obj, name, value):
        if str(obj.id) in self.values and name in self.valid_values:
            self.values[str(obj.id)][name] = value
            return True
        return False

    # set a value from a user/guild, adds to database if doesn't exist
    def set_value_force(self, obj, name, value):
        if str(obj.id) not in self.values:
            self.values[str(obj.id)] = {}
        for n in self.default_values:
            if n not in self.values[str(obj.id)]:
                self.values[str(obj.id)][n] = self.default_values[n]
        return self.set_value(obj, name, value)

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