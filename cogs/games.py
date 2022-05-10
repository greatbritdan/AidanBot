import discord
from discord import Option
from discord.ext import commands
from discord.commands import SlashCommandGroup

import asyncio, math
from random import choice, randint
from functions import getComEmbed, getBar, userPostedRecently

class FightCog(commands.Cog):
	def __init__(self, client):
		self.client = client

	gamesgroup = SlashCommandGroup("games", "All Games.")

	async def canPlay(self, ctx, user):
		# not a bot and dnd enabled and no messages in last 5 messages.
		if (not user.bot) and self.client.UCON.get_value(user, "dnd", guild=ctx.guild) and (not await userPostedRecently(ctx.channel, user, 5)):
			await ctx.respond("This user has DND enabled and hasn't spoken recently (In this channel), this game can not be started, ask them to join you first.")
			return False
		return True

	@gamesgroup.command(name="fight", description="Fight ig.")
	async def fight(self, ctx, 
		player1:Option(discord.Member, "First fighter.", required=True),
		player2:Option(discord.Member, "Second fighter.", required=True),
		starthealth:Option(int, "Max health and also the starter health.", default=100),
		startenergy:Option(int, "Max energy and also the starter energy.", default=10),
		startheals:Option(int, "Number of heals you start with.", default=2),
		starthealammount:Option(int, "How much health you gain when you heal.", default=50),
	):
		if not ((ctx.author == player1 or await self.canPlay(ctx, player1)) and (ctx.author == player2 or await self.canPlay(ctx, player2))):
			return

		maxhealth = starthealth
		maxenergy = startenergy
		healammount = starthealammount
		player = {
			"p1": {
				"name": player1.display_name,
				"id": player1.id,
				"bot": player1.bot,
				"health": maxhealth,
				"energy": 4,
				"heals": startheals
			},
			"p2": {
				"name": player2.display_name,
				"id": player2.id,
				"bot": player2.bot,
				"health": maxhealth,
				"energy": 4,
				"heals": startheals
			}
		}
		turn, turnt = "p1", "p2"
		win, wint = "", ""

		# creates buttons
		def fightButton(name, id, emoji, timeout=False, row=1):
			disable = (player[turn]["bot"] == True or timeout)
			return discord.ui.Button(label=name, style=discord.ButtonStyle.grey, custom_id=id, emoji=emoji, disabled=disable, row=row)

		# for cheking if move can be used
		def checkMove(interaction, typ, eng=0, con=None):
			move = movetoemoji[interaction.data["custom_id"]]
			if con:
				return (move == typ and player[turn]["energy"] >= eng and player[turn]["heals"] > 0)
			else:
				return (move == typ and player[turn]["energy"] >= eng)

		# embed for the fight command
		def getFightEmbed(ctx, action=None, timeout=None, winned=None, fleeed=None):
			if winned:
				embed = getComEmbed(ctx, self.client, f"{player[win]['name']} Won The Battle!!!", f"Tough luck {player[wint]['name']}...")
			elif fleeed:
				embed = getComEmbed(ctx, self.client, f"{player[turnt]['name']} Won The Battle!!!", f"Because {player[turn]['name']} fleed, BOO!!!")
			else:
				fields = [
					[player["p1"]["name"] + " Stats:", "`Health:` " + getBar(player["p1"]["health"], maxhealth, 10, True) + " **(" + str(player["p1"]["health"]) + ")**\n`Energy:` " + getBar(player["p1"]["energy"], maxenergy, 5, True) + " (" + str(player["p1"]["energy"]) + ")"],
					[player["p2"]["name"] + " Stats:", "`Health:` " + getBar(player["p2"]["health"], maxhealth, 10, True) + " **(" + str(player["p2"]["health"]) + ")**\n`Energy:` " + getBar(player["p2"]["energy"], maxenergy, 5, True) + " (" + str(player["p2"]["energy"]) + ")"]
				]
				if action:
					fields.append([action[0], action[1]])
				fields.append([player[turn]["name"] + "'s Turn:", "Click a button to submit a move."])
				embed = getComEmbed(ctx, self.client, player["p1"]["name"] + " VS " + player["p2"]["name"], fields=fields)

			view = None
			if not (player["p1"]["bot"] and player["p2"]["bot"]):
				view = discord.ui.View(
					fightButton("Punch (" + str(math.ceil(player[turn]["energy"] / 2)) + ")", "punch", "👊",  timeout),
					fightButton("Slap (0)",                                                   "slap",  "✋",  timeout),
					fightButton("Heal (x" + str(player[turn]["heals"]) + ")",                 "heal",  "🍷",   timeout),
					fightButton("Wait (-1)",                                                  "wait",  "🕓",  timeout),
					fightButton("Flee",                                                       "flee",  "❌",  timeout)
				)

			return embed, view

		movetoemoji = {"wait":"🕓", "punch":"👊", "heal":"🍷", "flee":"❌", "slap":"✋"}

		embed, view = getFightEmbed(ctx, False)
		await ctx.respond(embed=embed, view=view)

		# for cheking if the right user uses the buttons
		def check(interaction):
			return (interaction.user.id == player[turn]["id"] and (checkMove(interaction, "❌", 0) or checkMove(interaction, "🕓", 0) or checkMove(interaction, "👊", 2) or checkMove(interaction, "✋", 0) or checkMove(interaction, "🍷", 0, True)))

		# the main loop
		while True:
			# waits for the reaction to be added
			try:
				move = ""
				if player[turn]["bot"]:
					move = "heal"
					if player[turn]["heals"] == 0 or player[turn]["health"] >= math.floor(maxhealth/2) or (player[turn]["health"] >= math.floor(maxhealth/4) and randint(1, 4) == 1) or randint(1, 4) > 1:
						eng = math.floor((maxenergy/5)*4)
						if player[turn]["energy"] > 0 and (randint(1, eng) + player[turn]["energy"]) > eng:
							move = "punch"
						else:
							move = "wait"

					await asyncio.sleep(1.5)
				else:
					interaction = await self.client.wait_for("interaction", timeout=120, check=check)
					move = interaction.data["custom_id"]
					await interaction.response.defer()

				move = movetoemoji[move]
				name1, name2 = player[turn]["name"], player[turnt]["name"]
				action = None
					
				# flee (aka quit the game)
				if move == "❌":
					embed, view = getFightEmbed(ctx, action, True, fleeed=True)
					await ctx.edit(embed=embed, view=view)
					return

				# punch
				# more energy makes the attack stronger but attacking will half your energy
				if move == "👊":
					# key (goes from 0 to 10): 0-0, 4-6, 8-12, 12-18, 16-24, 20-30, 24-36, 28-42, 32-48, 36-54, 40-60
					num = randint((player[turn]["energy"]*5)-player[turn]["energy"], (player[turn]["energy"]*5)+player[turn]["energy"])
					enum = math.ceil(player[turn]["energy"] / 2)
					action = [f"{name1} hit {name2}!", f"{name2} lost **{num} health**!\n{name1} lost **{enum} energy**!"]

					player[turn]["energy"] -= enum
					player[turnt]["health"] = clamp(player[turnt]["health"]-num, 0, maxhealth)

				# slap
				# doesn't take away any energy but does very little damage
				if move == "✋":
					num = randint(4, 10)
					action = [f"{name1} slapped {name2}!", f"{name2} lost **{num} health**!"]

					player[turnt]["health"] = clamp(player[turnt]["health"]-num, 0, maxhealth)

				# heal
				# heals 50 health, you only get 2 per battle
				if move == "🍷":
					num = healammount
					if player[turn]["heals"] == 1:
						action = [f"{name1} drank a health potion! That was their last...", f"{name1} gained **{num} health**!"]
					else:
						action = [f"{name1} drank a health potion!", f"{name1} gained **{num} health**!"]

					player[turn]["heals"] -= 1
					player[turn]["health"] = clamp(player[turn]["health"]+num, 0, maxhealth)

				# wait
				# does nothing, but it heals 1 energy
				if move == "🕓":
					action = [f"{name1} decided to wait.!", f"{name1} gained **1 energy**!"]

					player[turn]["energy"] = clamp(player[turn]["energy"]+1, 0, maxenergy)

				if player[turnt]["health"] == 0:
					win = turn
					wint = turnt
					break

				player[turn]["energy"] = clamp(player[turn]["energy"]+1, 0, maxenergy)

				oldturn = turn
				turn, turnt = turnt, oldturn

				embed, view = getFightEmbed(ctx, action)
				await ctx.edit(embed=embed, view=view)

			# if no reaction is added in a miniue, it's a draw
			except asyncio.TimeoutError:
				win = "timeout"
				break

		# victory message
		if win == "timeout":
			embed, view = getFightEmbed(ctx, action, True)
			await ctx.edit(embed=embed, view=view)
		else:
			embed, view = getFightEmbed(ctx, action, True, winned=True)
			await ctx.edit(embed=embed, view=view)

	@gamesgroup.command(name="rps", description="Rock, paper, scissors.")
	async def rps(self, ctx, 
		player1:Option(discord.Member, "First player.", required=True),
		player2:Option(discord.Member, "Second player.", required=True),
	):
		if not ((ctx.author == player1 or await self.canPlay(ctx, player1)) and (ctx.author == player2 or await self.canPlay(ctx, player2))):
			return

		options = ["rock", "paper", "scissors"]
		strtohand = {"rock":"👊", "paper":"✋", "scissors":"✌️"}
		player = {
			"p1": {
				"name": player1.display_name,
				"id": player1.id,
				"bot": player1.bot,
				"pick": ""
			},
			"p2": {
				"name": player2.display_name,
				"id": player2.id,
				"bot": player2.bot,
				"pick": ""
			}
		}
		if player["p1"]["bot"]:
			player["p1"]["pick"] = choice(options)
		if player["p2"]["bot"]:
			player["p2"]["pick"] = choice(options)

		def getRPSEmbed(timeout=None, finish=None):
			embed = ""
			if finish:
				embed = getComEmbed(ctx, self.client, finish, f"{player['p1']['name']}: `{strtohand[player['p1']['pick']]}`   |   {player['p2']['name']}: `{strtohand[player['p2']['pick']]}`")
			else:
				embed = getComEmbed(ctx, self.client, "Choose your choice.", f"{player['p1']['name']}: `?`   |   {player['p2']['name']}: `?`")

			view = None
			if not (player["p1"]["bot"] and player["p2"]["bot"]):
				view = discord.ui.View(
					discord.ui.Button(label="rock", style=discord.ButtonStyle.green, custom_id="rock", emoji="👊", disabled=timeout),
					discord.ui.Button(label="paper", style=discord.ButtonStyle.green, custom_id="paper", emoji="✋", disabled=timeout),
					discord.ui.Button(label="scissors", style=discord.ButtonStyle.green, custom_id="scissors", emoji="✌️", disabled=timeout)
				)
			return embed, view

		embed, view = getRPSEmbed()
		await ctx.respond(embed=embed, view=view)

		def check(interaction):
			return (((interaction.user.id == player["p1"]["id"] and player["p1"]["pick"] == "") or (interaction.user.id == player["p2"]["id"] and player["p2"]["pick"] == "")))

		if not (player["p1"]["bot"] and player["p2"]["bot"]):
			while True:
				try:
					interaction = await self.client.wait_for("interaction", timeout=30, check=check)
					if interaction.user.id == player["p1"]["id"]:
						player["p1"]["pick"] = interaction.data["custom_id"]
					else:
						player["p2"]["pick"] = interaction.data["custom_id"]
					await interaction.response.defer()
					if player["p1"]["pick"] != "" and player["p2"]["pick"] != "":
						break

				except asyncio.TimeoutError:
					embed, view = getRPSEmbed(True)
					await ctx.edit(embed=embed, view=view)

		state = "Something broke lol, i'm gonna blame you. <:AidanSmug:837001740947161168>"
		if player["p1"]["pick"] == player["p2"]["pick"]:
			state = "Same result, draw."
		elif player["p1"]["pick"] == "paper" and player["p2"]["pick"] == "rock":
			state = f"Paper covers Rock, {player['p1']['name']} wins!"
		elif player["p1"]["pick"] == "rock" and player["p2"]["pick"] == "scissors":
			state = f"Rock breaks Scissors, {player['p1']['name']} wins!"
		elif player["p1"]["pick"] == "scissors" and player["p2"]["pick"] == "paper":
			state = f"Scissors cuts Paper, {player['p1']['name']} wins!"
		elif player["p1"]["pick"] == "rock" and player["p2"]["pick"] == "paper":
			state = f"Paper covers Rock, {player['p2']['name']} wins!"
		elif player["p1"]["pick"] == "scissors" and player["p2"]["pick"] == "rock":
			state = f"Rock breaks Scissors, {player['p2']['name']} wins!"
		elif player["p1"]["pick"] == "paper" and player["p2"]["pick"] == "scissors":
			state = f"Scissors cuts Paper, {player['p2']['name']} wins!"

		embed, view = getRPSEmbed(True, state)
		await ctx.edit(embed=embed, view=view)

def clamp(n, minn, maxn):
	return max(min(maxn, n), minn)

def setup(client):
	client.add_cog(FightCog(client))