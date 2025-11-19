import discord, os
from dotenv import load_dotenv

from aidanbot import AidanBot

load_dotenv()
token = os.getenv("DISCORD_TOKEN")

debug_guilds = [] # [discord.Object(760987756985843733)] #, discord.Object(836936601824788520), discord.Object(879063875469860874), discord.Object(1041821214777278464)]

def main():
	client = AidanBot(debug_guilds)
	client.run(token)
	
if __name__ == '__main__':
	main()
	
'''
Slash Command Hierarchy!
( Think of it as a diet coke help command )

	/botinfo -  Bot info.
	/ping -     Get bots latency.
	/echo -     Make the bot say something.
	/clone -    Say something as another user.

	/info
	-	/info user -   Get info on a user.
	-	/info guild -  Get info on the guild.

	/config
	-	/config guild -  Edit guild configeration. (GUILD ONLY) (REQUIRES KICK MEMBERS)
	-	/config user -   Edit user configeration.

	/opinion
	-	/opinion rate -      Rate a thing.
	-	/opinion percent -   Get percent of thing.
	-	/opinion ask -       Ask a thing.
	-	/opinion decide -    Decinde on thing.
	-	/opinion tierlist -  AidanBot will make a very cool tier list.
	-	/opinion poll -      Create a poll.
	-	/opinion 8ball -     AidanBot will shake a magic 8 ball on yur behalf.
	
	/games
	-	/games rps -           Rock, paper, sissors.
	-	/games fight -         Fight people or bots.
	-	/games fightclassic -  Fight people or bots, but classic.

	/qotd (MUST HAVE 'qotd_channel' CONFIG SETUP!)
	-	/qotd view -    View questions.
	-	/qotd ask -     Ask a new question.
	-	/qotd remove -  Remove a question, can only remove your own unless you're a mod.
	-	/qotd test -    Test a question, can only use if you're a mod.

	/suggestbot
	-	/suggestbot info     -  Info about suggestionbot.
	-	/suggestbot generate -  Generates random suggestions.

	(message) Eval -        Eval dat text. (OWNER ONLY)
	(message) Eval-rerun -  Eval dat text but you can rerun it. (OWNER ONLY)


'''
