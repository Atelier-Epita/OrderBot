import logging
import os
import sys

from dotenv import load_dotenv

from .src import discord_bot, github_bot

# write to file with time and level
logging.basicConfig(
    handlers=[
        logging.FileHandler("orderbot.log", mode="w"),
        logging.StreamHandler(sys.stdout)
    ],
    format='[%(asctime)s][%(levelname)s][%(message)s]',
    datefmt='%d-%b-%y %H:%M:%S',
    level=logging.DEBUG
)


load_dotenv()

discord_token = os.getenv("DISCORD_TOKEN")
github_token = os.getenv("GITHUB_TOKEN")
github_org = os.getenv("GITHUB_ORG")
github_repo = os.getenv("GITHUB_REPO")
github_project_number = os.getenv("GITHUB_PROJECT_NUMBER")

if not all([discord_token, github_token, github_org, github_repo, github_project_number]):
    raise Exception("Missing environment variables")

github_bot = github_bot.GithubBot(github_org, github_repo, github_token)
discord_bot = discord_bot.DiscordBot(discord_token, github_bot)

discord_bot.run()
