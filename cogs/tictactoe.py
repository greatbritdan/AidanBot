import discord
from discord.ext import commands

import random
import asyncio

from main import add_command
from main import getEmbed, Error, addField

class TTTCog(commands.Cog):
	def __init__(self, client):
		self.client = client

	add_command(["tictactoe", "Games", "ttt", "Play tic-tac-toe.", False])
	@commands.command()
	async def ttt(self, ctx, user1:discord.User=None):
		if user1 == None:
			await Error(ctx, "Missing un-optional argument for command.")
			return

		v1 = ctx.author
		v2 = user1

		await TTTNewgame(ctx, self.client, v1, v2)

async def TTTNewgame(ctx, client, p1:discord.User, p2:discord.User):
	# setup lists
	player = {
		"p1": {
			"name": p1.name,
			"id": p1.id,
			"bot": p1.bot,
			"let": "X"
		},
		"p2": {
			"name": p2.name,
			"id": p2.id,
			"bot": p2.bot,
			"let": "O"
		}
	}
	guildid = ctx.guild.id
	channelid = ctx.channel.id
	movelist = ["a1", "a2", "a3", "b1", "b2", "b3", "c1", "c2", "c3"]
	grid = {
		"a": {"1": " ", "2": " ", "3": " "},
		"b": {"1": " ", "2": " ", "3": " "},
		"c": {"1": " ", "2": " ", "3": " "}
	}

	turn = "p1"
	turnt = "p2"

	# for cheking if the right user send a command in the valid guild and channel
	def check(message):
		return (message.author.id == player[turn]["id"] and message.guild.id == guildid and message.channel.id == channelid)

	# embed for titc tac toe
	def getTTTEmbed(ctx, vic=None):
		if vic:
			emb = getEmbed(ctx, "Tic-Tac-Toe", vic, getTTTGrid())
		else:
			emb = getEmbed(ctx, "Tic-Tac-Toe", player["p1"]["name"] + " VS " + player["p2"]["name"], getTTTGrid())
			emb = addField(emb, player[turn]["name"] + "'s Turn:", f"Valid moves: {movelist}")

		return emb

	# gets the grid
	def getTTTGrid():
		return player["p1"]["name"] + ": " + player["p1"]["let"] + "\n" + player["p2"]["name"] + ": " + player["p2"]["let"] + "\n" + "```\n  1   2   3   \na {0} | {1} | {2}\n  --+---+--\nb {3} | {4} | {5}\n  --+---+--\nc {6} | {7} | {8}\n```".format(grid["a"]["1"], grid["a"]["2"], grid["a"]["3"], grid["b"]["1"], grid["b"]["2"], grid["b"]["3"], grid["c"]["1"], grid["c"]["2"], grid["c"]["3"])

	embed = getTTTEmbed(ctx)
	MSG = await ctx.send(embed=embed)

	# the main loop
	playing = True
	win = False
	while playing:
		# waits for the correct message to be sent
		try:
			if player[turn]["bot"]:
				message = None
				move = random.choice(movelist)

				await asyncio.sleep(1.5)
			else:
				message = await client.wait_for("message", timeout=60, check=check)
				move = message.content

			if move in movelist:
				grid[move[0]][move[1]] = player[turn]["let"]
				movelist.remove(move)

			if message:
				await message.delete()

			# check for win
			if grid["a"]["1"] == grid["a"]["2"] == grid["a"]["3"] != " ":
				win = turn
			elif grid["b"]["1"] == grid["b"]["2"] == grid["b"]["3"] != " ":
				win = turn
			elif grid["c"]["1"] == grid["c"]["2"] == grid["c"]["3"] != " ":
				win = turn
			elif grid["a"]["1"] == grid["b"]["1"] == grid["c"]["1"] != " ":
				win = turn
			elif grid["a"]["2"] == grid["b"]["2"] == grid["c"]["2"] != " ":
				win = turn
			elif grid["a"]["3"] == grid["b"]["3"] == grid["c"]["3"] != " ":
				win = turn
			elif grid["a"]["1"] == grid["b"]["2"] == grid["c"]["3"] != " ":
				win = turn
			elif grid["a"]["3"] == grid["b"]["2"] == grid["c"]["1"] != " ":
				win = turn
			else:
				if len(movelist) == 0:
					win = "draw"

			# wow we can end this
			if win:
				playing = False
				break

			# swap turn
			oldturn = turn
			turn = turnt
			turnt = oldturn

			# update embed
			embed = getTTTEmbed(ctx)
			await MSG.edit(embed=embed)

		# if no message is sent in a miniue, it's a draw
		except asyncio.TimeoutError:
			win = "timeout"
			playing = False
			break

	# victory message
	if win == "timeout":
		embed = getTTTEmbed(ctx, "Timeout.")
	elif win == "draw":
		embed = getTTTEmbed(ctx, "It was a draw!")
	else:
		embed = getTTTEmbed(ctx, "GG " + player[win]["name"] + "!!!")
	await MSG.edit(embed=embed)

def setup(client):
  client.add_cog(TTTCog(client))