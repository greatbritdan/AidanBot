import discord, json, os

from aidanbot import AidanBot
from github import Github

from typing import Literal
from dotenv import load_dotenv

#load_dotenv()
token = os.getenv("DISCORD_TOKEN")
github = Github(os.getenv("GITHUB_TOKEN"))
githubrepo = github.get_repo("Aid0nModder/AidanBot")

debug_guilds = False #[discord.Object(760987756985843733), discord.Object(836936601824788520), discord.Object(879063875469860874), discord.Object(1041821214777278464)]

def main():
	client = AidanBot(debug_guilds, githubrepo)
	client.run(token)
	
if __name__ == '__main__':
	main()

'''
Slash Command Hierarchy!
( Think of it as a diet coke help command )

	/info -      Bot info.
	/ping -      Get bots latency.
	/echo -      Make the bot say something.
	/clone -     Say something as another user.
	/issue -     Create an issue on github.
	/role -      Add/Remove a [r] role to/from yourself or any role to/from anyone if you have manage roles. (GUILD ONLY)

	/userinfo -  Get info on a user.
	/guildinfo - Get info on the guild.

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
	
	/birthday
	-	/birthday change -    Set your birthday.
	-	/birthday upcoming -  See upcoming birthdays.

	/qotd (MUST HAVE 'qotd_channel' CONFIG SETUP!)
	-	/qotd list -    List all questions.
	-	/qotd ask -     Ask a question.
	-	/qotd remove -  Remove a question.
	-	/qotd edit -    Edit a question.
	-	/qotd reroll -  Resend a questionm if the old one wasn't good.

	/suggestbot
	-	/suggestbot info     -  Info about suggestionbot.
	-	/suggestbot generate -  Generates random suggestions.

	(message) UwU -         /rpsifys a message. :3
	(message) Eval -        Eval dat text. (OWNER ONLY)
	(message) Eval-rerun -  Eval dat text but you can rerun it. (OWNER ONLY)
	
	(user) Info -           Get info on a user.

'''

def getnames(path):
	names = []
	with open(f'./data/{path}.json') as file:
		list = json.load(file)
		for val in list:
			if "restricted" not in list[val]:
				names.append(val)
	return Literal[tuple(names)]
def getCONnames():
	return getnames("values")
def getUCONnames():
	return getnames("uservalues")
def getGithubtags():
	return Literal[tuple([tag.name for tag in githubrepo.get_labels()])]
