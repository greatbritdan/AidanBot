import discord
from discord.ext import commands
from discord.utils import get

from functions import getEmbed

import json
with open('./commanddata.json') as file:
    temp = json.load(file)
    DESC = temp["desc"]

class LoggingCog(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.red = discord.Color.red()
        self.green = discord.Color.green()
        self.yellow = discord.Color.orange()
        self.channel = False

    def check_valid(self, guild):
        if self.client.isbeta:
            return
        chan = self.client.get_value(guild, "logs_channel")
        if chan:
            self.channel = False
            if type(chan) == int:
                self.channel = get(guild.channels, id=chan)
            elif type(chan) == str:
                self.channel = get(guild.channels, name=chan)
            if self.channel:
                return True
        return False

    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):
        if not self.check_valid(channel.guild):
            return

        emb = getEmbed("📺 ✔️ Channel Created!", f"#{channel.name} ({channel.mention})", self.green, {})
        emb.set_footer(text=f"ID: {channel.id}.")
        await self.channel.send(embed=emb)

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        if not self.check_valid(channel.guild):
            return

        emb = getEmbed("📺 ✖️ Channel Deleted!", f"#{channel.name}", self.red, {})
        emb.set_footer(text=f"ID: {channel.id}.")
        await self.channel.send(embed=emb)

    @commands.Cog.listener()
    async def on_guild_channel_update(self, old, new):
        if not self.check_valid(old.guild):
            return

        fields = []
        if old.name != new.name:
            fields.append(["Name Changed:", f"**Old:** #{old.name}\n**New:** #{new.name}"])
        if old.topic != new.topic:
            fields.append(["Topic Changed:", f"**Old:** {old.topic}\n**New:** {new.topic}"])
        if len(fields) == 0:
            return

        emb = getEmbed("📺 🛠️ Channel Updated!", f"#{old.name} ({old.mention}) was updated.", self.yellow, fields)
        emb.set_footer(text=f"ID: {old.id}.")
        await self.channel.send(embed=emb)

    @commands.Cog.listener()
    async def on_guild_update(self, old, new):
        if not self.check_valid(old):
            return

        fields = []
        if old.name != new.name:
            fields.append(["Name Changed:", f"**Old:** {old.name}\n**New:** {new.name}"])
        if old.icon != new.icon:
            fields.append(["Icon Changed:", f" "])
        if len(fields) == 0:
            return

        emb = getEmbed("⚙️ Guild Updated!", f"Server was updated.", self.yellow, fields)
        emb.set_footer(text=f"ID: {old.id}.")
        emb.set_thumbnail(url=new.icon.url)
        await self.channel.send(embed=emb)

    @commands.Cog.listener()
    async def on_guild_role_create(self, role):
        if not self.check_valid(role.guild):
            return

        emb = getEmbed("📝 ✔️ Role Created!", f"@{role.name} ({role.mention})", self.green, {})
        emb.set_footer(text=f"ID: {role.id}.")
        await self.channel.send(embed=emb)

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role):
        if not self.check_valid(role.guild):
            return

        emb = getEmbed("📝 ✖️ Role Deleted!", f"@{role.name}", self.red, {})
        emb.set_footer(text=f"ID: {role.id}.")
        await self.channel.send(embed=emb)

    @commands.Cog.listener()
    async def on_guild_role_update(self, old, new):
        if not self.check_valid(old.guild):
            return

        fields = []
        if old.name != new.name:
            fields.append(["Name Changed:", f"**Old:** {old.name}\n**New:** {new.name}"])
        if old.color != new.color:
            oldc, newc = f"({old.color.r},{old.color.g},{old.color.b})", f"({new.color.r},{new.color.g},{new.color.b})"
            fields.append(["Color Changed:", f"**Old:** {oldc}\n**New:** {newc}"])
        if old.hoist and (not new.hoist):
            fields.append(["Role un-hoisted", f"**Old:** False\n**New:** True"])
        elif (not old.hoist) and new.hoist:
            fields.append(["Role hoisted", f"**Old:** True\n**New:** False"])
        if len(fields) == 0:
            return

        emb = getEmbed("📝 🛠️ Role Updated!", f"@{old.name} ({old.mention}) was updated.", self.yellow, fields)
        emb.set_footer(text=f"ID: {old.id}.")
        await self.channel.send(embed=emb)

def setup(client):
    client.add_cog(LoggingCog(client))