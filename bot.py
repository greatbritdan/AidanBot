from aidanbot import AidanBot
from github import Github
import json

github = Github(os.getenv("GITHUB_TOKEN"))
githubrepo = github.get_repo("Aid0nModder/AidanBot")
token = os.getenv("DISCORD_TOKEN")

def getCONnames():
	names = []
	with open('./data/values.json') as file:
		list = json.load(file)
		for val in list:
			if "restricted" not in list[val]:
				names.append(val)
	return names
	
def getUCONnames():
	names = []
	with open('./data/uservalues.json') as file:
		list = json.load(file)
		for val in list:
			if "restricted" not in list[val]:
				names.append(val)
	return names

def getGithubtags():
	return [tag.name for tag in githubrepo.get_labels()]

def main():
	client = AidanBot(githubrepo, [836936601824788520, 760987756985843733, 939885594786533396, 879063875469860874])
	client.run(token)
	
if __name__ == '__main__':
	main()

'''
Slash Command Hierarchy!
( Think of it as a diet coke help command )

	/info -      Bot info.
	/ping -      Get bots latency.
	/echo -      Make the bot say something.
	/issue -     Create an issue on github.
	/userinfo -  Get info on a user.

	/config
	-	/config guild -       Edit guild configeration. (GUILD ONLY) (REQUIRES KICK MEMBERS)
	-	/config user -        Edit user configeration.
	/role
	-	/role add -           Add a [r] role to yourself or any role to anyone if you have manage roles. (GUILD ONLY)
	-	/role remove -        Remove a role, same restrictions as above. (GUILD ONLY)

	/opinion
	-	/opinion rate -       Rate a thing.
	-	/opinion percent -    Get percent of thing.
	-	/opinion ask -        Ask a thing.
	-	/opinion decide -     Decinde on thing.
	/games
	-	/games rps -           Rock, paper, sissors.
	-	/games fight -         Fight people or bots.
	-	/games fightclassic -  Fight people or bots, but classic.
	
	/birthday
	-	/birthday set -       Set your birthday.
	-	/birthday remove -    Remove your birthday.
	-	/birthday upcoming -  See upcoming birthdays.
	/qotd (MUST HAVE 'qotd_channel' CONFIG SETUP!)
	-	/qotd ask -           Forcefully ask a question. (OWNER ONLY)
	-	/qotd config -        Add, remove and see all questions.

	/owner
	-	/owner change_status -  Change a guilds status

	(message) UwU -  Uwuifys a message. :3
	(message) Raw -  Get the raw text of a message.
	(message) Eval -        Eval dat text. (OWNER ONLY)
	(message) Eval-rerun -  Eval dat text but you can rerun it. (OWNER ONLY)
	(user) Info -    Get info on a user.

'''
