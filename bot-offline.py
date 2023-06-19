import discord, os
from aidanbot import AidanBot
from dotenv import load_dotenv

load_dotenv()
token = os.getenv("DISCORD_TOKEN")

debug_guilds = [discord.Object(760987756985843733), discord.Object(836936601824788520), discord.Object(879063875469860874), discord.Object(1041821214777278464)]

def main():
	client = AidanBot(debug_guilds, offline=True)
	client.run(token)
	
if __name__ == '__main__':
	main()