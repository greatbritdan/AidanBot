from aidanbot import AidanBot
from github import Github
import os, json, discord
from typing import Literal

### DON'T LEAK! ###
github = Github(os.getenv("GITHUB_TOKEN"))
githubrepo = github.get_repo("Aid0nModder/AidanBot")
token = os.getenv("DISCORD_TOKEN")
### DON'T LEAK! ###

debug_guilds = False #[discord.Object(760987756985843733), discord.Object(836936601824788520)]

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

def main():
	client = AidanBot(githubrepo, debug_guilds)
	client.run(token)
	
if __name__ == '__main__':
	main()

'''
Slash Command Hierarchy!
( Think of it as a diet coke help command )

	/info -      Bot info.
	/ping -      Get bots latency.
	/echo -      Make the bot say something.
	/embed -     Create a custom embed.
	/clone -     Say something as another user.
	/issue -     Create an issue on github.
	/role -      Add/Remove a [r] role to/from yourself or any role to/from anyone if you have manage roles. (GUILD ONLY)
	/userinfo -  Get info on a user.

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
	/games
	-	/games rps -           Rock, paper, sissors.
	-	/games fight -         Fight people or bots.
	-	/games fightclassic -  Fight people or bots, but classic.
	
	/birthday
	-	/birthday change -    Set your birthday.
	-	/birthday upcoming -  See upcoming birthdays.

	/qotd (MUST HAVE 'qotd_channel' CONFIG SETUP!)
	-	/qotd post -    Forcefully ask a question. (OWNER ONLY)
	-	/qotd list -    List all questions.
	-	/qotd ask -     Ask a question.
	-	/qotd remove -  Remove a question.

	(message) UwU -         Uwuifys a message. :3
	(message) Eval -        Eval dat text. (OWNER ONLY)
	(message) Eval-rerun -  Eval dat text but you can rerun it. (OWNER ONLY)
	(user) Info -           Get info on a user.

'''
