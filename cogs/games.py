import discord
from discord.commands import SlashCommandGroup
from discord import Option, ButtonStyle
from discord.ui import View, Button

import asyncio, math
from random import randint, choice
from functions import getComEmbed, getBar, userPostedRecently

punch_damage = [8,18,30]
combo_damage_1 = [0,8,18]
combo_damage_2 = [0,18,30]
heal_gain = [5,10,25]

class GamesCog(discord.Cog):
	def __init__(self, client):
		self.client = client

	async def canPlay(self, ctx, user):
		# not a bot and dnd enabled and no messages in last 5 messages.
		if (not user.bot) and self.client.UCON.get_value(user, "dnd", guild=ctx.guild) and (not await userPostedRecently(ctx.channel, user, 5)):
			await ctx.respond("This user has DND enabled and hasn't spoken recently (In this channel), this game can not be started, ask them to join you first.")
			return False
		return True

	gamesgroup = SlashCommandGroup("games", "All Games.")

	@gamesgroup.command(name="rps", description="Rock, paper, scissors!")
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
				"name": player1.display_name, "id": player1.id, "bot": player1.bot,
				"pick": ""
			},
			"p2": {
				"name": player2.display_name, "id": player2.id, "bot": player2.bot,
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

# Fight Base
	async def fightBase(self, ctx, player1, player2, Button_func, Move_func):
		PLAYER1, PLAYER2 = player1, player2

		turn, turnt, win, wint, causeofded = False, False, False, False, ""
		def getFightEmbed(disabled=None, timeout=None, win=None, wint=None, action=None):
			disabled = True if disabled or turn.disableMove() else False
			view = Button_func(turn, disabled)

			if win:
				return getComEmbed(ctx, self.client, f"{win.name} Won The Battle!!!", f"{causeofded}".format(win=win.name, wint=wint.name)), view
			else:
				title = f"{PLAYER1.name} VS {PLAYER2.name}"
				if timeout: title = f"[Timeout] {title}"
				fields = [PLAYER1.getUI(), PLAYER2.getUI()]
				if action: fields.append(action)
				fields.append([f"{turn.name}'s Turn:", "Select an action below "])
				return getComEmbed(ctx, self.client, title, fields=fields), view
				
		turn, turnt = PLAYER1, PLAYER2
		embed, view = getFightEmbed()
		response = await ctx.respond(embed=embed, view=view)
		msg = await response.original_message()
		
		def check(interaction:discord.Interaction):
			return (interaction.user.id == turn.user.id and interaction.message.id == msg.id)
		
		while True:
			try:
				skip = turn.specialMove()
				if skip:
					id = skip
					await asyncio.sleep(2.5)
				else:
					if turn.bot:
						id = turn.makeMove()
						await asyncio.sleep(2.5)
					else:
						interaction = await self.client.wait_for("interaction", check=check, timeout=180)
						await interaction.response.defer()
						id = interaction.custom_id

				changes, movefailed = Move_func(id, turn, turnt)
				if movefailed:
					if id == "flee": win, wint, causeofded = turnt, turn, "flee"; break
					else: id = "error"

				turn.clamp(); turnt.clamp()
				if turnt.health == 0: win, wint, causeofded = turn, turnt, id; break
				if turn.health == 0: win, wint, causeofded = turnt, turn, "killedyourself"; break

				action = None
				if id == "error":
					action = ["And error occurred!", "Please try again."]
				else:
					action = self.fightChanges(changes, id, turn, turnt)
				
				if id != "error":
					oldturn = turn
					turn, turnt = turnt, oldturn

				embed, view = getFightEmbed(action=action)
				await ctx.edit(embed=embed, view=view)
			except asyncio.TimeoutError:
				win = "timeout"
				break
	
		embed, view = None, None
		if win == "timeout":
			embed, view = getFightEmbed(disabled=True, timeout=True)
		else:
			deathmessages = {
				"punch": "{win} punched {wint} into oblivion.",
				"slap": "{win} was destryed by {wint}'s mega slap.",
				"combo": "{wint} couldn't even handle half of {win}'s combo.",
				"comboend": "{wint} got combo'd right in the gut by {win}.",
				"pierce": "{win} pierced {wint} in the heart.",
				"killedyourself": "{wint} was destroyed by their own kamikaze, {win} was confused.",
				"kamikaze": "{wint} was crippled by {win}'s kamikaze.",
				"flee": "{wint} fled like a baby!"
			}
			causeofded = deathmessages[causeofded]
			embed, view = getFightEmbed(disabled=True, win=win, wint=wint)
		await ctx.edit(embed=embed, view=view)

	def fightChanges(self, changes, id, turn, turnt):
		action = [f"{turn.name} used {id}!"]
		if id == "comboend":
			action = [f"{turn.name} finished combo!"]
		elif id == "heal" and (turn.heals != False) and turn.heals == 0:
			action = [f"{turn.name} used {id}, That was their last..."]

		if len(changes) > 0:
			txt = ""
			for change in changes:
				target = turn if change[0] == "turn" else turnt
				match change[1]:
					case "health-": txt += f"{target.name} Lost **{change[2]} Health**.\n"
					case "health+": txt += f"{target.name} Gained **{change[2]} Health**.\n"
					case "energy-": txt += f"{target.name} Lost **{change[2]} Energy**.\n"
					case "energy+": txt += f"{target.name} Gained **{change[2]} Energy**.\n"
					case "mp-": txt += f"{target.name} Lost **{change[2]} MP**.\n"
					case "mp+": txt += f"{target.name} Gained **{change[2]} MP**.\n"
					case "multipliers": txt += f"{target.name}'s Multipliers set to **x{target.multiplier}**.\n"
			action.append(txt)
		else:
			action.append("Nothing changed.")
		return action

	# ACCTUAL COMMANDS #

	@gamesgroup.command(name="fight", description="Fight against another user or one of the main AI levels.")
	async def fight(self, ctx, 
		player1:Option(discord.Member, "First fighter.", required=True),
		player2:Option(discord.Member, "Second fighter.", required=True),
		level:Option(str, "Bot AI level.", choices=["dead","random","easy","medium","hard","rigged"], default="medium"),
		level1:Option(str, "Player 1 Bot AI level. Overides master AI level", choices=["dead","random","easy","medium","hard","rigged"], required=None),
		level2:Option(str, "Player 2 Bot AI level. Overides master AI level", choices=["dead","random","easy","medium","hard","rigged"], required=None)
	):
		if not ((ctx.author == player1 or await self.canPlay(ctx, player1)) and (ctx.author == player2 or await self.canPlay(ctx, player2))):
			return

		level1, level2 = level1 or level, level2 or level
		player1c, player2c = None, None
		if player1 == player2:
			player1c, player2c = fightUser(player1, level1, "1"), fightUser(player2, level2, "2")
		else:
			player1c, player2c = fightUser(player1, level1), fightUser(player2, level2)
		player1c.enemy, player2c.enemy = player2c, player1c

		def Button_func(turn, disabled):
			all, allm = turn.energy, turn.mp
			onem, twom, onemmp, one, two, three = (all < 1), (all < 2), (allm < 1), (allm != 1), (allm != 2), (allm != 3)
			return View(
				Button( style=ButtonStyle.red,     label=f"Punch [{max(all,1)}]", row=1, disabled=(disabled or onem),   custom_id="punch",     emoji="👊" ),
				Button( style=ButtonStyle.red,     label=f"Combo [2]",            row=1, disabled=(disabled or twom),   custom_id="combo",     emoji="⛓️" ),
				Button( style=ButtonStyle.red,     label=f"Defend [1]",           row=1, disabled=(disabled or onem),   custom_id="defend",    emoji="🛡️" ),
				Button( style=ButtonStyle.gray,    label=f"Wait",                 row=1, disabled=disabled,             custom_id="wait",      emoji="🕐" ),
				Button( style=ButtonStyle.gray,    label=f"Flee",                 row=1, disabled=disabled,             custom_id="flee",      emoji="✖️" ),
				Button( style=ButtonStyle.blurple, label=f"Attack Up [1]",        row=2, disabled=(disabled or one),    custom_id="attack-up", emoji="⏫" ),
				Button( style=ButtonStyle.blurple, label=f"Pierce [2]",           row=2, disabled=(disabled or two),    custom_id="pierce",    emoji="📍"  ),
				Button( style=ButtonStyle.blurple, label=f"Kamikaze [3]",         row=2, disabled=(disabled or three),  custom_id="kamikaze",  emoji="💥" ),
				Button( style=ButtonStyle.green,   label=f"Heal [{max(allm,1)}]", row=2, disabled=(disabled or onemmp), custom_id="heal",      emoji="💓" )
			)

		def Move_func(id, turn, turnt):
			changes = []
			# Move Stuff
			match id:
				case "wait":
					changes = []
				case "punch":
					damage, energyloss = turn.getDamage(punch_damage[turn.energy-1]), turn.energy
					turnt.health, turn.energy = turnt.health-damage, 0
					changes = [["turnt","health-",damage],["turn","energy-",energyloss]]
				case "combo":
					damage = turn.getDamage(combo_damage_1[turn.energy-1])
					turnt.health, turn.comboing, turn.energy = turnt.health-damage, turn.energy, turn.energy-2
					changes = [["turnt","health-",damage],["turn","energy-",2]]
				case "comboend":
					damage = turn.getDamage(combo_damage_2[turn.comboing-1])
					turnt.health, turn.comboing = turnt.health-damage, False
					changes = [["turnt","health-",damage]]
				case "defend":
					turn.defending, turn.energy = True, turn.energy-1
					changes = [["turn","energy-",1]]
				case "attack-up":
					turn.multiplier, turn.mp = turn.multiplier+0.5, turn.mp-1
					changes = [["turn","multipliers"],["turn","mp-",1]]
				case "pierce":
					turnt.health, turn.mp, turnt.mp = turnt.health-15, turn.mp-2, turnt.mp-1
					changes = [["turnt","health-",15],["turnt","mp-",1],["turn","mp-",2]]
				case "kamikaze":
					turn.health, turnt.health, turn.mp = turn.health-50, turnt.health-50, turn.mp-3
					changes = [["turn","health-",50],["turnt","health-",50],["turn","mp-",3]]
				case "heal":
					gain, loss = heal_gain[turn.mp-1], turn.mp
					turn.health, turn.mp = turn.health+gain, 0
					changes = [["turn","health+",gain],["turn","mp-",loss]]
				case _: # Failed move
					return [], True

			# Logic Stuff
			if id == "punch" or id == "combo":
				if turn.multiplier > 1:
					turn.multiplier = turn.defaultmultiplier
					changes.append(["turn","multipliers"])
			if id != "punch" and id != "combo" and id != "comboend":
				if turn.energy < 3 and id != "defend":
					turn.energy += 1
					changes.append(["turn","energy+",1])
				if turnt.defending and id != "pierce" and id != "kamikaze":
					turnt.energy = min(turnt.energy+2, 3)
					turnt.multiplier += 0.5
					changes.append(["turnt","energy+",2])
					changes.append(["turnt","multipliers"])
			elif turnt.mp < 3 and id != "defend":
				turnt.mp += 1
				changes.append(["turnt","mp+",1])
			if turnt.defending:
				turnt.defending = False
			return changes, False

		await self.fightBase(ctx, player1c, player2c, Button_func, Move_func)

	@gamesgroup.command(name="fightclassic", description="Fight against another user or one of the main AI levels. Full recreation of the original fight.")
	async def classicfight(self, ctx, 
		player1:Option(discord.Member, "First fighter.", required=True),
		player2:Option(discord.Member, "Second fighter.", required=True),
		level:Option(str, "Bot AI level.", choices=["dead","random","normal"], default="normal"),
		level1:Option(str, "Player 1 Bot AI level. Overides master AI level", choices=["dead","random","normal"], required=None),
		level2:Option(str, "Player 2 Bot AI level. Overides master AI level", choices=["dead","random","normal"], required=None)
	):
		if not ((ctx.author == player1 or await self.canPlay(ctx, player1)) and (ctx.author == player2 or await self.canPlay(ctx, player2))):
			return
			
		player1c, player2c = None, None
		level1, level2 = level1 or level, level2 or level
		if player1 == player2:
			player1c, player2c = fightUserClassic(player1, level1, "1"), fightUserClassic(player2, level2, "2")
		else:
			player1c, player2c = fightUserClassic(player1, level1), fightUserClassic(player2, level2)
		player1c.enemy, player2c.enemy = player2c, player1c

		def Button_func(turn, disabled):
			all, allh = turn.energy, turn.heals
			lowe, noh = (all < 2), (allh == 0)
			return View(
				Button( style=ButtonStyle.red,   label=f"Punch [{math.floor(all/2)}]", disabled=(disabled or lowe), custom_id="punch", emoji="👊" ),
				Button( style=ButtonStyle.red,   label=f"Slap",                        disabled=disabled,           custom_id="slap",  emoji="🖐️" ),
				Button( style=ButtonStyle.green, label=f"Heal [x{allh}]",              disabled=(disabled or noh),  custom_id="heal",  emoji="🍷"  ),
				Button( style=ButtonStyle.gray,  label=f"Wait",                        disabled=disabled,           custom_id="wait",  emoji="🕐" ),
				Button( style=ButtonStyle.gray,  label=f"Flee",                        disabled=disabled,           custom_id="flee",  emoji="✖️" ),
			)

		def Move_func(id, turn, turnt):
			changes = []
			# Move Stuff
			match id:
				case "wait":
					changes = []
				case "punch":
					damage, energyloss = randint((turn.energy*4)-5, (turn.energy*4)+5), math.floor(turn.energy/2)
					turnt.health, turn.energy = turnt.health-damage, turn.energy-energyloss
					changes = [["turnt","health-",damage],["turn","energy-",energyloss]]
				case "slap":
					damage = randint(5,10)
					turnt.health -= damage
					changes = [["turnt","health-",damage]]
				case "heal":
					turn.health, turn.heals = turn.health+50, turn.heals-1 
					changes = [["turn","health+",50]]
				case _:
					return [], True

			# Logic Stuff
			if id != "punch":
				if id == "slap":
					turn.energy += 1
					changes.append(["turn","energy+",1])
				else:
					turn.energy += 2
					changes.append(["turn","energy+",2])
			return changes, False

		await self.fightBase(ctx, player1c, player2c, Button_func, Move_func)

class fightUser():
	def __init__(self, user:discord.Member, level, id=None):
		self.user, self.name, self.bot = user, user.display_name, user.bot
		if id: self.name += f" [{id}]"
		self.level = level
		
		self.health, self.energy, self.mp = 100, 2, 1
		self.heals = False
		self.defaultmultiplier = 1.5 if self.bot and self.level == "rigged" else 1
		self.multiplier = self.defaultmultiplier
		self.comboing, self.defending, self.enemy = False, False, False

	def specialMove(self):
		return "comboend" if self.comboing else False
	def disableMove(self):
		return self.comboing
	def clamp(self):
		self.health, self.energy, self.mp = clamp(self.health,0,100), clamp(self.energy,0,3), clamp(self.mp,0,3)
	def getUI(self):
		return [f"{self.name} Stats:", f'''
		`Health    :` {getBar(self.health,100,10,True)} **({self.health})**
		`Energy/MP :` {getBar(self.energy,3,3,False,'red')} / {getBar(self.mp,3,3,False,'red')}
		`Multiplier:` **x{self.multiplier:.1f}**
		''']

	def getDamage(self, value, multi=None):
		multi = multi if multi else self.multiplier
		dmg = value * multi
		if self.enemy.defending: dmg /= 2 # defending supersedes multiplier
		return math.floor(dmg)
	def getDamageAt(self, values, multi=None): # simulates what damage will be given with punch/combo
		return self.getDamage(values[self.energy-1], multi)

	def makeMove(self):
		if self.comboing: return "-"
		if self.level == "dead": return "wait"
		if self.level == "random": return self.makeMoveRandom()
		if self.level == "easy": return self.makeMoveEasy()
		if self.level == "medium": return self.makeMoveMedium()
		if self.level == "hard" or self.level == "rigged": return self.makeMoveHard()
	def makeMoveEasy(self): # oldfights ai but made for newfight
		if self.mp > 0 and self.health <= self.energy*25 and randint(0,3) < self.energy: return "heal"
		elif self.energy == 3 or (self.energy == 2 and randint(1,2) == 2) or (self.energy == 1 and randint(1,3) == 3): return "punch"
		else: return "wait"
	def makeMoveMedium(self): # like easy but understands new moves
		if self.energy > 0:
			if self.enemy.multiplier >= 2 and randint(1,4) != 4: return "defend"  # 75%
			if self.enemy.defending and randint(1,3) != 3: return "punch" # 66.6%
			if self.energy == 2 and self.health > 50 and randint(1,2) == 2: return "combo" # 50%
			if self.energy == 3 or randint(1,3) == 3: return "punch" # 33.3%
		if self.mp > 0:
			if self.mp == 3 and self.enemy.health <= 50: return "kamikaze"
			if self.mp == 2 and (self.enemy.defending or self.enemy.mp > 1) and randint(1,2) == 2: return "pierce" # 50%
			if self.mp == 1 and (self.health >= 40 or randint(1,3) == 3): return "attack-up" # 33.3%
			if self.health <= self.energy*25 and randint(0,3) < self.energy: return "heal"
		return "wait"
	def makeMoveHard(self): # doesn't take any chances
		enemyhd, ushd, ushdplus = self.enemy.getDamageAt(punch_damage), self.getDamageAt(punch_damage), self.getDamageAt(punch_damage,self.multiplier+0.5)
		if enemyhd >= self.health:
			if (self.mp == 3 or (self.energy == 0 and self.mp > 0)) and randint(1,2) == 2: return "heal" # 50%
			if self.energy > 0: return "defend"
		if self.energy > 0:
			if self.energy > 1 and self.enemy.health <= self.getDamageAt(combo_damage_1)+self.getDamageAt(combo_damage_2,1): return "combo"
			if self.enemy.health <= self.getDamageAt(punch_damage) or self.energy == 3: return "punch"
		if self.energy > 0 and (not self.enemy.comboing) and self.enemy.energy == 0: return "defend"
		if self.mp == 3 and self.enemy.health <= 50: return "kamikaze"
		if self.mp == 2 and (15 > ushd or (self.enemy.mp > 1 and 10 > ushd)): return "pierce"
		if self.mp == 1 and ushdplus >= self.enemy.health: return "attack-up"
		return "wait"
	def makeMoveRandom(self):
		opt = ["wait"]
		if self.energy > 0: opt.append("punch"); opt.append("defend")
		if self.energy > 1: opt.append("combo")
		if self.mp == 1: opt.append("attack-up")
		if self.mp == 2: opt.append("pierce")
		if self.mp == 3: opt.append("kamikaze")
		if self.mp > 0: opt.append("heal")
		return choice(opt)

class fightUserClassic(fightUser):
	def __init__(self, user: discord.Member, level, id=None):
		self.user, self.name, self.bot = user, user.display_name, user.bot
		if id: self.name += f" [{id}]"
		self.level = level
		
		self.health, self.energy, self.heals = 100, 4, 2
		self.enemy = False

	def specialMove(self): return False
	def disableMove(self): return False
	def clamp(self):
		self.health, self.energy = clamp(self.health,0,100), clamp(self.energy,0,10)
	def getUI(self):
		return [f"{self.name} Stats:", f'''
		`Health :` {getBar(self.health,100,10,True)} **({self.health})**
		`Energy :` {getBar(self.energy,10,5,True,'red')} **({self.energy})**
		''']
	
	def makeMove(self):
		if self.level == "dead": return "wait"
		if self.level == "random": return self.makeMoveRandom()
		if self.level == "normal": return self.makeMoveNormal()
	def makeMoveNormal(self):
		if self.heals > 0 and self.health < 50 and  randint(0,math.floor(self.health/15)) == 0: return "heal"
		if self.energy == 9: return "slap"
		if self.energy == 10 or (self.energy == 8 and randint(1,2) == 2): return "punch"
		return "wait"
	def makeMoveRandom(self):
		opt = ["wait","slap"]
		if self.energy > 1: opt.append("punch")
		if self.heals > 0: opt.append("heal")
		return choice(opt)

def clamp(n, minn, maxn):
	return max(min(maxn, n), minn)

def setup(client):
	client.add_cog(GamesCog(client))
