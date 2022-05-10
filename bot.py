import os
from aidanbot import AidanBot

def main():
	client = AidanBot()
	client.run(os.getenv("DISCORD_TOKEN"))

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
	-	/config guild -       Edit guild configeration. (GUILD ONLY)
	-	/config user -        Edit user configeration.

	/role
	-	/role add -           Add a [r] role to yourself or any role to anyone if you have manage roles.
	-	/role remove -        Remove a role, same restrictions as above.

	/opinion
	-	/opinion rate -       Rate a thing.
	-	/opinion percent -    Get percent of thing.
	-	/opinion ask -        Ask a thing.
	-	/opinion decide -     Decinde on thing.

	/games
	-	/games fight -        Fight people or bots.
	-	/games rps -          Rock, paper, sissors.

	/birthday
	-	/birthday set -       Set your birthday.
	-	/birthday remove -    Remove your birthday.
	-	/birthday upcoming -  See upcoming birthdays.

	/qotd (MUST HAVE 'qotd_channel' CONFIG SETUP!)
	-	/qotd list -          Forcefully ask a question. (OWNER ONLY)
	-	/qotd config -        Add, remove and see all questions.

	/owner
	-	/owner eval -         [DONE] run sum code (OWNER ONLY)

	(message) UwU - Uwuifys a message. :3
	(message) Raw - Get the raw text of a message.
	(user) Info - Get info on a user.

'''
