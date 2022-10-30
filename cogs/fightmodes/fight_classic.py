from discord import ButtonStyle as Style

import math
from random import randint, choice

from cogs.fightmodes.fight_base import FightPlayer, FightManager, FightValue, FightMove, FightButton, FightGeneral

### Funcs ###

def update(manager:FightManager, move:str, turn:FightPlayer, turnt:FightPlayer):
	if move == "punch": return
	if move == "slap": turn.energy += 1; return
	turn.energy += 2; return

### AI ###

def makeMoveEasy(player:FightPlayer):
	if player.heals > 0 and player.health <= 50 and max(1,randint(1, math.floor(player.health/10)) == 1): return "heal"
	if player.energy >= 7 and randint(player.energy,10) == 10: return "punch"
	if player.energy >= 4 and randint(1,3) == 1: return "slap"
	return "wait"
def makeMoveHard(player:FightPlayer):
	if player.heals > 0 and player.health <= (player.enemy.energy*4)+5: return "heal"
	if player.energy == 10 or (player.energy*4)+5 >= player.enemy.health: return "punch"
	if player.energy == 9: return "slap"
	return "wait"
def makeMoveRandom(player:FightPlayer):
	opt = ["wait","slap"]
	if player.energy > 0: opt.append("punch")
	if player.heals > 0: opt.append("heal")
	return choice(opt)

### Moves ###

def punch(turn:FightPlayer, turnt:FightPlayer, butid):
	turnt.health -= randint((turn.energy*4)-5, (turn.energy*4)+5); turn.energy -= math.floor(turn.energy/2)

def slap(turn:FightPlayer, turnt:FightPlayer, butid):
	turnt.health -= randint(5,10)

def heal(turn:FightPlayer, turnt:FightPlayer, butid):
	turn.health += 50; turn.heals -= 1

### The Stuffs ###

values = [
	FightValue(name="health", display_name="Health", default=100, min=0, max=100, ui="{bar} **({val})**", bar=[10,"blue",True]),
	FightValue(name="energy", display_name="Energy", default=4,   min=0, max=10,  ui="{bar} **({val})**", bar=[5,"red",True]),
	FightValue(name="heals",  display_name="Heals",  default=2,   min=0, max=2,   ui="**x{val}**", changestyle="use")
]

moves = [
	FightMove(name="punch", display_name="Punch", call=punch, death="{turn} punched {turnt} into oblivion!"),
	FightMove(name="slap",  display_name="Slap",  call=slap, death="{turn} was wrecked by {turnt}'s megaslap!"),
	FightMove(name="heal",  display_name="Heal",  call=heal)
]

buttons = [
	FightButton(name="punch", label="Punch", emoji="👊", style=Style.red,   move="punch", ui="[{maxval}]", condition="energy|>|1"),
	FightButton(name="slap",  label="Slap",  emoji="🖐️", style=Style.red,   move="slap"),
	FightButton(name="heal",  label="Heal",  emoji="🍷",  style=Style.green, move="heal",  ui="[x{val}]",  condition="heals|>|0"),
	FightButton(name="wait",  label="Wait",  emoji="🕐", style=Style.gray,  move="wait"),
	FightButton(name="flee",  label="Flee",  emoji="✖️", style=Style.gray,  move="flee")
]

general = FightGeneral(update=update, easy=makeMoveEasy, hard=makeMoveHard, random=makeMoveRandom)

def startFightClassic(user1, user2, aiuser1, aiuser2):
	return FightManager(user1, user2, aiuser1, aiuser2, values, moves, buttons, general)