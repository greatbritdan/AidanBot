import os
from aidanbot import AidanBot

def main():
	client = AidanBot("$")
	client.run(os.getenv("DISCORD_TOKEN"))

if __name__ == '__main__':
    main()
