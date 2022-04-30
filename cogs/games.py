from importlib.metadata import files
import discord
from discord.ext import commands

import asyncio, math, datetime
from random import seed, randint, choice

from functions import getComEmbed, getBar, userPostedRecently

class GamesCog(commands.Cog):
	def __init__(self, client):
		self.client = client
		with open('./data/words.txt') as file:
			self.worblewords = [line.rstrip().lower() for line in file]

	async def canPlay(self, ctx, user):
		# not a bot and dnd enabled and no messages in last 5 messages.
		if (not user.bot) and self.client.UCON.get_value(user, "dnd", guild=ctx.guild) and (not await userPostedRecently(ctx.channel, user, 5)):
			await ctx.send("This user has DND enabled and hasn't spoken recently (In this channel), this game can not be started, ask them to join you first.")
			return False
		return True

	@commands.command()
	@commands.cooldown(1, 20)
	async def fight(self, ctx, user1:discord.Member=None, user2:discord.Member=None):
		if user1 == None:
			v1 = ctx.author
			v2 = ctx.guild.get_member(self.client.user.id)
		elif user2 == None:
			v1 = ctx.author
			v2 = user1
			if not await self.canPlay(ctx, v2):
				return
		else:
			v1 = user1
			v2 = user2
			if not (await self.canPlay(ctx, v1) and await self.canPlay(ctx, v2)):
				return

		await self.FightNewgame(ctx, self.client, v1, v2, 100, 10)
			
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
					fightButton("Punch (" + str(math.ceil(player[turn]["energy"] / 2)) + ")", "punch", "👊",  timeout),
					fightButton("Slap (0)",                                                   "slap",  "✋",  timeout),
					fightButton("Heal (x" + str(player[turn]["heals"]) + ")",                 "heal",  "🍷",   timeout),
					fightButton("Wait (-1)",                                                  "wait",  "🕓",  timeout),
					fightButton("Flee",                                                       "flee",  "❌",  timeout)
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
				action = None
					
				# flee (aka quit the game)
				if move == "❌":
					await MSG.delete()
					await ctx.send(f"{name1} fled!\nGG {name2}!!!")
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

	@commands.command()
	@commands.cooldown(1, 3)
	async def fighthelp(self, ctx):
		emb = getComEmbed(ctx, self.client, "Fight Help", f"How to fight (like a boss)", "Fight is the oldest game and is still up there as my most complex command, here is how to play it properly.", fields=[["**Understanding energy:**","Energy determines how much power a punch has, at max power it'll deal a mighty blow. The number next to each button shows how much energy it'll take up, spesific actions may even give you more energy, like __Wait__."],["**Heals:**","Each game starts you out with 2 heals, Each gives 50 health. This is currently the only way to heal so use them wisely."],["**Punches and Slaps**:","Punches are better when your energy is high, and remeber that punching halves your energy. Slaps however are weaker but only take 1 energy."],["**Main Stratergy:**","The stratergy that I use on the rare occdasion I play the game is to only use wait. Punching when my energy is at least 8, Healing when my health is below the maximum damage [60], Using slaps is uncommon but if you want to incorporate them go ahead!"]])
		await ctx.reply(embed=emb, mention_author=False)

	### RPS ###

	@commands.command()
	@commands.cooldown(1, 8)
	async def rps(self, ctx, user1:discord.Member=None, user2:discord.Member=None):
		if user1 == None:
			v1 = ctx.author
			v2 = ctx.guild.get_member(self.client.user.id)
		elif user2 == None:
			v1 = ctx.author
			v2 = user1
			if not await self.canPlay(ctx, v2):
				return
		else:
			v1 = user1
			v2 = user2
			if not (await self.canPlay(ctx, v1) and await self.canPlay(ctx, v2)):
				return

		await self.RPSNewgame(ctx, self.client, v1, v2)

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

	### Worble ###

	@commands.command(aliases=["wordle"])
	@commands.cooldown(1, 8)
	async def worble(self, ctx):
		tries = 7
		attry = 0
		grid, trywords = [], []
		for i in range(1, tries+1):
			grid.append(":black_large_square::black_large_square::black_large_square::black_large_square::black_large_square::black_large_square:")
			trywords.append("------")

		startdate = datetime.date(2022, 3, 14)
		todaydate = datetime.date.today()
		newdate = todaydate - startdate
		day = newdate.days
		seed(day)
		word = choice(self.worblewords)

		def worbleEmbed(timeout=False, txt=""):
			command = "Worble"
			if timeout:
				command = "Worble (timeout)"

			emb = getComEmbed(ctx, self.client, command, f"Worble! (Day {day})", txt + "\n(*say giveup to give up*)", fields=[["Grid", "\n".join(grid)], ["Words", "\n".join(trywords)]], inline=True)
			return emb

		emb = worbleEmbed()
		MSG = await ctx.send(embed=emb)

		def check(message):
			return (message.author == ctx.author and message.guild.id == ctx.guild.id and message.channel.id == ctx.channel.id)

		while True:
			try:
				message = await self.client.wait_for("message", timeout=300, check=check)
				tryword = message.content.lower()

				ret = False
				if tryword == "giveup":
					emb = worbleEmbed(True, f"{ctx.author.display_name} gave up. It was ||{word}||.")
					await MSG.edit(embed=emb)
					return
				elif tryword.isalpha() and len(tryword) == 6 and " " not in tryword:
					newgrid = ""
					win = 0

					#"altert", "retire", "entire"
					# gren
					for i in range(0, 6):
						if tryword[i] == word[i]:
							newgrid += ":green_square:"
							win += 1
						elif tryword.count(tryword[i]) <= word.count(tryword[i]) and tryword[i] in word:
							newgrid += ":yellow_square:"
						else:
							newgrid += ":black_large_square:"
							
					grid[attry] = newgrid
					trywords[attry] = f"||{tryword}||"

					if win == 6:
						emb = worbleEmbed(False, f"Word was CORRECT! It was ||{word}||.")
						ret = True
					else:
						attry += 1
						if tries == attry:
							emb = worbleEmbed(False, f"Word was valid but wrong. No more tries remaining. It was ||{word}||.")
							ret = True
						else:
							emb = worbleEmbed(False, f"Word was valid but wrong. {6-win} letters remain unknown.")
				else:
					emb = worbleEmbed(False, "Word was not valid!")

				await message.delete()
				await MSG.edit(embed=emb)
				if ret:
					return
			
			except asyncio.TimeoutError:
				emb = worbleEmbed(True)
				await MSG.edit(embed=emb)
				return

	@commands.command(aliases=["wordlehelp"])
	@commands.cooldown(1, 3)
	async def worblehelp(self, ctx):
		emb = getComEmbed(ctx, self.client, "Worble Help", f"How to worble", "Worble is 100% not based on Wordle but the rules are the same.\n\nYou have 7 tries to guess a word. You type in a 6 letter word and get green squares if the letter is in the word and in the right place, and yellow squares if the letter is in the word but in the wrong place. Black square means it's not in the word.", fields=[["What's valid?", "Any 6 letter word that is just letters (Auto lowercases)"]])
		await ctx.reply(embed=emb, mention_author=False)

def clamp(n, minn, maxn):
	return max(min(maxn, n), minn)

def setup(client):
	client.add_cog(GamesCog(client))