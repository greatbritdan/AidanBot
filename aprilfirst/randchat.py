from random import choice
from discord.utils import get
import discord

async def randchat_on_message(client, msg:discord.Message):
    logguild = get(client.guilds, id=879063875469860874) # get log channel
    logchannel = get(logguild.text_channels, name="randomlog-talk")
    member = choice(msg.guild.members) # get random member
    await client.sendWebhook(msg.channel, member.display_name, member.display_avatar, msg.content, [])
    await client.sendWebhook(logchannel, msg.author.display_name, msg.author.display_avatar, msg.content, [])
    await msg.delete()
