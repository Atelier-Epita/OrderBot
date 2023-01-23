import os
from dotenv import load_dotenv

from .src import discord_bot
from .src import github_bot

load_dotenv()

discord_token = os.getenv("DISCORD_TOKEN")
github_token = os.getenv("GITHUB_TOKEN")
github_owner = os.getenv("GITHUB_OWNER")
github_repo = os.getenv("GITHUB_REPO")
github_project_id = os.getenv("GITHUB_PROJECT_ID")

if not all([discord_token, github_token, github_owner, github_repo, github_project_id]):
    raise Exception("Missing environment variables")

discord_bot = discord_bot.DiscordBot(discord_token)
github_bot = github_bot.GithubBot(github_owner, github_repo, github_project_id, github_token)

discord_bot.run()