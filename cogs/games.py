import discord
import discord.ext.commands as CM
import discord.app_commands as AC
from discord import Interaction as Itr

import asyncio, json
from random import choice
from typing import Literal

from aidanbot import AidanBot
from utils.functions import getComEmbed, userPostedRecently

rps_options = ["rock", "paper", "scissors"]
rps_optionsemoji = {"rock":"👊", "paper":"✋", "scissors":"✌️"}

from cogs.fightmodes.fight_base import FightPlayer as FP
from cogs.fightmodes.fight_normal import startFightNormal
from cogs.fightmodes.fight_classic import startFightClassic

class GamesCog(CM.Cog):
	def __init__(self, client:AidanBot):
		self.client = client

		self.replay = AC.ContextMenu(name="Fight-replay", callback=self.fight_replay_msg)
		self.client.tree.add_command(self.replay, guilds=self.client.debug_guilds)

	async def cog_unload(self):
		self.client.tree.remove_command(self.replay.name, type=self.replay.type)

	async def canPlay(self, itr:Itr, user:discord.Member):
		# not a bot and dnd enabled and no messages in last 5 messages.
		if (not user.bot) and self.client.UCON.get_value(user, "games_disabled", guild=itr.guild) and (not await userPostedRecently(itr.channel, user, 5)):
			await itr.response.send_message("This user has DND enabled and hasn't spoken recently (In this channel), this game can not be started, ask them to join you first.", ephemeral=True)
			return False
		return True

	async def defaultUsers(self, itr:Itr, user1:discord.Member=None, user2:discord.Member=None):
		if user1 and user2:
			return user1, user2
		elif user1 and user1.id != itr.user.id:
			return user1, itr.user
		elif user2 and user2.id != itr.user.id:
			return itr.user, user2
		else:
			return itr.user, await itr.guild.fetch_member(itr.client.user.id)

	###

	class rpsPlayer():
		def __init__(self, user:discord.Member):
			self.id = user.id
			self.name = user.display_name
			self.bot = user.bot
			if self.bot:
				self.pick = choice(rps_options)
			else:
				self.pick = ""
			
		@property
		def getEmoji(self):
			return rps_optionsemoji[self.pick]
			
	gamesgroup = AC.Group(name="games", description="Commands to do with games.")

	@gamesgroup.command(name="rps", description="Rock, paper, scissors!")
	@AC.describe(user1="The first player.", user2="The second player.")
	async def rps(self, itr:Itr, user1:discord.Member=None, user2:discord.Member=None):
		user1, user2 = await self.defaultUsers(itr, user1, user2)
		if not ((itr.user == user1 or await self.canPlay(itr, user1)) and (itr.user == user2 or await self.canPlay(itr, user2))):
			return
		player1, player2 = self.rpsPlayer(user1), self.rpsPlayer(user2)

		def getRPSEmbed(timeout=None, finish=None):
			embed = ""
			if finish:
				embed = getComEmbed(self.client, finish, f"{player1.name}: `{player1.getEmoji}`   |   {player2.name}: `{player2.getEmoji}`", command="Rock Paper Scissors")
			else:
				embed = getComEmbed(self.client, "Choose your choice.", f"{player1.name}: `?`   |   {player2.name}: `?`", command="Rock Paper Scissors")

			if (player1.bot and player2.bot):
				timeout = True
			view = discord.ui.View(timeout=None)
			view.add_item(discord.ui.Button(label="rock", style=discord.ButtonStyle.green, custom_id="rock", emoji="👊", disabled=timeout))
			view.add_item(discord.ui.Button(label="paper", style=discord.ButtonStyle.green, custom_id="paper", emoji="✋", disabled=timeout))
			view.add_item(discord.ui.Button(label="scissors", style=discord.ButtonStyle.green, custom_id="scissors", emoji="✌️", disabled=timeout))
			return embed, view

		embed, view = getRPSEmbed()
		await itr.response.send_message(embed=embed, view=view)
		MSG = await itr.original_response()
		
		if (player1.bot and player2.bot):
			await asyncio.sleep(1.5)
		else:
			def check(checkitr:Itr):
				try:
					return (checkitr.message.id == MSG.id)
				except:
					return False
			while True:
				try:
					butitr:Itr = await self.client.wait_for("interaction", timeout=30, check=check)
					if butitr.user.id == player1.id and player1.pick == "":
						player1.pick = butitr.data["custom_id"]
						await butitr.response.send_message(f"Pick set to {player1.getEmoji}!", ephemeral=True)
					elif butitr.user.id == player2.id and player2.pick == "":
						player2.pick = butitr.data["custom_id"]
						await butitr.response.send_message(f"Pick set to {player2.getEmoji}!", ephemeral=True)
					elif butitr.user.id != player1.id and butitr.user.id != player2.id:
						await butitr.response.send_message(self.client.itrFail(), ephemeral=True)
					if player1.pick != "" and player2.pick != "":
						break
				except asyncio.TimeoutError:
					embed, view = getRPSEmbed(True)
					await itr.edit_original_response(embed=embed, view=view)
					return
				
		state = "Something broke lol, i'm gonna blame you. <:AidanSmug:837001740947161168>"
		if player1.pick == player2.pick:
			state = "Same result, draw."
		elif player1.pick == "paper" and player2.pick == "rock":
			state = f"Paper covers Rock, {player1.name} wins!"
		elif player1.pick == "rock" and player2.pick == "scissors":
			state = f"Rock breaks Scissors, {player1.name} wins!"
		elif player1.pick == "scissors" and player2.pick == "paper":
			state = f"Scissors cuts Paper, {player1.name} wins!"
		elif player1.pick == "rock" and player2.pick == "paper":
			state = f"Paper covers Rock, {player2.name} wins!"
		elif player1.pick == "scissors" and player2.pick == "rock":
			state = f"Rock breaks Scissors, {player2.name} wins!"
		elif player1.pick == "paper" and player2.pick == "scissors":
			state = f"Scissors cuts Paper, {player2.name} wins!"

		embed, view = getRPSEmbed(True, state)
		await itr.edit_original_response(embed=embed, view=view)

	###

	async def fight(self, itr:Itr, mode:str=None, user1:discord.Member=None, user2:discord.Member=None, aiuser1:str=None, aiuser2:str=None):
		core, turn, turnt = "", "", ""
		if mode == "normal":
			core = startFightNormal(user1, user2, aiuser1, aiuser2)
		elif mode == "classic":
			core = startFightClassic(user1, user2, aiuser1, aiuser2)
		turn:FP = core.turn
		turnt:FP = core.turnt

		LOG = {"version":"V0.2","mode":mode,"player1ai":aiuser1,"player2ai":aiuser2,"embeds":[]}
		def addLog(embed:discord.Embed):
			LOG["embeds"].append(embed.to_dict())
		def endLog():
			with open("fightlog.json", "w+") as file:
				json.dump(LOG, file, indent=4)

		embed, view = core.getEmbed(itr, self.client, turn)
		addLog(embed)
		await itr.response.send_message(embed=embed, view=view)
		MSG = await itr.original_response()

		def check(checkitr:Itr):
			try:
				return (checkitr.message.id == MSG.id and checkitr.user.id == turn.id)
			except:
				return False
		while True:
			try:
				move = ""
				if turn.nextturn:
					move = turn.nextturn
					butid = False
					await asyncio.sleep(2.5)
				elif turn.bot:
					move = core.userMoveAI()
					butid = False
					await asyncio.sleep(2.5)
				else:
					butitr:Itr = await self.client.wait_for("interaction", check=check, timeout=180)
					await butitr.response.defer()
					butid = butitr.data["custom_id"]
					move = core.moves.getMoveFromButton(butid, turn, turnt)

				end, endid = False, ""
				if move == "flee":
					end, endid = True, "flee"
				else:
					end, endid = core.useMove(move, butid)
				if end:
					if endid.endswith("-killself") or endid == "flee":
						turn, turnt = core.swapTurn()
					embed, view = core.getWinEmbed(itr, self.client, endid, turn, turnt)
					addLog(embed)
					endLog()
					await itr.edit_original_response(embed=embed, view=view)
					with open("fightlog.json", "rb") as file:
						await itr.channel.send(file=discord.File(file,"fightlog.json"))
					return

				if turn.continueturn:
					turn.continueturn = False
				else:
					turn, turnt = core.swapTurn()
				embed, view = core.getEmbed(itr, self.client, turn)
				addLog(embed)
				await itr.edit_original_response(embed=embed, view=view)

			except asyncio.TimeoutError:
				embed, view = core.getEmbed(itr, self.client, turn, True)
				await itr.edit_original_response(embed=embed, view=view)
				return

	@gamesgroup.command(name="fight", description="Fight against another user or one of the main AI levels.")
	@AC.describe(user1="The first player.", user2="The second player.", ailevel="AI level for the bot.",
		ailevel1="AI level for player 1 if a bot, overrides master.", ailevel2="AI level for player 2 if a bot, overrides master."
	)
	async def fight_normal(self, itr:Itr, user1:discord.Member=None, user2:discord.Member=None,
		ailevel:Literal["dead","random","easy","medium","hard"]="medium", ailevel1:Literal["dead","random","easy","medium","hard"]=None, ailevel2:Literal["dead","random","easy","medium","hard"]=None
	):
		aiuser1, aiuser2 = ailevel1 or ailevel, ailevel2 or ailevel
		user1, user2 = await self.defaultUsers(itr, user1, user2)
		if not ((itr.user == user1 or await self.canPlay(itr, user1)) and (itr.user == user2 or await self.canPlay(itr, user2))):
			return
		await self.fight(itr, "normal", user1, user2, aiuser1, aiuser2)

	@gamesgroup.command(name="fight-classic", description="Fight against another user or one of the main AI levels. Full recreation of the original fight.")
	@AC.describe(user1="The first player.", user2="The second player.", ailevel="AI level for the bot.",
		ailevel1="AI level for player 1 if a bot, overrides master.", ailevel2="AI level for player 2 if a bot, overrides master."
	)
	async def fight_classic(self, itr:Itr, user1:discord.Member=None, user2:discord.Member=None,
		ailevel:Literal["dead","random","easy","hard"]="easy", ailevel1:Literal["dead","random","easy","hard"]=None, ailevel2:Literal["dead","random","easy","hard"]=None
	):
		aiuser1, aiuser2 = ailevel1 or ailevel, ailevel2 or ailevel
		user1, user2 = await self.defaultUsers(itr, user1, user2)
		if not ((itr.user == user1 or await self.canPlay(itr, user1)) and (itr.user == user2 or await self.canPlay(itr, user2))):
			return
		await self.fight(itr, "classic", user1, user2, aiuser1, aiuser2)

	###

	@gamesgroup.command(name="fight-replay", description="Replay a fight from a fightlog file!")
	@AC.describe(logfile="The fightlog file to read from.")
	async def fight_replay_slash(self, itr:Itr, logfile:discord.Attachment):
		await self.fight_replay(itr, logfile)

	async def fight_replay_msg(self, itr:Itr, msg:discord.Message):
		if len(msg.attachments) > 0:
			await self.fight_replay(itr, msg.attachments[0], True)
		else:
			await itr.response.send_message("The message you selected has no attachments.", ephemeral=True)

	async def fight_replay(self, itr:Itr, logfile:discord.Attachment, app_command=False):
		page, pages = 0, []
		try:
			byte = await logfile.read()
			LOG = json.loads(byte.decode("utf-8"))
			pages = [discord.Embed.from_dict(e) for e in LOG["embeds"]]
		except:
			if app_command:
				return await itr.response.send_message("The attachment for the log file you inputted is incorrect! Make sure the log file is the first or only attachment then try again.", ephemeral=True)
			else:
				return await itr.response.send_message("The log file you inputted is incorrect! If you're on mobile use the message command games-replay or upload the file as a `.txt`. If you're on PC please try again.", ephemeral=True)

		def getView(timeout=False):
			view = discord.ui.View(timeout=None)
			view.add_item(discord.ui.Button(label="Start",                  style=discord.ButtonStyle.blurple, custom_id="start",   disabled=timeout))
			view.add_item(discord.ui.Button(label="<-",                     style=discord.ButtonStyle.blurple, custom_id="left",    disabled=timeout))
			view.add_item(discord.ui.Button(label=f"{page+1}/{len(pages)}", style=discord.ButtonStyle.gray,    custom_id="display", disabled=True))
			view.add_item(discord.ui.Button(label="->",                     style=discord.ButtonStyle.blurple, custom_id="right",   disabled=timeout))
			view.add_item(discord.ui.Button(label="End",                    style=discord.ButtonStyle.blurple, custom_id="end",     disabled=timeout))
			return view
		
		await itr.response.send_message(embed=pages[page], view=getView())
		MSG = await itr.original_response()

		def check(checkitr:Itr):
			try:
				return (checkitr.message.id == MSG.id)
			except:
				return False
		while True:
			try:
				butitr:Itr = await self.client.wait_for("interaction", timeout=30, check=check)
				if butitr.user == itr.user:
					await butitr.response.defer()
					if butitr.data["custom_id"] == "left":
						page -= 1
						if page < 0: page = len(pages)-1
					elif butitr.data["custom_id"] == "right":
						page += 1
						if page > len(pages)-1: page = 0
					elif butitr.data["custom_id"] == "start":
						page = 1
					elif butitr.data["custom_id"] == "end":
						page = len(pages)-1
					await itr.edit_original_response(embed=pages[page], view=getView())
				else:
					await butitr.response.send_message(self.client.itrFail(), ephemeral=True)
			except asyncio.TimeoutError:
				return await itr.edit_original_response(view=getView(True))

async def setup(client:AidanBot):
	await client.add_cog(GamesCog(client), guilds=client.debug_guilds)