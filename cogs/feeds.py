import discord
import discord.ext.commands as CM
from discord.ext import tasks

from aidanbot import AidanBot
from utils.functions import sendCustomError

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

	async def checkFeeds(self):
		if self.client.settingup or self.client.isbeta:
			return

		try:
			for guild in await self.client.CON.loopdata():
				channels:list[discord.TextChannel] = self.client.CON.get_value(guild, "feed_youtube_channel", guild=guild)
				channelids:list[str] = self.client.CON.get_value(guild, "feed_youtube_channelid", guild=guild)
				videoids:list[str] = self.client.CON.get_value(guild, "feed_youtube", guild=guild)

				if (not channels) or (not channelids) or (not videoids):
					continue
				
				messages:list[str] = self.client.CON.get_value(guild, "feed_youtube_message", guild=guild)
				pings:list[discord.Role] = self.client.CON.get_value(guild, "feed_youtube_ping", guild=guild)

				for idx, channelid in enumerate(channelids):
					lastvideoidapi = self.getLastVideoIDFromChannelID(channelid)
					if lastvideoidapi == None or videoids[idx] == lastvideoidapi: # Failed to get video or last video is same as video
						continue
					if videoids[idx] == False:
						await self.client.CON.set_value(guild, "feed_youtube", lastvideoidapi)
						continue

					lastvideoapi = self.getVideoFromID(lastvideoidapi)

					ping, message, channel = pings[0], messages[0], channels[0]
					if idx in pings:
						ping = pings[idx]
					if idx in messages:
						ping = messages[idx]
					if idx in channels:
						channel = channels[idx]

					if not ping:
						ping = "(No ping role setup)"
						if not message:
							message = "**{name}** just posted a new video!\n\n> **{title}**\n\n{url}"
					else:
						ping = ping.mention
						if not message:
							message = "{ping} | **{name}** just posted a new video!\n\n> **{title}**\n\n{url}"

					await channel.send(message.format(ping=ping, title=lastvideoapi["title"], name=lastvideoapi["channelTitle"], url=f"https://www.youtube.com/watch?v={lastvideoidapi}"))
					await self.client.CON.set_value(guild, "feed_youtube", lastvideoidapi)

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

async def setup(client:AidanBot):
	await client.add_cog(FeedsCog(client), guilds=client.debug_guilds)