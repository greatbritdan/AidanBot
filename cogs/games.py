import discord
from discord.ext import commands

import asyncio
import math
from random import randint

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

		await FightNewgame(ctx, self.client, v1, v2, 100, 10)

	@commands.command(description=DESC["rps"])
	@commands.cooldown(1, 5)
	async def rps(self, ctx, rigged:bool=False):
		options = ["rock", "paper", "scissors"]
		strtohand = {"rock":"👊", "paper":"✋", "scissors":"✌️"}
		p1pick = ""
		p2pick = options[randint(0, len(options)-1)]

		name = ctx.author.name
		if ctx.author.nick:
			name = ctx.author.nick

		emb = getComEmbed(ctx, self.client, "Rock, Paper, Scissors", "Choose your choice", "You: `?`   AidanBot: `?`")
		MSG = await ctx.send(embed=emb, view=discord.ui.View(
			discord.ui.Button(label="rock", style=discord.ButtonStyle.green, custom_id="rock", emoji="👊"),
			discord.ui.Button(label="paper", style=discord.ButtonStyle.green, custom_id="paper", emoji="✋"),
			discord.ui.Button(label="scissors", style=discord.ButtonStyle.green, custom_id="scissors", emoji="✌️")
		))

		def check(interaction):
			return (interaction.user.id == ctx.author.id and interaction.message.id == MSG.id)

		try:
			interaction = await self.client.wait_for("interaction", timeout=30, check=check)
			p1pick = interaction.data["custom_id"]

			if rigged:
				if p1pick == "rock":
					p2pick = "paper"
				elif p1pick == "paper":
					p2pick = "scissors"
				elif p1pick == "scissors":
					p2pick = "rock"

			state = "Something broke lol, i'm gonna blame you. <:AidanSmug:837001740947161168>"
			if p1pick == p2pick:
				state = "Same result, draw."
			elif p1pick == "paper" and p2pick == "rock":
				state = f"Paper covers Rock, {name} wins!"
			elif p1pick == "rock" and p2pick == "scissors":
				state = f"Rock breaks Scissors, {name} wins!"
			elif p1pick == "scissors" and p2pick == "paper":
				state = f"Scissors cuts Paper, {name} wins!"
			elif p1pick == "rock" and p2pick == "paper":
				state = "Paper covers Rock, I win!!!"
			elif p1pick == "scissors" and p2pick == "rock":
				state = "Rock breaks Scissors, I win!!!"
			elif p1pick == "paper" and p2pick == "scissors":
				state = "Scissors cuts Paper, I win!!!"

			emb = getComEmbed(ctx, self.client, "Rock, Paper, Scissors", state, f"You: {strtohand[p1pick]} | AidanBot: {strtohand[p2pick]}")
			await MSG.edit(embed=emb, view=discord.ui.View(
				discord.ui.Button(label="rock", style=discord.ButtonStyle.grey, custom_id="rock", emoji="👊", disabled=True),
				discord.ui.Button(label="paper", style=discord.ButtonStyle.grey, custom_id="paper", emoji="✋", disabled=True),
				discord.ui.Button(label="scissors", style=discord.ButtonStyle.grey, custom_id="scissors", emoji="✌️", disabled=True)
			))

		except asyncio.TimeoutError:
			emb = getComEmbed(ctx, self.client, "Rock, Paper, Scissors (timeout)", "Too slow idiot!", "You: `?` | AidanBot: `?`")
			await MSG.edit(embed=emb, view=discord.ui.View(
				discord.ui.Button(label="rock", style=discord.ButtonStyle.grey, custom_id="rock", emoji="👊", disabled=True),
				discord.ui.Button(label="paper", style=discord.ButtonStyle.grey, custom_id="paper", emoji="✋", disabled=True),
				discord.ui.Button(label="scissors", style=discord.ButtonStyle.grey, custom_id="scissors", emoji="✌️", disabled=True)
			))
			
async def FightNewgame(ctx, client, p1:discord.Member, p2:discord.Member, mhealth:int=100, menergy:int=10):
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
		fields.append(player[turn]["name"] + "'s Turn:", "Click a button to submit a move.")
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

def clamp(n, minn, maxn):
	return max(min(maxn, n), minn)

def setup(client):
	client.add_cog(GamesCog(client))