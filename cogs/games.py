import discord
from discord.ext import commands

import asyncio, math
from random import randint, choice

from functions import getComEmbed, getBar

import json
with open('./commanddata.json') as file:
	temp = json.load(file)
	DESC = temp["desc"]

class GamesCog(commands.Cog):
	def __init__(self, client):
		self.client = client

	@commands.command(description=DESC["fight"])
	@commands.cooldown(1, 30)
	async def fight(self, ctx, user1:discord.Member=None, user2:discord.Member=None):
		if user1 == None:
			v1 = ctx.author
			v2 = ctx.guild.get_member(self.client.user.id)
		elif user2 == None:
			v1 = ctx.author
			v2 = user1
		else:
			v1 = user1
			v2 = user2

		await self.FightNewgame(ctx, self.client, v1, v2, 100, 10)

	@commands.command(description=DESC["rps"])
	@commands.cooldown(1, 10)
	async def rps(self, ctx, user1:discord.Member=None, user2:discord.Member=None):
		if user1 == None:
			v1 = ctx.author
			v2 = ctx.guild.get_member(self.client.user.id)
		elif user2 == None:
			v1 = ctx.author
			v2 = user1
		else:
			v1 = user1
			v2 = user2

		await self.RPSNewgame(ctx, self.client, v1, v2)
			
	async def FightNewgame(self, ctx, client, p1:discord.Member, p2:discord.Member, mhealth:int=100, menergy:int=10):
		# setup vars and lists
		maxhealth = mhealth
		maxenergy = menergy
		player = {
			"p1": {
				"name": p1.display_name,
				"id": p1.id,
				"bot": p1.bot,
				"health": maxhealth,
				"energy": 4,
				"heals": 2
			},
			"p2": {
				"name": p2.display_name,
				"id": p2.id,
				"bot": p2.bot,
				"health": maxhealth,
				"energy": 4,
				"heals": 2
			}
		}
		turn, turnt = "p1", "p2"

		# creates buttons
		def fightButton(name, id, emoji, timeout=False):
			disable = (player[turn]["bot"] == True or timeout)
			return discord.ui.Button(label=name, style=discord.ButtonStyle.grey, custom_id=id, emoji=emoji, disabled=disable)

		# for cheking if move can be used
		def checkMove(interaction, typ, eng=0, con=None):
			move = movetoemoji[interaction.data["custom_id"]]
			if con:
				return (move == typ and player[turn]["energy"] >= eng and player[turn]["heals"] > 0)
			else:
				return (move == typ and player[turn]["energy"] >= eng)

		# embed for the fight command
		def getFightEmbed(ctx, action=None, timeout=None):
			command = "Fight"
			if timeout:
				command = "Fight (timeout)"

			fields = [
				[player["p1"]["name"] + " Stats:", "`Health:` " + getBar(player["p1"]["health"], maxhealth, 10, True) + " **(" + str(player["p1"]["health"]) + ")**\n`Energy:` " + getBar(player["p1"]["energy"], maxenergy, 5, True) + " (" + str(player["p1"]["energy"]) + ")"],
				[player["p2"]["name"] + " Stats:", "`Health:` " + getBar(player["p2"]["health"], maxhealth, 10, True) + " **(" + str(player["p2"]["health"]) + ")**\n`Energy:` " + getBar(player["p2"]["energy"], maxenergy, 5, True) + " (" + str(player["p2"]["energy"]) + ")"]
			]
			if action:
				fields.append([action[0], action[1]])
			fields.append([player[turn]["name"] + "'s Turn:", "Click a button to submit a move."])
			emb = getComEmbed(ctx, client, command, player["p1"]["name"] + " VS " + player["p2"]["name"], fields=fields)

			view = None
			if not (player["p1"]["bot"] and player["p2"]["bot"]):
				view = discord.ui.View(
					fightButton("Wait (-1)",                                                  "wait",  "🕓", timeout),
					fightButton("Punch (" + str(math.ceil(player[turn]["energy"] / 2)) + ")", "punch", "👊", timeout),
					fightButton("Slap (0)",                                                   "slap",  "✋", timeout),
					fightButton("Heal (x" + str(player[turn]["heals"]) + ")",                 "heal",  "🍷", timeout),
					fightButton("Flee",                                                       "flee",  "❌", timeout)
				)

			return emb, view

		movetoemoji = {"wait":"🕓", "punch":"👊", "heal":"🍷", "flee":"❌", "slap":"✋"}

		embed, view = getFightEmbed(ctx, False)
		MSG = await ctx.send(embed=embed, view=view)

		# for cheking if the right user uses the buttons
		def check(interaction):
			return (interaction.user.id == player[turn]["id"] and interaction.message.id == MSG.id and (checkMove(interaction, "❌", 0) or checkMove(interaction, "🕓", 0) or checkMove(interaction, "👊", 2) or checkMove(interaction, "✋", 0) or checkMove(interaction, "🍷", 0, True)))

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
					interaction = await client.wait_for("interaction", timeout=60, check=check)
					move = interaction.data["custom_id"]

				move = movetoemoji[move]
				name1, name2 = player[turn]["name"], player[turnt]["name"]
					
				# flee (aka quit the game)
				if move == "❌":
					await MSG.delete()
					await ctx.send(f"{name1} fled!\nGG {name2}!!!")
					return

				# punch
				# more energy makes the attack stronger but attacking will half your energy
				if move == "👊":
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
					num = 50
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
				await MSG.edit(embed=embed, view=view)

			# if no reaction is added in a miniue, it's a draw
			except asyncio.TimeoutError:
				win = "timeout"
				break

		# victory message
		if win == "timeout":
			embed, view = getFightEmbed(ctx, action, True)
			await MSG.edit(embed=embed, view=view)
		else:
			await MSG.delete()
			await ctx.send("GG " + player[win]["name"] + "!!! Tough luck " + player[wint]["name"])

	async def RPSNewgame(self, ctx, client, p1:discord.Member, p2:discord.Member):
		options = ["rock", "paper", "scissors"]
		strtohand = {"rock":"👊", "paper":"✋", "scissors":"✌️"}

		player = {
			"p1": {
				"name": p1.display_name,
				"id": p1.id,
				"bot": p1.bot,
				"pick": ""
			},
			"p2": {
				"name": p2.display_name,
				"id": p2.id,
				"bot": p2.bot,
				"pick": ""
			}
		}

		if player["p1"]["bot"]:
			player["p1"]["pick"] = choice(options)
		if player["p2"]["bot"]:
			player["p2"]["pick"] = choice(options)

		def getRPSEmbed(timeout=None, finish=None):
			command = "Rock, Paper, Scissors"
			if timeout:
				command = "Rock, Paper, Scissors (timeout)"

			emb = ""
			if finish:
				emb = getComEmbed(ctx, client, command, finish, f"{player['p1']['name']}: `{strtohand[player['p1']['pick']]}`   |   {player['p2']['name']}: `{strtohand[player['p2']['pick']]}`")
			else:
				emb = getComEmbed(ctx, client, command, "Choose your choice.", f"{player['p1']['name']}: `?`   |   {player['p2']['name']}: `?`")

			view = None
			if not (player["p1"]["bot"] and player["p2"]["bot"]):
				view = discord.ui.View(
					discord.ui.Button(label="rock", style=discord.ButtonStyle.green, custom_id="rock", emoji="👊", disabled=timeout),
					discord.ui.Button(label="paper", style=discord.ButtonStyle.green, custom_id="paper", emoji="✋", disabled=timeout),
					discord.ui.Button(label="scissors", style=discord.ButtonStyle.green, custom_id="scissors", emoji="✌️", disabled=timeout)
				)

			return emb, view

		emb, view = getRPSEmbed()
		MSG = await ctx.send(embed=emb, view=view)

		def check(interaction):
			return (interaction.message.id == MSG.id and ((interaction.user.id == player["p1"]["id"] and player["p1"]["pick"] == "") or (interaction.user.id == player["p2"]["id"] and player["p2"]["pick"] == "")))

		if not (player["p1"]["bot"] and player["p2"]["bot"]):
			while True:
				try:
					interaction = await self.client.wait_for("interaction", timeout=30, check=check)
					if interaction.user.id == player["p1"]["id"]:
						player["p1"]["pick"] = interaction.data["custom_id"]
					else:
						player["p2"]["pick"] = interaction.data["custom_id"]

					if player["p1"]["pick"] != "" and player["p2"]["pick"] != "":
						break

				except asyncio.TimeoutError:
					emb, view = getRPSEmbed(True)
					await MSG.edit(embed=emb, view=view)

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

		emb, view = getRPSEmbed(True, state)
		await MSG.edit(embed=emb, view=view)

def clamp(n, minn, maxn):
	return max(min(maxn, n), minn)

def setup(client):
	client.add_cog(GamesCog(client))