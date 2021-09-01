import discord
from discord.ext import commands
from discord.utils import get

import asyncio
import math
from random import randint

from functions import getEmbed, Error, addField, clamp, getBar

class FightCog(commands.Cog):
	def __init__(self, client):
		self.client = client

	@commands.command(description="Fight someone or set 2 others up to fight.\n\nFor more options use `{prefix}fightplus`.")
	async def fight(self, ctx, user1:discord.User=None, user2:discord.User=None):
		if user1 == None:
			await Error(ctx, self.client, "Missing un-optional argument for command.")
			return
		elif user2 == None:
			v1 = ctx.author
			v2 = user1
		else:
			v1 = user1
			v2 = user2

		await FightNewgame(ctx, self.client, v1, v2)

	@commands.command(description="Fight someone or set 2 others up to fight.\n\nNow with extra options!")
	async def fightplus(self, ctx, user1, user2):
		if user1 == None:
			await Error(ctx, self.client, "Missing un-optional argument for command.")
			return
		elif user2 == None:
			v1 = ctx.author
			v2 = user1
		else:
			v1 = user1
			v2 = user2
    
		questions = ["Max & Starter health?", "Max energy?"]
		answers = [100, 10]

		emb = getEmbed(ctx, "fight+ > setup", "N/A", "Type your awnser or `none` to keep default!\nmin is 5, max is 250!")
		MSG = await ctx.send(embed=emb)

		for i in range(0, len(questions)):
			def check(message):
				return (ctx.author == message.author)

			emb = getEmbed(ctx, "fight+ > setup", questions[i] + " (Default: {})".format(answers[i]), "Type your answer or `none` to keep default!")
			await MSG.edit(embed=emb)

			try:
				message = await self.client.wait_for("message", timeout=60, check=check)

				if message:
					if message.content.lower() != "none":
						try:
							answers[i] = int(message.content)
						except ValueError:
							await Error(ctx, self.client, message.content + " is not a valid argument. Needs to be an whole number!")
							return

						answers[i] = clamp(answers[i], 5, 250)

					await message.delete()

			except asyncio.TimeoutError:
				await MSG.delete()
				await ctx.send("Timeout.")
				return

		await MSG.delete()
		await FightNewgame(ctx, self.client, v1, v2, answers[0], answers[1])

async def FightNewgame(ctx, client, p1:discord.User, p2:discord.User, mhealth:int=100, menergy:int=10):
	# setup vars and lists
	maxhealth = mhealth
	maxenergy = menergy
	player = {
		"p1": {
			"name": p1.name,
			"id": p1.id,
			"bot": p1.bot,
			"health": maxhealth,
			"energy": 4,
			"heals": 2
		},
		"p2": {
			"name": p2.name,
			"id": p2.id,
			"bot": p2.bot,
			"health": maxhealth,
			"energy": 4,
			"heals": 2
		}
	}

	turn = "p1"
	turnt = "p2"

	# for cheking if move can be used
	def checkMove(rec, typ, eng=0, con=None):
		if con:
			return (str(rec.emoji) == typ and player[turn]["energy"] >= eng and player[turn]["heals"] > 0)
		else:
			return (str(rec.emoji) == typ and player[turn]["energy"] >= eng)

	# for cheking if the right user uses valid reactions on a spesific message
	def check(rec, user):
		return (user.id == player[turn]["id"] and rec.message.id == MSG.id and (checkMove(rec, "❌", 0) or checkMove(rec, "🕓", 0) or checkMove(rec, "👊", 2) or checkMove(rec, "🍷", 0, True)))

	# embed for the fight command
	def getFightEmbed(ctx, action):
		emb = getEmbed(ctx, "Fight", player["p1"]["name"] + " VS " + player["p2"]["name"], "")
		addField(emb, player["p1"]["name"] + " Stats:", "`Health:` " + getBar(player["p1"]["health"], maxhealth, 10, True) + " (" + str(player["p1"]["health"]) + ")\n`Energy:` " + getBar(player["p1"]["energy"], maxenergy, 5, True) + " (" + str(player["p1"]["energy"]) + ")")
		addField(emb, player["p2"]["name"] + " Stats:", "`Health:` " + getBar(player["p2"]["health"], maxhealth, 10, True) + " (" + str(player["p2"]["health"]) + ")\n`Energy:` " + getBar(player["p2"]["energy"], maxenergy, 5, True) + " (" + str(player["p2"]["energy"]) + ")")

		if action:
			emb = addField(emb, action[0], action[1])

		text = f"🕓: `Wait (+1 Energy)`\n👊: `Attack  (-" + str(math.ceil(player[turn]["energy"] / 2)) + " Energy)`"
		if player[turn]["heals"] > 0:
			text = text + "\n🍷: `Heal (0 Energy) (" + str(player[turn]["heals"]) + " left)`"
		text = text + "\n❌: `Flee (0 Energy)`"

		emb = addField(emb, player[turn]["name"] + "'s Turn:", text)

		return emb

	embed = getFightEmbed(ctx, False)
	MSG = await ctx.send(embed=embed)
    
	if (not player["p1"]["bot"]) and (not player["p2"]["bot"]):
		await MSG.add_reaction("🕓")
		await MSG.add_reaction("👊")
		await MSG.add_reaction("🍷")
		await MSG.add_reaction("❌")

	# the main loop
	playing = True
	while playing:
		# waits for the reaction to be added
		try:
			if player[turn]["bot"]:
				reaction = "🍷"
				if player[turn]["heals"] == 0 or player[turn]["health"] >= 50 or (player[turn]["health"] >= 25 and randint(1, 4) == 1) or randint(1, 4) > 1:
					if player[turn]["energy"] > 0 and (randint(1, 8) + player[turn]["energy"]) > 8:
						reaction = "👊"
					else:
						reaction = "🕓"

				user = get(ctx.guild.members, id=player[turn]["id"])
				await asyncio.sleep(3.5)
			else:
				reaction, user = await client.wait_for("reaction_add", timeout=60, check=check)

			if reaction:
				if type(reaction) != str:
					reaction = str(reaction.emoji)
                
				# flee (aka quit the game)
				if reaction == "❌":
					await MSG.delete()
					await ctx.send(player[turn]["name"] + " fled!\nGG " + player[turnt]["name"] + "!!!")
					return

				# punch
				# more energy makes the attack stronger but attacking will half your energy
				if reaction == "👊":
					num = randint((player[turn]["energy"]*5)-player[turn]["energy"], (player[turn]["energy"]*5)+player[turn]["energy"])
					enum = math.ceil(player[turn]["energy"] / 2)
					action = "{name1} hit {name2}!".format(name1=player[turn]["name"] , name2=player[turnt]["name"]), "{name2} lost **{num} health**!\n{name1} lost **{enum} energy**!".format(name1=player[turn]["name"], name2=player[turnt]["name"], num=num, enum=enum)

					player[turn]["energy"] -= enum
					player[turnt]["health"] -= num
					player[turnt]["health"] = clamp(player[turnt]["health"], 0, maxhealth)

				# heal
				if reaction == "🍷":
					player[turn]["heals"] -= 1
					num = 50

					if player[turn]["heals"] == 0:
						action = "{name} drank a health potion! That was their last...".format(name=player[turn]["name"]), "{name} gained **{num} health**!".format(name=player[turn]["name"], num=num)
					else:
						action = "{name} drank a health potion!".format(name=player[turn]["name"]), "{name} gained **{num} health**!".format(name=player[turn]["name"], num=num)

					player[turn]["health"] += num
					player[turn]["health"] = clamp(player[turn]["health"], 0, maxhealth)

				# wait
				if reaction == "🕓":
					action = "{name} decided to wait.!".format(name=player[turn]["name"]), "{name} gained **1 energy**!".format(name=player[turn]["name"])

					player[turn]["energy"] += 1
					player[turn]["energy"] = clamp(player[turn]["energy"], 0, maxenergy)

				# if it's a bot don't remove reaction
				if not player[turn]["bot"]:
					await MSG.remove_reaction(reaction, user)

				# if enemy health at 0, you win!
				if player[turnt]["health"] == 0:
					win = turn
					playing = False

				# swap turn
				oldturn = turn
				turn = turnt
				turnt = oldturn

				# gain energy
				player[turn]["energy"] += 1
				player[turn]["energy"] = clamp(player[turn]["energy"], 0, maxenergy)

				# update embed
				embed = getFightEmbed(ctx, action)
				await MSG.edit(embed=embed)

		# if no reaction is added in a miniue, it's a draw
		except asyncio.TimeoutError:
			win = "timeout"
			playing = False
			break

	# victory message
	await MSG.delete()
	if win == "timeout":
		await ctx.send("Timeout.")
	else:
		await ctx.send("GG " + player[win]["name"] + "!!!")

def setup(client):
  client.add_cog(FightCog(client))