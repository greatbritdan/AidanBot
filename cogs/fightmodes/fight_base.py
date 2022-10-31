import discord
from discord import ButtonStyle as Style
from discord import Interaction as Itr

import math

from aidanbot import AidanBot
from functions import getBar, getComEmbed

def clamp(n, minn, maxn):
	return max(min(maxn, n), minn)

###

class FightValue():
	def __init__(self, name:str, default:int, min:int=None, max:int=None, display_name:str=None, ui:str=False, bar:list=False, changestyle:str="diff"):
		self.name = name
		self.display_name = display_name or name

		self.default = default
		self.min = min
		self.max = max
		self.ui = ui
		self.bar = bar
		self.changestyle = changestyle

class FightMove():
	def __init__(self, name:str, display_name:str=None, call=None, ui:str=None, death:str=None, deathself:str=None):
		self.name = name
		self.display_name = display_name or name
		self.call = call

		self.ui = ui or "{turn} used {name}"
		self.death = death or "{turn} killed {turnt}."
		self.deathself = deathself

class FightButton():
	def __init__(self, name:str, label:str=None, emoji:str=None, style:Style=None, row:int=0, move:str=False, ui:str=False, condition:str=None, dynamic=None, dynamicmove=None):
		self.name = name
		self.label = label or name
		self.emoji = emoji
		self.style = style
		self.row = row

		self.move = move
		self.ui = ui
		self.condition = condition
		self.dynamic = dynamic
		self.dynamicmove = dynamicmove

class FightGeneral():
	def __getitem__(self, key):
		return getattr(self, key)
	def __init__(self, update, easy=None, medium=None, hard=None, random=None, noai=False):
		self.update = update
		self.easy = easy
		self.medium = medium
		self.hard = hard
		self.random = random
		self.noai = noai

###

defaultmoves = [
	FightMove(name="wait", display_name="Wait"),
	FightMove(name="flee", display_name="Flee", death="{turn} fled like a baby!")
]

class FightPlayer():
	def __setitem__(self, key, value):
		setattr(self, key, value)
	def __getitem__(self, key):
		return getattr(self, key)

	def __init__(self, core, user:discord.Member, id:int, ailevel:str, values:list[FightValue]):
		self.core = core
		self.user = user
		self.id = user.id
		self.bot = user.bot
		self.enemy:FightPlayer = None

		# used vars for formatting
		self.health, self.energy, self.heals, self.mp, self.multiplier = 0,0,0,0,0
		self.card1, self.card2, self.card3, self.card4 = 0,0,0,0
		self.deck, self.modify = False, False
		self.defending, self.healing, self.meditated = False, False, False
		self.nextturn, self.nextturnsave, self.continueturn = False, 0, False
	
		self.before = False

		self.ailevel = ailevel
		self.playerid = id
		self.values = values
		for v in self.values:
			self[v.name] = v.default

	@property
	def name(self):
		if self.enemy.user == self.user:
			return self.user.display_name+f" [{self.playerid}]"
		else:
			return self.user.display_name
	@property
	def UI(self):
		ui = ""
		maxw = 0
		for v in self.values:
			if len(v.name) > maxw: maxw = len(v.name)
		for v in self.values:
			if v.ui:
				ui += "`{1:<{0}}`: ".format(maxw,v.name)
				bar = "<no bar arg>"
				if v.bar:
					bar = getBar(self[v.name],v.max,v.bar[0],v.bar[2],color=v.bar[1])
				ui += v.ui.format(bar=bar, val=self[v.name]) + "\n"
		return [f"{self.name} Stats:", ui]
	
	def getValueData(self, name):
		for v in self.values:
			if v.name == name:
				return v
		return False
	def getStats(self):
		sdict = {}
		for v in self.values:
			sdict[v.name] = self[v.name]
		return sdict

	def clamp(self):
		for v in self.values:
			if v.min != None and v.max != None:
				self[v.name] = clamp(self[v.name], v.min, v.max)
	
	### Fight Normal Things, Remove?
	def getDamage(self, value, multi=None):
		multi = multi if multi else self.multiplier
		dmg = value * multi
		if self.enemy.defending: dmg /= 2
		return math.floor(dmg)
	def getDamageAt(self, values, multi=None):
		return self.getDamage(values[self.energy-1], multi)
				
class FightManager():
	def __init__(self, user1:discord.Member, user2:discord.Member, aiuser1:str, aiuser2:str, playerdata:FightGeneral, movedata:list, buttondata:list, generaldata:list):
		self.player1, self.player2 = FightPlayer(self,user1,"1",aiuser1,playerdata), FightPlayer(self,user2,"2",aiuser2,playerdata)
		self.player1.enemy, self.player2.enemy = self.player2, self.player1
		self.moves = FightMoves(self, movedata, buttondata)

		self.turnid = 1
		self.actions = None
		self.modify = False
		self.data = generaldata

		self.turn.before, self.turnt.before = self.turn.getStats(), self.turnt.getStats()
	
	@property
	def turn(self):
		if self.turnid == 1:
			return self.player1
		return self.player2
	@property
	def turnt(self):
		if self.turnid == 1:
			return self.player2
		return self.player1
	def swapTurn(self):
		self.turnid = 1 if self.turnid == 2 else 2
		return self.turn, self.turnt
	
	def getEmbed(self, itr:Itr, client:AidanBot, turn:FightPlayer, timeout=False):
		title = f"{self.player1.name} VS {self.player2.name}"
		fields = [self.player1.UI, self.player2.UI]
		if self.actions:
			fields.append(self.actions)
		if not timeout:
			fields.append([f"{turn.name}'s Turn:", "> Select an action below"])
		return getComEmbed(str(itr.user), client, title, fields=fields), self.moves.getView(timeout)
	def getWinEmbed(self, itr:Itr, client:AidanBot, move:str, turn:FightPlayer, turnt:FightPlayer):
		return getComEmbed(str(itr.user), client, f"{turn.name} won! Tough luck {turnt.name}", self.moves.getDeath(move).format(turn=turn.name, turnt=turnt.name)), self.moves.getView(True)

	def getActionsPlayer(self, actiontxt, player:FightPlayer, playerbefore, playerafter):
		for name in playerbefore.keys():
			v = player.getValueData(name)
			if v:
				if v.changestyle == "diff":
					if playerbefore[name] < playerafter[name]:
						gain = playerafter[name] - playerbefore[name]
						actiontxt += f"> {player.name} gained {gain} {name}\n"
					elif playerbefore[name] > playerafter[name]:
						loss = playerbefore[name] - playerafter[name]
						actiontxt += f"> {player.name} lost {loss} {name}\n"
				elif v.changestyle == "new":
					if playerbefore[name] != playerafter[name]:
						actiontxt += f"> {player.name}'s {name} changed to {playerafter[name]}\n"
				elif v.changestyle == "use":
					if playerbefore[name] != playerafter[name]:
						if playerafter[name] == 0:
							actiontxt += f"> {player.name} used {name}, that was their last.\n"
						else:
							actiontxt += f"> {player.name} used {name}\n"
		return actiontxt

	def getActions(self, move, turn:FightPlayer, turnt:FightPlayer, turnbefore, turntbefore, turnafter, turntafter):
		movedata = self.moves.getMove(move)
		actions = [movedata.ui.format(turn=turn.name, name=movedata.display_name)]
		actiontxt = ""
		actiontxt = self.getActionsPlayer(actiontxt, turn, turnbefore, turnafter)
		actiontxt = self.getActionsPlayer(actiontxt, turnt, turntbefore, turntafter)
		if actiontxt == "":
			actions.append("Nothing changed.")
		else:
			actions.append(actiontxt)
		self.actions = actions

	def useMove(self, move, butid):
		turn, turnt = self.turn, self.turnt
		if move != "wait":
			self.moves.useMove(move, butid)
		if turn.continueturn:
			turn.clamp(); turnt.clamp()
		else:
			self.data.update(self, move, turn, turnt)
			turn.clamp(); turnt.clamp()
			turnafter, turntafter = turn.getStats(), turnt.getStats()
			self.getActions(move, turn, turnt, self.turn.before, self.turnt.before, turnafter, turntafter)
			self.turn.before, self.turnt.before = turn.getStats(), turnt.getStats()

		if turnt.health <= 0:
			return True, move
		elif turn.health <= 0:
			return True, move+"-killself"
		else:
			return False, False
	
	def userMoveAI(self):
		if self.data.noai: return "wait"
		if self.turn.nextturn:
			return "-"
		elif self.turn.ailevel == "dead":
			return "wait"
		else:
			return self.data[self.turn.ailevel](self.turn)

class FightMoves():
	def __setitem__(self, key, value):
		setattr(self, key, value)
	def __getitem__(self, key):
		return getattr(self, key)

	def __init__(self, core:FightManager, moves:list[FightMove], buttons:list[FightButton]):
		self.core = core
		self.moves = moves+defaultmoves
		self.buttons = buttons

	def getView(self, timeout=False):
		turn, turnt = self.core.turn, self.core.turnt
		timeout = True if timeout or turn.nextturn or turn.bot else False

		view = discord.ui.View(timeout=None)
		for b in self.buttons:
			con = b.condition
			skip, name, func, val = False, "", "", 0
			if con:
				skip = True
				con = con.split("|")
				name, func, val = con[0], con[1], int(con[2])
				value = turn[name]
				if func == ">":
					val+=1 
					if value > val:
						skip = False
				if func == "=" and value == val:
					skip = False
			
			butname, butstyle, butdisable = b.label, b.style, (timeout or skip)
			if b.dynamic:
				butname, butstyle, butdisable = b.dynamic(b.name, turn, turnt)
				butdisable = (timeout or butdisable)

			if b.ui:
				print(value,val)
				view.add_item(discord.ui.Button( style=butstyle, label=f"{butname} "+b.ui.format(cval=val, val=value, maxval=max(value,val)), custom_id=b.name, row=b.row, disabled=butdisable, emoji=b.emoji))
			else:
				view.add_item(discord.ui.Button( style=butstyle, label=butname, custom_id=b.name, row=b.row, disabled=butdisable, emoji=b.emoji))
		return view

	def getMoveFromButton(self, name, turn, turnt):
		for b in self.buttons:
			if name == b.name:
				move = b.move
				if b.dynamicmove:
					move = b.dynamicmove(move, turn, turnt)
				return b.move
		return "wait"
	def getMove(self, move):
		for m in self.moves:
			if move == m.name:
				return m
		return False
	def useMove(self, move, butid):
		m = self.getMove(move)
		if m:
			return m.call(self.core.turn, self.core.turnt, butid)
	def getDeath(self, move):
		for m in self.moves:
			if move == m.name and m.death:
				return m.death
			elif move == m.name+"-killself" and m.deathself:
				return m.deathself
		return "{turnt} killed {turn}."
