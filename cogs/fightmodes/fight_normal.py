from discord import ButtonStyle as Style

import math
from random import randint, choice

from cogs.fightmodes.fight_base import FightPlayer, FightManager, FightValue, FightMove, FightButton, FightGeneral

punch_damage = [8,18,30]
combo_damage_1 = [0,8,18]
combo_damage_2 = [0,18,30]
heal_gain = [10,25,40]

### Funcs ###

def update(manager:FightManager, move:str, turn:FightPlayer, turnt:FightPlayer):
	if move == "punch" or move == "combo":
		turn.multiplier = 1
	if move != "punch" and move != "combo" and move != "comboend":
		if turn.energy < 3 and move != "defend":
			turn.energy += 1
		if turnt.defending and move != "pierce" and move != "kamikaze":
			turnt.energy = min(turnt.energy+2, 3)
			turnt.multiplier += 0.5
	elif turnt.mp < 3 and move != "defend":
		turnt.mp += 1
	if turnt.defending:
		turnt.defending = False
### AI ###

def makeMoveEasy(player:FightPlayer): # oldfights ai but made for newfight
	if player.mp > 0 and player.health <= player.energy*25 and randint(0,3) < player.energy: return "heal"
	elif player.energy == 3 or (player.energy == 2 and randint(1,2) == 2) or (player.energy == 1 and randint(1,3) == 3): return "punch"
	else: return "wait"
def makeMoveMedium(player:FightPlayer): # like easy but understands new moves
	if player.energy > 0:
		if player.enemy.multiplier >= 2 and randint(1,4) != 4: return "defend"  # 75%
		if player.enemy.defending and randint(1,3) != 3: return "punch" # 66.6%
		if player.energy == 2 and player.health > 50 and randint(1,2) == 2: return "combo" # 50%
		if player.energy == 3 or randint(1,3) == 3: return "punch" # 33.3%
	if player.mp > 0:
		if player.mp == 3 and player.enemy.health <= 50: return "kamikaze"
		if player.mp == 2 and (player.enemy.defending or player.enemy.mp > 1) and randint(1,2) == 2: return "pierce" # 50%
		if player.mp == 1 and (player.health >= 40 or randint(1,3) == 3): return "attack_up" # 33.3%
		if player.health <= player.energy*25 and randint(0,3) < player.energy: return "heal"
	return "wait"
def makeMoveHard(player:FightPlayer): # doesn't take any chances
	enemyhd, ushd, ushdplus = player.enemy.getDamageAt(punch_damage), player.getDamageAt(punch_damage), player.getDamageAt(punch_damage,player.multiplier+0.5)
	if enemyhd >= player.health:
		if (player.mp == 3 or (player.energy == 0 and player.mp > 0)) and randint(1,2) == 2: return "heal" # 50%
		if player.energy > 0: return "defend"
	if player.energy > 0:
		if player.energy > 1 and player.enemy.health <= player.getDamageAt(combo_damage_1)+player.getDamageAt(combo_damage_2,1): return "combo"
		if player.enemy.health <= player.getDamageAt(punch_damage) or player.energy == 3: return "punch"
	if player.energy > 0 and (not player.enemy.nextturn == "comboend") and player.enemy.energy == 0: return "defend"
	if player.mp == 3 and player.enemy.health <= 50: return "kamikaze"
	if player.mp == 2 and (15 > ushd or (player.enemy.mp > 1 and 10 > ushd)): return "pierce"
	if player.mp == 1 and ushdplus >= player.enemy.health: return "attack_up"
	return "wait"	
def makeMoveRandom(player:FightPlayer):
	opt = ["wait"]
	if player.energy > 0: opt.append("punch"); opt.append("defend")
	if player.energy > 1: opt.append("combo")
	if player.mp == 1: opt.append("attack_up")
	if player.mp == 2: opt.append("pierce")
	if player.mp == 3: opt.append("kamikaze")
	if player.mp > 0: opt.append("heal")
	return choice(opt)

### Moves ###

def punch(turn:FightPlayer, turnt:FightPlayer, butid):
	damage = turn.getDamage(punch_damage[turn.energy-1])
	turnt.health, turn.energy = turnt.health-damage, 0

def combo(turn:FightPlayer, turnt:FightPlayer, butid):
	damage = turn.getDamage(combo_damage_1[turn.energy-1])
	turn.nextturn, turn.nextturnsave = "comboend", turn.energy
	turnt.health, turn.energy = turnt.health-damage, turn.energy-2

def comboend(turn:FightPlayer, turnt:FightPlayer, butid):
	damage = turn.getDamage(combo_damage_2[turn.nextturnsave-1])
	turnt.health, turn.nextturn, turn.nextturnsave = turnt.health-damage, False, 0

def defend(turn:FightPlayer, turnt:FightPlayer, butid):
	turn.defending, turn.energy = True, turn.energy-1

def attack_up(turn:FightPlayer, turnt:FightPlayer, butid):
	turn.multiplier, turn.mp = turn.multiplier+0.5, turn.mp-1

def pierce(turn:FightPlayer, turnt:FightPlayer, butid):
	turnt.health, turn.mp, turnt.mp = turnt.health-15, turn.mp-2, turnt.mp-1

def kamikaze(turn:FightPlayer, turnt:FightPlayer, butid):
	turn.health, turnt.health, turn.mp = turn.health-50, turnt.health-50, turn.mp-3

def heal(turn:FightPlayer, turnt:FightPlayer, butid):
	gain = heal_gain[turn.mp-1]
	turn.health, turn.mp = turn.health+gain, 0

### The Stuffs ###

values = [
	FightValue(name="health",     display_name="Health",     default=100, min=0,   max=100,   ui="{bar} **({val})**", bar=[10,"blue",True]),
	FightValue(name="energy",     display_name="Energy",     default=2,   min=0,   max=3,     ui="{bar} **({val})**", bar=[3,"red",False]),
	FightValue(name="mp",         display_name="MP",         default=2,   min=0,   max=3,     ui="{bar} **({val})**", bar=[3,"red",False]),
	FightValue(name="multiplier", display_name="Multiplier", default=1,   min=0.5, max=2.5,   ui="**x{val:.1f}**",    changestyle="new"),
]

moves = [
	FightMove(name="punch",     display_name="Punch",      call=punch,     death="{turn} punched {turnt} into oblivion!"),
	FightMove(name="combo",     display_name="Combo",      call=combo,     death="{turnt} couldn't even handle half of {turn}'s combo!"),
	FightMove(name="comboend",  display_name="Combo End",  call=comboend,  death="{turnt} got combo'd right in the gut by {turn}!"),
	FightMove(name="defend",    display_name="Defend",     call=defend),
	FightMove(name="attack_up", display_name="Attack-up",  call=attack_up),
	FightMove(name="pierce",    display_name="Pierce",     call=pierce,    death="{turn} pierced {turnt} in the heart!"),
	FightMove(name="kamikaze",  display_name="Kamikaze",   call=kamikaze,  death="{turnt} was crippled by {turn}'s kamikaze!", deathself="{turnt} was destroyed by their own kamikaze, {turn} was confused."),
	FightMove(name="heal",      display_name="Heal",       call=heal),
]

buttons = [
	FightButton(name="punch",     label="Punch",     emoji="👊", style=Style.red,     move="punch",  ui="[{maxval}]", condition="energy|>|0"),
	FightButton(name="combo",     label="Combo",     emoji="⛓️", style=Style.red,     move="combo",  ui="[{maxval}]", condition="energy|>|1"),
	FightButton(name="defend",    label="Defend",    emoji="🛡️", style=Style.red,     move="defend", ui="[{cval}]",   condition="energy|>|0"),
	FightButton(name="wait",      label="Wait",      emoji="🕐", style=Style.gray,    move="wait"),
	FightButton(name="flee",      label="Flee",      emoji="✖️", style=Style.gray,    move="flee"),
	FightButton(name="attack_up", label="Attack-Up", emoji="⏫", style=Style.blurple, move="attack_up", row=1, ui="[{cval}]",   condition="mp|=|1"),
	FightButton(name="pierce",    label="Pierce",    emoji="📍", style=Style.blurple, move="pierce",    row=1, ui="[{cval}]",   condition="mp|=|2"),
	FightButton(name="kamikaze",  label="Kamikaze",  emoji="💥", style=Style.blurple, move="kamikaze",  row=1, ui="[{cval}]",   condition="mp|=|3"),
	FightButton(name="heal",      label="Heal",      emoji="🍷", style=Style.green,   move="heal",      row=1, ui="[{maxval}]", condition="mp|>|0"),
]

general = FightGeneral(update=update, easy=makeMoveEasy, medium=makeMoveMedium, hard=makeMoveHard, random=makeMoveRandom)

def startFightNormal(user1, user2, aiuser1, aiuser2):
	return FightManager(user1, user2, aiuser1, aiuser2, values, moves, buttons, general)