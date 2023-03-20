import discord
import discord.ext.commands as CM
import discord.app_commands as AC
from discord import Interaction as Itr
from discord.ext import tasks

from aidanbot import AidanBot
from utils.functions import sendCustomError
from utils.checks import ab_check

class FeedsCog(CM.Cog):
	def __init__(self, client:AidanBot):
		self.client = client
		self.loops = 0

		self.youtube_api = client.youtube_api
		self.ping.start()

	async def cog_unload(self):
		self.ping.cancel()

	def getLastVideoIDFromChannelID(self, channelid):
		try:
			request = self.youtube_api.get_activities_by_channel(channel_id=channelid).items[0].to_dict()["contentDetails"]["upload"]["videoId"]
			return request
		except:
			return None
	def getVideoFromID(self, videoid):
		try:
			request = self.youtube_api.get_video_by_id(video_id=videoid).items[0].to_dict()["snippet"]
			return request
		except:
			return None

	###
		
	async def checkFeed(self, guild, testchannelid=None):
		channels:list[discord.TextChannel] = self.client.CON.get_value(guild, "feed_youtube_channel", guild=guild)
		channelids:list[str] = self.client.CON.get_value(guild, "feed_youtube_channelid", guild=guild)

		if (not channels) or (not channelids):
			return
		
		videoids:list[str] = self.client.CON.get_value(guild, "feed_youtube", guild=guild)
		messages:list[str] = self.client.CON.get_value(guild, "feed_youtube_message", guild=guild)
		pings:list[discord.Role] = self.client.CON.get_value(guild, "feed_youtube_ping", guild=guild) 

		for idx, channelid in enumerate(channelids):
			if testchannelid and testchannelid != channelid:
				continue

			lastvideoidapi = self.getLastVideoIDFromChannelID(channelid)
			if lastvideoidapi == None or (videoids[idx] == lastvideoidapi and (not testchannelid)): # Failed to get video or last video is same as video
				return
			if (not videoids) or (not videoids[idx]):
				if not videoids:
					videoids = []
				videoids[idx] = lastvideoidapi
				await self.client.CON.set_value(guild, "feed_youtube", videoids)
				return

			lastvideoapi = self.getVideoFromID(lastvideoidapi)
			ping, message, channel = pings[0], messages[0], channels[0]
			if idx < len(pings):
				ping = pings[idx]
			if idx < len(messages):
				message = messages[idx]
			if idx < len(channels):
				channel = channels[idx]

			if not ping:
				ping = "(No ping role setup)"
				if not message:
					message = "**{name}** just posted a new video!\n\n> **{title}**\n\n{url}"
			else:
				ping = ping.mention
				if not message:
					message = "{ping} | **{name}** just posted a new video!\n\n> **{title}**\n\n{url}"
			if testchannelid:
				ping = "@fakeping"
			message = message.replace('\\n', '\n')

			await channel.send(message.format(ping=ping, title=lastvideoapi["title"], name=lastvideoapi["channelTitle"], url=f"https://www.youtube.com/watch?v={lastvideoidapi}"))
			if not testchannelid:
				await self.client.CON.set_value(guild, "feed_youtube", lastvideoidapi)

	async def checkFeeds(self):
		if self.client.settingup: #or self.client.isbeta:
			return
		
		try:
			for guild in await self.client.CON.loopdata():
				await self.checkFeed(guild)	
			self.loops = 0
		except:
			self.loops += 1
			if self.loops >= 5:
				self.ping.cancel()
				await sendCustomError(self.client, "Feeds Error", "Something went wrong with feeds. Tried 5 times, cancelling...")
			else:
				await sendCustomError(self.client, "Feeds Error", "Something went wrong with feeds.")
		
	@tasks.loop(seconds=10)
	async def ping(self):
		await self.checkFeeds()

	###
	
	feedgroup = AC.Group(name="feeds", description="Feed commands.")

	@feedgroup.command(name="test", description="Test a feed.")
	async def post(self, itr:Itr, channel:str):
		if not await ab_check(itr, self.client, is_owner=True, is_guild=True, has_value="qotd_channel"):
			return
		
		channelids:list[str] = self.client.CON.get_value(itr.guild, "feed_youtube_channelid", guild=itr.guild)
		if channel not in channelids:
			return await itr.response.send_message("You must use a valid channel, the command should show you valid options.", ephemeral=True)

		await itr.response.defer(ephemeral=True)
		await self.checkFeed(itr.guild, channel)
		await itr.edit_original_response(content="Feed tested!")

	@post.autocomplete("channel")
	async def channelname(self, itr:Itr, current):
		channelids:list[str] = self.client.CON.get_value(itr.guild, "feed_youtube_channelid", guild=itr.guild)
		if not channelids:
			return None
	
		ret = []
		for channelid in channelids:
			lastvideoidapi = self.getLastVideoIDFromChannelID(channelid)
			lastvideoapi = self.getVideoFromID(lastvideoidapi)
			ret.append(AC.Choice(name="Channel: "+lastvideoapi["channelTitle"], value=channelid))
		return ret

async def setup(client:AidanBot):
	await client.add_cog(FeedsCog(client), guilds=client.debug_guilds)
